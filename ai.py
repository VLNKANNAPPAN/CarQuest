import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("PPI"))
model = genai.GenerativeModel("gemini-2.5-flash")

def convert_to_sql(user_query):
    prompt = f'''
You are an expert SQL generator specializing in vehicle databases. Translate the following natural language query into MySQL queries using the provided schema.

Database: defaultdb

Schema definitions
# Vehicle table (basic info)
CREATE TABLE IF NOT EXISTS Vehicle (
  vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
  brand VARCHAR(50) NOT NULL,
  model VARCHAR(50) NOT NULL,
  variant VARCHAR(255),
  type VARCHAR(50),
  price DECIMAL(20,2),
  url VARCHAR(255),
  image_link VARCHAR(255)
);

# Engine table (engine details)
CREATE TABLE IF NOT EXISTS Engine (
  engine_id INT AUTO_INCREMENT PRIMARY KEY,
  vehicle_id INT NOT NULL,
  fuel VARCHAR(20),
  displacement INT,
  no_of_cylinders FLOAT,
  bhp_value INT,
  bhp_rpm FLOAT,
  torque_value FLOAT,
  torque_rpm FLOAT,
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

# Transmission table (transmission details)
CREATE TABLE IF NOT EXISTS Transmission (
  transmission_id INT AUTO_INCREMENT PRIMARY KEY,
  vehicle_id INT NOT NULL,
  transmission VARCHAR(50),
  gearbox INT,
  drive_type VARCHAR(50),
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

# Performance table (mileage and capacity)
CREATE TABLE IF NOT EXISTS Performance (
  performance_id INT AUTO_INCREMENT PRIMARY KEY,
  vehicle_id INT NOT NULL,
  mileage FLOAT,
  capacity FLOAT,
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

# Dimensions table (boot space, seating capacity, wheel base)
CREATE TABLE IF NOT EXISTS Dimensions (
  dimension_id INT AUTO_INCREMENT PRIMARY KEY,
  vehicle_id INT NOT NULL,
  boot_space FLOAT,
  seating_capacity INT,
  wheel_base FLOAT,
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

# Chassis table (brakes and tyre details)
CREATE TABLE IF NOT EXISTS Chassis (
  chassis_id INT AUTO_INCREMENT PRIMARY KEY,
  vehicle_id INT NOT NULL,
  front_brake VARCHAR(50),
  rear_brake VARCHAR(50),
  tyre_size VARCHAR(50),
  tyre_type VARCHAR(50),
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

# Features table (additional features as booleans and extras)
CREATE TABLE IF NOT EXISTS Features (
  feature_id INT AUTO_INCREMENT PRIMARY KEY,
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
  price_id INT AUTO_INCREMENT PRIMARY KEY,
  vehicle_id INT NOT NULL,
  city VARCHAR(50) NOT NULL,
  price DECIMAL(20,2),
  FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

Now convert the following query to SQL:
"{user_query}"
'''
    response = model.generate_content(prompt)
    sql_output = response.text
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
