"""
filters.py  –  Build a parameterized SELECT query for the Filters page.
Uses SQLite-compatible ? placeholders.
"""


def build_filter_query(city, brand, car_type, variant, price_range, fuel,
                       displacement_range, bhp_range, torque_range,
                       mileage_range, seating_capacity, transmission_type,
                       sort_by):
    filters = []
    params  = []

    filters.append("p.city = ?")
    params.append(city)

    filters.append("p.price BETWEEN ? AND ?")
    params.extend([price_range[0] * 100000, price_range[1] * 100000])

    if brand:
        placeholders = ", ".join(["?"] * len(brand))
        filters.append(f"v.brand IN ({placeholders})")
        params.extend(brand)

    if car_type:
        placeholders = ", ".join(["?"] * len(car_type))
        filters.append(f"v.type IN ({placeholders})")
        params.extend(car_type)

    if variant:
        filters.append("v.variant LIKE ?")
        params.append(f"%{variant}%")

    if fuel:
        placeholders = ", ".join(["?"] * len(fuel))
        filters.append(f"e.fuel IN ({placeholders})")
        params.extend(fuel)

    filters.append("e.displacement BETWEEN ? AND ?")
    params.extend([displacement_range[0], displacement_range[1]])

    filters.append("e.bhp_value BETWEEN ? AND ?")
    params.extend([bhp_range[0], bhp_range[1]])

    filters.append("e.torque_value BETWEEN ? AND ?")
    params.extend([torque_range[0], torque_range[1]])

    filters.append("pf.mileage BETWEEN ? AND ?")
    params.extend([mileage_range[0], mileage_range[1]])

    if seating_capacity:
        placeholders = ", ".join(["?"] * len(seating_capacity))
        filters.append(f"d.seating_capacity IN ({placeholders})")
        params.extend(seating_capacity)

    if transmission_type:
        placeholders = ", ".join(["?"] * len(transmission_type))
        filters.append(f"t.transmission IN ({placeholders})")
        params.extend(transmission_type)

    where_clause = " AND ".join(filters)

    sort_clause = {
        "Price":   "p.price ASC",
        "BHP":     "e.bhp_value DESC",
        "Mileage": "pf.mileage DESC",
    }.get(sort_by, "p.price ASC")

    final_query = f"""
      SELECT DISTINCT
          v.vehicle_id, v.brand, v.model, v.variant, v.type,
          p.price, v.image_link, e.bhp_value, pf.mileage
      FROM Vehicle v
      JOIN Price         p  ON v.vehicle_id = p.vehicle_id
      JOIN Engine        e  ON v.vehicle_id = e.vehicle_id
      JOIN Transmission  t  ON v.vehicle_id = t.vehicle_id
      JOIN Performance   pf ON v.vehicle_id = pf.vehicle_id
      JOIN Dimensions    d  ON v.vehicle_id = d.vehicle_id
      JOIN Features      f  ON v.vehicle_id = f.vehicle_id
      WHERE {where_clause}
      ORDER BY {sort_clause}
      LIMIT 10
    """
    return final_query, tuple(params)
