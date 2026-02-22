"""
setup_db.py  –  Run this ONCE to build carquest.db from data/car_details.csv
Usage:  python setup_db.py
"""

import sqlite3
import pandas as pd
import re
import os
import requests
import concurrent.futures
from tqdm import tqdm
import urllib.parse

CSV_PATH = os.path.join("data", "car_details.csv")
DB_PATH  = os.path.join("data", "carquest.db")

# ── helpers ──────────────────────────────────────────────────────────────────

def parse_num(val):
    """Extract first numeric value from strings like '1197 cc', '80bhp@5700rpm'."""
    if pd.isna(val):
        return None
    m = re.search(r"[\d.]+", str(val))
    return float(m.group()) if m else None

def yn(val):
    """Map Yes/Not Available/True/False → 1/0."""
    if pd.isna(val):
        return 0
    v = str(val).strip().lower()
    if v in ("yes", "true", "1", "with guidedlines"):
        return 1
    return 0

# ── load CSV ─────────────────────────────────────────────────────────────────

print(f"Reading {CSV_PATH} …")
df = pd.read_csv(CSV_PATH, dtype=str)
print(f"  {len(df)} rows loaded")

# ── fetch original car images ────────────────────────────────────────────────
print("Fetching real exterior car images (this might take a minute)...")
unique_models = df.drop_duplicates(subset=["model"])[["model", "url"]]
model_image_map = {}

def fetch_image(row):
    model_name = str(row["model"]).title().strip()
    url = row["url"]
    if pd.isna(url): return model_name, None
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        # Find all exterior images and capture query params e.g. ?tr=w-664
        # We look for "https://stimg.cardekho.com...jpg" followed by optional "?..."
        matches = re.findall(r'(https://stimg\.cardekho\.com/images/carexteriorimages/[A-Za-z0-9/_-]+\.jpg(?:\?[a-zA-Z0-9=&-]+)?)', r.text)
        if matches:
            # Prefer the front-left-side image if available
            front_left = [m for m in matches if 'front-left-side' in m]
            if front_left: return model_name, front_left[0]
            # otherwise just the first one
            return model_name, matches[0]
    except Exception:
        pass
    return model_name, None

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(fetch_image, r) for _, r in unique_models.iterrows()]
    for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
        m_name, img_url = future.result()
        if img_url:
            model_image_map[m_name] = img_url


# ── open / create SQLite ─────────────────────────────────────────────────────

conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()

# Foreign keys (not strictly required for reads, but good practice)
cur.execute("PRAGMA foreign_keys = ON")

# ── DDL ───────────────────────────────────────────────────────────────────────

cur.executescript("""
CREATE TABLE IF NOT EXISTS Vehicle (
  vehicle_id   INTEGER PRIMARY KEY AUTOINCREMENT,
  brand        TEXT NOT NULL,
  model        TEXT NOT NULL,
  variant      TEXT,
  type         TEXT,
  price        REAL,
  url          TEXT,
  image_link   TEXT
);

CREATE TABLE IF NOT EXISTS Engine (
  engine_id        INTEGER PRIMARY KEY AUTOINCREMENT,
  vehicle_id       INTEGER NOT NULL,
  fuel             TEXT,
  displacement     REAL,
  no_of_cylinders  REAL,
  bhp_value        REAL,
  bhp_rpm          REAL,
  torque_value     REAL,
  torque_rpm       REAL,
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

CREATE TABLE IF NOT EXISTS Transmission (
  transmission_id INTEGER PRIMARY KEY AUTOINCREMENT,
  vehicle_id      INTEGER NOT NULL,
  transmission    TEXT,
  gearbox         TEXT,
  drive_type      TEXT,
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

CREATE TABLE IF NOT EXISTS Performance (
  performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
  vehicle_id     INTEGER NOT NULL,
  mileage        REAL,
  capacity       REAL,
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

CREATE TABLE IF NOT EXISTS Dimensions (
  dimension_id     INTEGER PRIMARY KEY AUTOINCREMENT,
  vehicle_id       INTEGER NOT NULL,
  boot_space       REAL,
  seating_capacity INTEGER,
  wheel_base       REAL,
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

CREATE TABLE IF NOT EXISTS Chassis (
  chassis_id  INTEGER PRIMARY KEY AUTOINCREMENT,
  vehicle_id  INTEGER NOT NULL,
  front_brake TEXT,
  rear_brake  TEXT,
  tyre_size   TEXT,
  tyre_type   TEXT,
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

CREATE TABLE IF NOT EXISTS Features (
  feature_id             INTEGER PRIMARY KEY AUTOINCREMENT,
  vehicle_id             INTEGER NOT NULL,
  cruise_control         INTEGER DEFAULT 0,
  parking_sensors        TEXT,
  keyLess_entry          INTEGER DEFAULT 0,
  engine_start_stop_button INTEGER DEFAULT 0,
  LED_headlamps          INTEGER DEFAULT 0,
  no_of_airbags          INTEGER,
  rear_camera            INTEGER DEFAULT 0,
  hill_assist            INTEGER DEFAULT 0,
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

CREATE TABLE IF NOT EXISTS Price (
  price_id   INTEGER PRIMARY KEY AUTOINCREMENT,
  vehicle_id INTEGER NOT NULL,
  city       TEXT NOT NULL,
  price      REAL,
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

CREATE INDEX IF NOT EXISTS idx_vehicle_brand ON Vehicle(brand);
CREATE INDEX IF NOT EXISTS idx_vehicle_type  ON Vehicle(type);
CREATE INDEX IF NOT EXISTS idx_price_city    ON Price(city);
""")

