import streamlit as st
import tempfile
import pandas as pd
from PIL import Image
import base64
import os
from dotenv import load_dotenv
load_dotenv()

import db
import ai
import filters
# --- CONFIG ---
st.set_page_config(page_title="Car-Quest ✨", layout="wide")

# --- STYLE ---
st.markdown("""
<style>
    .main { padding: 20px; }
    .title-style { font-size: 3em; text-align: center; margin-bottom: 1em; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
page = st.sidebar.radio("Navigation", ["Home", "QuestAI", "Filters", "Compare"])


def bool_to_label(val):
    """Converts 1/0 (or True/False) to a user-friendly 'True'/'False'."""
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

# --- PAGE: HOME ---
if page == "Home":
    # Hero Section
    st.markdown("""
        <style>
        .hero {
            padding: 3rem 1rem;
            border-radius: 1rem;
            text-align: center;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            margin-bottom: 2rem;
        }
        .hero h1 {
            font-size: 3.5rem;
            color: #1a1a1a;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }
        .hero p {
            font-size: 1.25rem;
            color: #4a5568;
            max-width: 600px;
            margin: 0 auto;
        }
        .section-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #2d3748;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        </style>
        <div class="hero">
            <h1>CarQuest</h1>
            <p>Your intelligent platform to explore, compare, and discover the perfect vehicle.</p>
        </div>
    """, unsafe_allow_html=True)

    # Key Statistics / Quick Facts
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.metric(label="Vehicles Listed", value="250+")
    with col_stat2:
        st.metric(label="Brands", value="15+")
    with col_stat3:
        st.metric(label="Cities Covered", value="10")
    with col_stat4:
        st.metric(label="AI Integration", value="Active")

    st.markdown("<div class='section-title'>Featured Categories</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    with c1:
        with st.container(border=True):
            st.image("https://media.istockphoto.com/id/1167555914/photo/modern-red-suv-car-in-garage-with-lights-turned-on.jpg?s=612x612&w=0&k=20&c=DRKL152y8f0nxgcF-jfLAwM69YtcsYt86XHDEnCssI0=", use_container_width=True)
            st.markdown("#### Premium SUVs")
            st.caption("Command the road with spacious interiors and powerful performance.")
            
    with c2:
        with st.container(border=True):
            st.image("https://media.istockphoto.com/id/1264045166/photo/car-driving-on-a-road.jpg?s=612x612&w=0&k=20&c=vRYLFjs6XMBZv0rl6Pbk77AlZvFe9RC6gSZuqUe_jXs=", use_container_width=True)
            st.markdown("#### Executive Sedans")
            st.caption("Experience unmatched comfort and driving dynamics for the city.")

    with c3:
        with st.container(border=True):
            st.image("https://media.istockphoto.com/id/1486018004/photo/a-happy-handsome-adult-male-charging-his-expensive-electric-car-before-leaving-his-house-for.jpg?s=612x612&w=0&k=20&c=rY6SHolsHcNtS_y23F0DgAe0arV6KZ_c3-k9r7PNP9Q=", use_container_width=True)
            st.markdown("#### Electric Vehicles")
            st.caption("Embrace the future with zero emissions and instant torque.")

    st.markdown("---")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("<div class='section-title'>Top Picks This Month</div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("**Hyundai Creta 2024**<br><span style='color:gray; font-size:0.9em;'>Best Overall SUV</span>", unsafe_allow_html=True)
            st.divider()
            st.markdown("**Tata Nexon EV**<br><span style='color:gray; font-size:0.9em;'>Top Electric Compact</span>", unsafe_allow_html=True)
            st.divider()
            st.markdown("**Honda City Hybrid**<br><span style='color:gray; font-size:0.9em;'>Premium Sedan Choice</span>", unsafe_allow_html=True)
            st.divider()
            st.markdown("**Maruti Fronx**<br><span style='color:gray; font-size:0.9em;'>Value for Money Crossover</span>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='section-title'>Latest Industry Insights</div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("[Evaluating Cars Under ₹10 Lakhs](https://www.autocarindia.com/)")
            st.caption("A comprehensive review of budget-friendly performance.")
            st.divider()
            st.markdown("[The Rise of High-Mileage EVs](https://www.carwale.com/)")
            st.caption("Analyzing battery technology and real-world ranges.")
            st.divider()
            st.markdown("[Reliability Metrics in India](https://www.team-bhp.com/)")
            st.caption("Long-term ownership reports and maintenance costs.")
            st.divider()
            st.markdown("[2025 Market Launch Previews](https://www.zigwheels.com/)")
            st.caption("What to expect from major manufacturers next year.")

    st.markdown("---")

    st.markdown("<div class='section-title'>Platform Capabilities</div>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        st.info("**Advanced Filtering**\n\nFilter vehicles by over 15 parameters including Engine, Transmission, and Features.")
    with f2:
        st.info("**Side-by-Side Comparison**\n\nDirectly compare variants across different brands to find your perfect match.")
    with f3:
        st.warning("**QuestAI** \n\nLeverage our Gemini-powered AI to convert natural language queries into instant vehicle insights.")

# --- PAGE: ASK IN ENGLISH ---
elif page == "QuestAI":
    st.subheader("QuestAI 💕")
    user_input = st.text_input("Ask me to find a car:")
    if st.button("Search"):
        if user_input:
            with st.spinner("Processing your request..."):
                mysql_query = ai.convert_to_sql(user_input)
                with st.expander("🔍 View SQL Query"):
                    st.code(mysql_query, language='sql')
                try:
                    conn = db.get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(mysql_query)
                    rows = cursor.fetchall()
                    cursor.close()
                    conn.close()
                    results = [dict(r) for r in rows]
                    if results:
                        st.success("Results:")
                        df = pd.DataFrame(results)
                        st.dataframe(df)
                        export_to_csv(df)
                    else:
                        st.warning("No results found for your query.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a query.")

# --- PAGE: CUSTOM FILTERS ---
elif page == "Filters":
    st.subheader("Filter Your Search")
    # Basic Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        city = st.selectbox(
            "Select City",
            options=["Ahmedabad", "Bangalore", "Chandigarh", "Chennai", "Hyderabad",
                     "Jaipur", "Lucknow", "Mumbai", "Patna", "Pune"]
        )
    with col2:
        brands = db.get_all_brands()
        selected_brands = st.multiselect("Select Brand", options=brands)
    with col3:
        # Fetching car types dynamically as well
        try:
            conn = db.get_db_connection()
            rows = conn.execute("SELECT DISTINCT type FROM Vehicle ORDER BY type ASC").fetchall()
            car_types = [r['type'] for r in rows]
            conn.close()
        except:
            car_types = ["Sedan Cars", "Hatchback Cars", "SUV Cars", "MPV Cars"]
            
        selected_types = st.multiselect("Select Car Type", options=car_types)

    variant = st.text_input("Variant (Optional)")
    price_range = st.slider("Price Range (in Lakhs)", 0, 150, (5, 50))

    # Advanced Filters (Expandable)
    with st.expander("Advanced Filters"):
        fuel = st.multiselect("Fuel Type", options=["Petrol", "Diesel", "CNG", "Electric"])
        displacement_range = st.slider("Engine Displacement (cc)", 800, 5000, (800, 5000))
        bhp_range = st.slider("BHP Value", 50, 500, (50, 500))
        torque_range = st.slider("Torque Value (Nm)", 50, 5000, (50, 5000))
        mileage_range = st.slider("Mileage (kmpl)", 5, 40, (5, 40))
        seating_capacity = st.multiselect("Seating Capacity", options=[2, 4, 5, 7])
        transmission_type = st.multiselect("Transmission", options=["Manual", "Automatic"])
        sort_by = st.radio("Sort Results By", options=["Price", "BHP", "Mileage"], index=0)

    # Build parameterized query via filters module
    final_query, query_params = filters.build_filter_query(
        city=city, brand=selected_brands, car_type=selected_types, variant=variant,
        price_range=price_range, fuel=fuel,
        displacement_range=displacement_range, bhp_range=bhp_range,
        torque_range=torque_range, mileage_range=mileage_range,
        seating_capacity=seating_capacity,
        transmission_type=transmission_type,
        sort_by=sort_by
    )

    with st.expander("🔍 View SQL Query"):
        st.code(final_query, language='sql')

    # Execute and display results
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(final_query, query_params)
        rows = cursor.fetchall()
        results = [dict(r) for r in rows]
        cursor.close()
        conn.close()

        if results:
            df_results = pd.DataFrame(results)
            st.success("Matching Cars:")
            st.dataframe(df_results)
            export_to_csv(df_results)
            # Display detailed view for each result
            for _, car in df_results.iterrows():
                with st.container():
                    st.markdown(f"### {car['variant']} ({car['type']})")
                    cols = st.columns([1, 2])
                    with cols[0]:
                        if car.get("image_link"):
                            try:
                                st.image(car["image_link"], width=250)
                            except Exception:
                                st.write("🚗 No image available")
                        else:
                            st.write("🚗 No image available")
                    with cols[1]:
                        st.markdown(f"**Price:** ₹{int(car['price']):,}")
                        details_data = db.get_vehicle_details(car["vehicle_id"])

                        if details_data is not None:
                            vehicle_info = details_data["vehicle_info"]
                            city_prices = details_data["city_prices"]

                            # Create tabs
                            tabs = st.tabs([
                                "Overview",
                                "Engine",
                                "Transmission",
                                "Performance",
                                "Dimensions & Chassis",
                                "Features",
                                "City Prices",
                                "Similar Cars"
                            ])

                            # We only need the first row for general details
                            # because we dropped duplicates on vehicle_id
                            row = vehicle_info.iloc[0]

                            # In your "Overview" tab:
                            with tabs[0]:
                                st.markdown("### Overview")
                                overview_dict = {
                                    "Brand": row['brand'],
                                    "Model": row['model'],
                                    "Variant": row['variant'],
                                    "Type": row['type'],
                                    "Base Ex-Showroom Price": f"₹{int(float(row['base_price'])):,}",
                                }
                                overview_df = pd.DataFrame(list(overview_dict.items()), columns=["Specification", "Value"])
                                st.table(overview_df)

                                # EMI example (if you want to keep it)
                                st.write("**Estimated EMI (5-year loan @ 8% APR):**")
                                principal = float(row['base_price'])  # cast decimal.Decimal to float
                                interest_rate_annual = 0.08
                                monthly_interest = interest_rate_annual / 12
                                months = 5 * 12
                                emi = (principal * monthly_interest) / (1 - (1 + monthly_interest) ** (-months))
                                st.write(f"Approx: ₹{int(emi):,} per month")

                            # In your "Engine" tab:
                            with tabs[1]:
                                st.markdown("### Engine")
                                engine_dict = {
                                    "Fuel": row['fuel'],
                                    "Displacement (cc)": row['displacement'],
                                    "No. of Cylinders": row['no_of_cylinders'],
                                    "BHP Value": row['bhp_value'],
                                    "BHP RPM": row['bhp_rpm'],
                                    "Torque Value (Nm)": row['torque_value'],
                                    "Torque RPM": row['torque_rpm']
                                }
                                engine_df = pd.DataFrame(list(engine_dict.items()), columns=["Specification", "Value"])
                                st.table(engine_df)

                            # In your "Transmission" tab:
                            with tabs[2]:
                                st.markdown("### Transmission")
                                transmission_dict = {
                                    "Transmission": row['transmission'],
                                    "Gearbox": row['gearbox'],
                                    "Drive Type": row['drive_type']
                                }
                                trans_df = pd.DataFrame(list(transmission_dict.items()), columns=["Specification", "Value"])
                                st.table(trans_df)

                            # In your "Performance" tab:
                            with tabs[3]:
                                st.markdown("### Performance")
                                perf_dict = {
                                    "Mileage (kmpl)": row['mileage'],
                                    "Fuel Tank Capacity (L)": row['capacity']
                                }
                                perf_df = pd.DataFrame(list(perf_dict.items()), columns=["Specification", "Value"])
                                st.table(perf_df)

                            # In your "Dimensions & Chassis" tab:
                            with tabs[4]:
                                st.markdown("### Dimensions & Chassis")
                                dim_chassis_dict = {
                                    "Boot Space (L)": row['boot_space'],
                                    "Seating Capacity": row['seating_capacity'],
                                    "Wheel Base (mm)": row['wheel_base'],
                                    "Front Brake": row['front_brake'],
                                    "Rear Brake": row['rear_brake'],
                                    "Tyre Size": row['tyre_size'],
                                    "Tyre Type": row['tyre_type']
                                }
                                dim_df = pd.DataFrame(list(dim_chassis_dict.items()), columns=["Specification", "Value"])
                                st.table(dim_df)

                            # In your "Features" tab:
                            with tabs[5]:
                                st.markdown("### Features")
                                features_dict = {
                                    "Cruise Control": bool_to_label(row['cruise_control']),
                                    "Parking Sensors": row['parking_sensors'] if row['parking_sensors'] else "None",
                                    "Keyless Entry": bool_to_label(row['keyLess_entry']),
                                    "Engine Start/Stop": bool_to_label(row['engine_start_stop_button']),
                                    "LED Headlamps": bool_to_label(row['LED_headlamps']),
                                    "No. of Airbags": row['no_of_airbags'] if row['no_of_airbags'] else "N/A",
                                    "Rear Camera": bool_to_label(row['rear_camera']),
                                    "Hill Assist": bool_to_label(row['hill_assist'])
                                }
                                feat_df = pd.DataFrame(list(features_dict.items()), columns=["Feature", "Value"])
                                st.table(feat_df)

                            # In your "City Prices" tab:
                            with tabs[6]:
                                st.markdown("### City Prices")
                                st.dataframe(city_prices)  # Or st.table(city_prices) if you prefer a static table

                            # In your "Similar Cars" tab (tabs[7]):
                            with tabs[7]:
                                st.write("**Similar Cars**")
                                similar = db.get_similar_cars(row['brand'], row['vehicle_id'], limit=3)
                                if similar:
                                    sim_cols = st.columns(len(similar))
                                    for i, sim_car in enumerate(similar):
                                        with sim_cols[i]:
                                            st.image(sim_car["image_link"], width=150)
                                            st.write(f"{sim_car['brand']} {sim_car['model']}")
                                            st.write(sim_car['variant'])
                                else:
                                    st.write("No similar cars found.")
                        else:
                            st.info("Detailed information not available.")
        else:
            st.warning("No results found.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

elif page == "Compare":
    st.title("📊 Compare Two Car Models")

    brand1 = st.text_input("Enter Brand for Car 1")
    model1 = st.text_input("Enter Model for Car 1")
    brand2 = st.text_input("Enter Brand for Car 2")
    model2 = st.text_input("Enter Model for Car 2")

    if brand1 and model1 and brand2 and model2:
        try:
            conn = db.get_db_connection()
            cursor = conn.cursor()

            # Step 1: Fetch variants using fuzzy case-insensitive matching
            fetch_variants_query = """
            SELECT vehicle_id, brand, model, variant
            FROM Vehicle
            WHERE (brand LIKE ? AND model LIKE ?)
               OR (brand LIKE ? AND model LIKE ?)
            """
            b1_fuzzy = f"%{brand1.strip()}%"
            m1_fuzzy = f"%{model1.strip()}%"
            b2_fuzzy = f"%{brand2.strip()}%"
            m2_fuzzy = f"%{model2.strip()}%"
            
            cursor.execute(fetch_variants_query, (b1_fuzzy, m1_fuzzy, b2_fuzzy, m2_fuzzy))
            variant_rows = cursor.fetchall()

            # Cushion user errors in python matching by dropping case and white space
            car1_variants = [v for v in variant_rows if brand1.lower().strip() in v['brand'].lower() and model1.lower().strip() in v['model'].lower()]
            car2_variants = [v for v in variant_rows if brand2.lower().strip() in v['brand'].lower() and model2.lower().strip() in v['model'].lower()]

            st.subheader("✅ Select Variants to Compare")

            variant1 = st.selectbox("Select Variant for Car 1", [v["variant"] for v in car1_variants])
            variant2 = st.selectbox("Select Variant for Car 2", [v["variant"] for v in car2_variants])

            if st.button("🔍 Compare Selected Variants"):
                # Step 2: Fetch full data for selected variants
                compare_query = """
                SELECT
                    v.vehicle_id, v.brand, v.model, v.variant, v.type, v.image_link,
                    e.fuel, e.displacement, e.no_of_cylinders, e.bhp_value, e.bhp_rpm, e.torque_value, e.torque_rpm,
                    t.transmission, t.gearbox, t.drive_type,
                    p1.price AS chennai_price,
                    p2.price AS mumbai_price,
                    perf.mileage, perf.capacity,
                    d.boot_space, d.seating_capacity, d.wheel_base,
                    ch.front_brake, ch.rear_brake, ch.tyre_size, ch.tyre_type,
                    f.cruise_control, f.parking_sensors, f.keyLess_entry, f.engine_start_stop_button,
                    f.LED_headlamps, f.no_of_airbags, f.rear_camera, f.hill_assist
                FROM Vehicle v
                LEFT JOIN Engine e ON v.vehicle_id = e.vehicle_id
                LEFT JOIN Transmission t ON v.vehicle_id = t.vehicle_id
                LEFT JOIN Performance perf ON v.vehicle_id = perf.vehicle_id
                LEFT JOIN Dimensions d ON v.vehicle_id = d.vehicle_id
                LEFT JOIN Chassis ch ON v.vehicle_id = ch.vehicle_id
                LEFT JOIN Features f ON v.vehicle_id = f.vehicle_id
                LEFT JOIN Price p1 ON v.vehicle_id = p1.vehicle_id AND p1.city = 'Chennai'
                LEFT JOIN Price p2 ON v.vehicle_id = p2.vehicle_id AND p2.city = 'Mumbai'
                WHERE v.variant = ? OR v.variant = ?
                """

                cursor.execute(compare_query, (variant1, variant2))
                cars = cursor.fetchall()

                if cars and len(cars) == 2:
                    car1, car2 = cars[0], cars[1]

                    # Create DataFrame for display
                    comparison_data = {
                        "Feature": [
                            "Brand & Model", "Variant", "Fuel", "Transmission", "Drive Type",
                            "Displacement (cc)", "Mileage (km/l)", "Boot Space (L)", "Seating Capacity",
                            "BHP @ RPM", "Torque @ RPM", "Gearbox", "Tyres", "Brakes (Front/Rear)",
                            "Chennai Price (₹)", "Mumbai Price (₹)", "Airbags", "Cruise Control",
                            "Keyless Entry", "Rear Camera", "Hill Assist", "LED Headlamps",
                            "Parking Sensors", "Engine Start/Stop"
                        ],
                        f"{car1['brand']} {car1['model']} ({car1['variant']})": [
                            f"{car1['brand']} {car1['model']}", car1['variant'], car1['fuel'], car1['transmission'],
                            car1['drive_type'], car1['displacement'], car1['mileage'], car1['boot_space'],
                            car1['seating_capacity'], f"{car1['bhp_value']} @ {car1['bhp_rpm']} rpm",
                            f"{car1['torque_value']} @ {car1['torque_rpm']} rpm", car1['gearbox'],
                            f"{car1['tyre_size']} ({car1['tyre_type']})", f"{car1['front_brake']} / {car1['rear_brake']}",
                            f"₹{int(car1['chennai_price'] or 0):,}", f"₹{int(car1['mumbai_price'] or 0):,}",
                            car1['no_of_airbags'], '✅' if car1['cruise_control'] else '❌',
                            '✅' if car1['keyLess_entry'] else '❌', '✅' if car1['rear_camera'] else '❌',
                            '✅' if car1['hill_assist'] else '❌', '✅' if car1['LED_headlamps'] else '❌',
                            '✅' if car1['parking_sensors'] else '❌', '✅' if car1['engine_start_stop_button'] else '❌'
                        ],
                        f"{car2['brand']} {car2['model']} ({car2['variant']})": [
                            f"{car2['brand']} {car2['model']}", car2['variant'], car2['fuel'], car2['transmission'],
                            car2['drive_type'], car2['displacement'], car2['mileage'], car2['boot_space'],
                            car2['seating_capacity'], f"{car2['bhp_value']} @ {car2['bhp_rpm']} rpm",
                            f"{car2['torque_value']} @ {car2['torque_rpm']} rpm", car2['gearbox'],
                            f"{car2['tyre_size']} ({car2['tyre_type']})", f"{car2['front_brake']} / {car2['rear_brake']}",
                            f"₹{int(car2['chennai_price'] or 0):,}", f"₹{int(car2['mumbai_price'] or 0):,}",
                            car2['no_of_airbags'], '✅' if car2['cruise_control'] else '❌',
                            '✅' if car2['keyLess_entry'] else '❌', '✅' if car2['rear_camera'] else '❌',
                            '✅' if car2['hill_assist'] else '❌', '✅' if car2['LED_headlamps'] else '❌',
                            '✅' if car2['parking_sensors'] else '❌', '✅' if car2['engine_start_stop_button'] else '❌'
                        ]
                    }

                    df = pd.DataFrame(comparison_data)
                    st.dataframe(df, use_container_width=True)

                    # Optionally display car images
                    st.subheader("📸 Car Images")
                    cols = st.columns(2)
                    with cols[0]:
                        st.image(car1['image_link'], caption=f"{car1['brand']} {car1['model']} - {car1['variant']}", width=300)
                    with cols[1]:
                        st.image(car2['image_link'], caption=f"{car2['brand']} {car2['model']} - {car2['variant']}", width=300)
                else:
                    st.warning("Comparison data is incomplete or not available.")
                cursor.close()
                conn.close()

        except Exception as e:
            st.error(f"Error: {e}")
