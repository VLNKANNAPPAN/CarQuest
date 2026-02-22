import codecs

with codecs.open('c:/Users/computer/Desktop/KPP/AIML/CarQuest/app.py', 'r', 'utf-8') as f:
    code = f.read()

# Replace imports
old_imports = """import streamlit as st
import mysql.connector
import tempfile
import pandas as pd
from PIL import Image
import google.generativeai as genai
import base64
import os
import dotenv
dotenv.load_dotenv()"""

new_imports = """import streamlit as st
import pandas as pd
from PIL import Image
import base64
import os

import db
import ai
import filters"""

code = code.replace(old_imports, new_imports)

# Remove the big block from SSL to get_similar_cars
start_str = "# --- SSL CERTIFICATE SETUP ---"
end_str = "# --- PAGE: HOME ---"

start_idx = code.find(start_str)
end_idx = code.find(end_str)

if start_idx != -1 and end_idx != -1:
    big_block_replacement = """
def bool_to_label(val):
    \"\"\"Converts 1/0 (or True/False) to a user-friendly 'True'/'False'.\"\"\"
    if val in [1, True]:
        return "True"
    elif val in [0, False]:
        return "False"
    return str(val)  # Fallback for other data types

# --- EXPORT FUNCTION ---
def export_to_csv(data):
    csv = data.to_csv(index=False).encode('utf-8')
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="car_results.csv">Download CSV File</a>'
    st.markdown(href, unsafe_allow_html=True)

"""
    code = code[:start_idx] + big_block_replacement + code[end_idx:]

# Replace QuestAI execution
old_questai = """                mysql_query = convert_to_sql(user_input)
                st.code(mysql_query, language='sql')
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute(mysql_query)
                    results = cursor.fetchall()
                    cursor.close()
                    conn.close()"""

new_questai = """                try:
                    mysql_query = ai.convert_to_sql(user_input)
                    st.code(mysql_query, language='sql')
                    conn = db.get_db_connection()
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute(mysql_query)
                    results = cursor.fetchall()
                    cursor.close()
                    conn.close()"""
code = code.replace(old_questai, new_questai)

# Replace filter logic
old_filters_start = """    # Build filter conditions
    filters = []"""
old_filters_end = """    st.code(final_query, language='sql')"""

start_f_idx = code.find(old_filters_start)
end_f_idx = code.find(old_filters_end) + len(old_filters_end)

if start_f_idx != -1 and end_f_idx != -1 + len(old_filters_end):
    new_filters = """    # Build filter conditions
    final_query, query_params = filters.build_filter_query(
        city, brand, car_type, variant, price_range, fuel, 
        displacement_range, bhp_range, torque_range, mileage_range, 
        seating_capacity, transmission_type, sort_by
    )

    st.code(final_query, language='sql')"""

    code = code[:start_f_idx] + new_filters + code[end_f_idx:]

# Replace filter execution
old_filters_exec = """        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(final_query)
        results = cursor.fetchall()"""

new_filters_exec = """        conn = db.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(final_query, query_params)
        results = cursor.fetchall()"""

code = code.replace(old_filters_exec, new_filters_exec)

# Replace remaining variable / function names
code = code.replace("get_vehicle_details(", "db.get_vehicle_details(")
code = code.replace("get_similar_cars(", "db.get_similar_cars(")
code = code.replace("get_db_connection()", "db.get_db_connection()")

with codecs.open('c:/Users/computer/Desktop/KPP/AIML/CarQuest/app.py', 'w', 'utf-8') as f:
    f.write(code)

print("done")