# ── per-city price multipliers (approximate) ─────────────────────────────────
# We'll derive city prices from the base price with simple multipliers
cities = {
    "Ahmedabad":  1.00,
    "Bangalore":  1.02,
    "Chandigarh": 1.01,
    "Chennai":    1.03,
    "Hyderabad":  1.01,
    "Jaipur":     1.00,
    "Lucknow":    1.00,
    "Mumbai":     1.04,
    "Patna":      1.01,
    "Pune":       1.02,
}

# ── insert rows ──────────────────────────────────────────────────────────────

def parse_bhp_rpm(val):
    """Return (bhp, rpm) from strings like '80bhp@5700rpm'."""
    if pd.isna(val):
        return None, None
    m = re.search(r"([\d.]+)\s*bhp\s*[@@]?\s*([\d.]+)?", str(val), re.I)
    if m:
        return float(m.group(1)), float(m.group(2)) if m.group(2) else None
    return parse_num(val), None

def parse_torque_rpm(val):
    """Return (Nm, rpm) from strings like '111.7Nm@4300rpm'."""
    if pd.isna(val):
        return None, None
    m = re.search(r"([\d.]+)\s*[Nn][Mm]\s*[@@]?\s*([\d.]+)?", str(val))
    if m:
        return float(m.group(1)), float(m.group(2)) if m.group(2) else None
    return parse_num(val), None

print("Inserting rows …")

for _, row in df.iterrows():
    brand   = str(row.get("brand", "")).title().strip()
    model   = str(row.get("model", "")).title().strip()
    variant = str(row.get("variant", "")).title().strip()
    vtype   = str(row.get("type", "")).title().strip()
    price   = parse_num(row.get("price"))
    url     = str(row.get("url", ""))

    # Try to grab the high-res cardekho image we fetched; fallback to UI-Avatars
    image_link = model_image_map.get(model)
    if not image_link:
        placeholder_name = urllib.parse.quote(f"{brand} {model}")
        image_link = f"https://ui-avatars.com/api/?name={placeholder_name}&background=random&color=fff&size=512"

    cur.execute(
        "INSERT INTO Vehicle(brand,model,variant,type,price,url,image_link) VALUES(?,?,?,?,?,?,?)",
        (brand, model, variant, vtype, price, url, image_link)
    )
    vid = cur.lastrowid

    # Engine
    bhp, bhp_rpm     = parse_bhp_rpm(row.get("bhp"))
    torq, torq_rpm   = parse_torque_rpm(row.get("torque"))
    cur.execute(
        "INSERT INTO Engine(vehicle_id,fuel,displacement,no_of_cylinders,bhp_value,bhp_rpm,torque_value,torque_rpm) VALUES(?,?,?,?,?,?,?,?)",
        (vid,
         str(row.get("fuel","")).title().strip(),
         parse_num(row.get("displacement")),
         parse_num(row.get("no_of_cylinders")),
         bhp, bhp_rpm, torq, torq_rpm)
    )

    # Transmission
    cur.execute(
        "INSERT INTO Transmission(vehicle_id,transmission,gearbox,drive_type) VALUES(?,?,?,?)",
        (vid,
         str(row.get("transmission","")).strip(),
         str(row.get("gearbox","")).strip(),
         str(row.get("drive_type","")).strip())
    )

    # Performance
    cur.execute(
        "INSERT INTO Performance(vehicle_id,mileage,capacity) VALUES(?,?,?)",
        (vid, parse_num(row.get("mileage")), parse_num(row.get("capacity")))
    )

    # Dimensions
    cur.execute(
        "INSERT INTO Dimensions(vehicle_id,boot_space,seating_capacity,wheel_base) VALUES(?,?,?,?)",
        (vid,
         parse_num(row.get("boot_space")),
         parse_num(row.get("seating_capacity")),
         parse_num(row.get("wheel_base")))
    )

    # Chassis
    cur.execute(
        "INSERT INTO Chassis(vehicle_id,front_brake,rear_brake,tyre_size,tyre_type) VALUES(?,?,?,?,?)",
        (vid,
         str(row.get("front_brake","")).strip(),
         str(row.get("rear_brake","")).strip(),
         str(row.get("tyre_size","")).strip(),
         str(row.get("tyre_type","")).strip())
    )

    # Features
    cur.execute(
        "INSERT INTO Features(vehicle_id,cruise_control,parking_sensors,keyLess_entry,engine_start_stop_button,LED_headlamps,no_of_airbags,rear_camera,hill_assist) VALUES(?,?,?,?,?,?,?,?,?)",
        (vid,
         yn(row.get("cruise_control")),
         str(row.get("parking_sensors","")).strip(),
         yn(row.get("keyLess_entry")),
         yn(row.get("engine_start/stop_button")),
         yn(row.get("LED_headlamps")),
         parse_num(row.get("no_of_airbags")),
         yn(row.get("rear_camera")),
         yn(row.get("hill_assist")))
    )

    # City Prices
    if price:
        for city, mult in cities.items():
            cur.execute(
                "INSERT INTO Price(vehicle_id,city,price) VALUES(?,?,?)",
                (vid, city, round(price * mult, 2))
            )

conn.commit()
conn.close()

count = len(df)
print(f"\n✅  Done!  {count} variants inserted into {DB_PATH}")
print("   City prices generated for 10 cities.")
print("   Run 'streamlit run app.py' to start the app.")
