import os
import re
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
load_dotenv()

GROQ_API_KEY = st.secrets["groq_api"]

client = None
if GROQ_API_KEY:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY
    )

GROQ_MODEL = "llama-3.3-70b-versatile"

def convert_to_sql(user_query):
    prompt = f'''
You are an expert SQL generator specializing in vehicle databases. Translate the following natural language query into SQLite queries using the provided schema.

Database: defaultdb

Schema definitions
# Vehicle table (basic info)
CREATE TABLE IF NOT EXISTS Vehicle (
  vehicle_id INTEGER PRIMARY KEY AUTO_INCREMENT,
  brand VARCHAR(50) NOT NULL,
  model VARCHAR(50) NOT NULL,
  variant VARCHAR(255),
  type VARCHAR(50), -- Categorical: "Convertible Cars", "Coupe Cars", "Hatchback Cars", "Minivans", "Mpv Cars", "Pickup Trucks", "Sedan Cars", "Suv Cars"
  price DECIMAL(20,2),
  url VARCHAR(255),
  image_link VARCHAR(255)
);

# Engine table (engine details)
CREATE TABLE IF NOT EXISTS Engine (
  engine_id INTEGER PRIMARY KEY AUTO_INCREMENT,
  vehicle_id INT NOT NULL,
  fuel VARCHAR(20), -- Categorical: "Petrol", "Cng", "Diesel", "Electric(Battery)"
  displacement INT, -- Entry in cc (e.g., 1200)
  no_of_cylinders FLOAT,
  bhp_value INT,
  bhp_rpm FLOAT,
  torque_value FLOAT,
  torque_rpm FLOAT,
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

# Transmission table (transmission details)
CREATE TABLE IF NOT EXISTS Transmission (
  transmission_id INTEGER PRIMARY KEY AUTO_INCREMENT,
  vehicle_id INT NOT NULL,
  transmission VARCHAR(50), -- Categorical: "Manual", "Automatic"
  gearbox INT,
  drive_type VARCHAR(50),
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

# Performance table (mileage and capacity)
CREATE TABLE IF NOT EXISTS Performance (
  performance_id INTEGER PRIMARY KEY AUTO_INCREMENT,
  vehicle_id INT NOT NULL,
  mileage FLOAT,
  capacity FLOAT,
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

# Dimensions table (boot space, seating capacity, wheel base)
CREATE TABLE IF NOT EXISTS Dimensions (
  dimension_id INTEGER PRIMARY KEY AUTO_INCREMENT,
  vehicle_id INT NOT NULL,
  boot_space FLOAT,
  seating_capacity INT,
  wheel_base FLOAT,
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

# Chassis table (brakes and tyre details)
CREATE TABLE IF NOT EXISTS Chassis (
  chassis_id INTEGER PRIMARY KEY AUTO_INCREMENT,
  vehicle_id INT NOT NULL,
  front_brake VARCHAR(50),
  rear_brake VARCHAR(50),
  tyre_size VARCHAR(50),
  tyre_type VARCHAR(50),
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

# Features table (additional features as booleans and extras)
CREATE TABLE IF NOT EXISTS Features (
  feature_id INTEGER PRIMARY KEY AUTO_INCREMENT,
  vehicle_id INT NOT NULL,
  cruise_control BOOLEAN,
  parking_sensors VARCHAR(20),
  keyLess_entry BOOLEAN,
  engine_start_stop_button BOOLEAN,
  LED_headlamps BOOLEAN,
  no_of_airbags INT,
  rear_camera BOOLEAN,
  hill_assist BOOLEAN,
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

# Price table (separate table for per-city prices)
CREATE TABLE IF NOT EXISTS Price (
  price_id INTEGER PRIMARY KEY AUTO_INCREMENT,
  vehicle_id INT NOT NULL,
  city VARCHAR(50) NOT NULL, -- Categorical: Ahmedabad, Bangalore, Chandigarh, Chennai, Hyderabad, Jaipur, Lucknow, Mumbai, Patna, Pune
  price DECIMAL(20,2),
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

IMPORTANT GUIDELINES:
1. When the user asks for "Sedan", "SUV", etc., use the full categorical name (e.g., "Sedan Cars", "Suv Cars").
2. For engine capacity/displacement, if user says "1.2 Litre", search for displacement around 1200.
3. String comparisons for brands and models should be case-insensitive (e.g., using LOWER() or LIKE).
4. Prices in query MUST be converted to exact numerical format (e.g., 17 Lakhs = 1700000, 1 million = 1000000, 9 million = 9000000, 1 Crore = 10000000).
5. Only return the SQL query, no explanations.

Now convert the following query to SQL:
"{user_query}"
'''
    if not client:
        raise ValueError("Groq API key not found. Please set 'groq_api' in .env")

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    
    sql_output = response.choices[0].message.content
    sql_query = sql_output.split('```')[1][4:] if '```sql' in sql_output else sql_output
    sql_query = sql_query.strip()
    
    upper_query = sql_query.upper()
    dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "REPLACE", "GRANT", "REVOKE", "CREATE"]
    for keyword in dangerous_keywords:
        if re.search(r'\b' + keyword + r'\b', upper_query):
            raise ValueError(f"AI generated an unsafe SQL query containing {keyword}. Operation aborted.")
    
    if not upper_query.startswith("SELECT"):
        raise ValueError("AI generated query is not a SELECT statement.")
        
    return sql_query
