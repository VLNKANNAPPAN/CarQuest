"""
db.py  –  All database interaction, now backed by local SQLite.
"""

import os
import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "carquest.db")


def get_db_connection():
    """Return a sqlite3 connection with row_factory set to dict-like rows."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # lets us do row['column']
    return conn


def _rows_to_dicts(rows):
    return [dict(r) for r in rows]


# ── detailed vehicle info ────────────────────────────────────────────────────

def get_vehicle_details(vehicle_id):
    query = """
    SELECT v.vehicle_id,
           v.brand, v.model, v.variant, v.type, v.price AS base_price,
           e.fuel, e.displacement, e.no_of_cylinders, e.bhp_value, e.bhp_rpm,
           e.torque_value, e.torque_rpm,
           t.transmission, t.gearbox, t.drive_type,
           pf.mileage, pf.capacity,
           d.boot_space, d.seating_capacity, d.wheel_base,
           c.front_brake, c.rear_brake, c.tyre_size, c.tyre_type,
           f.cruise_control, f.parking_sensors, f.keyLess_entry,
           f.engine_start_stop_button, f.LED_headlamps,
           f.no_of_airbags, f.rear_camera, f.hill_assist,
           p.city, p.price AS city_price
    FROM Vehicle v
    LEFT JOIN Engine e       ON v.vehicle_id = e.vehicle_id
    LEFT JOIN Transmission t ON v.vehicle_id = t.vehicle_id
    LEFT JOIN Performance pf ON v.vehicle_id = pf.vehicle_id
    LEFT JOIN Dimensions d   ON v.vehicle_id = d.vehicle_id
    LEFT JOIN Chassis c      ON v.vehicle_id = c.vehicle_id
    LEFT JOIN Features f     ON v.vehicle_id = f.vehicle_id
    LEFT JOIN Price p        ON v.vehicle_id = p.vehicle_id
    WHERE v.vehicle_id = ?
    """
    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute(query, (vehicle_id,))
        rows = _rows_to_dicts(cur.fetchall())
        conn.close()

        if not rows:
            return None

        df = pd.DataFrame(rows)
        city_prices  = df[["city", "city_price"]].drop_duplicates()
        vehicle_info = (df.drop(columns=["city", "city_price"])
                          .drop_duplicates(subset=["vehicle_id"]))

        return {
            "vehicle_info": vehicle_info.reset_index(drop=True),
            "city_prices":  city_prices.reset_index(drop=True),
        }
    except Exception as e:
        st.error(f"Error fetching details for vehicle {vehicle_id}: {e}")
        return None


# ── similar cars ─────────────────────────────────────────────────────────────

def get_similar_cars(brand, vehicle_id, limit=3):
    query = """
    SELECT vehicle_id, brand, model, variant, type, image_link
    FROM Vehicle
    WHERE brand = ?
      AND vehicle_id <> ?
    LIMIT ?
    """
    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute(query, (brand, vehicle_id, int(limit)))
        results = _rows_to_dicts(cur.fetchall())
        conn.close()
        return results
    except Exception as e:
        st.error(f"Error fetching similar cars: {e}")
        return []
