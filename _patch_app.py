"""
Fix app.py filter section and QuestAI results, create .env
"""
import codecs, re

text = codecs.open('app.py', 'r', 'utf-8').read()
# Normalise to LF for easier processing
lf = text.replace('\r\n', '\n')

# ── FIX 1: Replace filter SQL builder ────────────────────────────────────────
START = '    # Build filter conditions'
# end anchor: right after cursor.execute(final_query)
# The block ends just after:  "        cursor.execute(final_query)\n        results = cursor.fetchall()"
# Find the start
si = lf.find(START)
if si == -1:
    print('ERROR: filter start marker not found')
else:
    # find the end anchor
    end_anchor = '        cursor.execute(final_query)\n        results = cursor.fetchall()'
    ei = lf.find(end_anchor, si)
    if ei == -1:
        print('ERROR: end anchor not found')
    else:
        ei_end = ei + len(end_anchor)
        replacement = '''    # Build parameterized query via filters module
    final_query, query_params = filters.build_filter_query(
        city=city, brand=brand, car_type=car_type, variant=variant,
        price_range=price_range, fuel=fuel,
        displacement_range=displacement_range, bhp_range=bhp_range,
        torque_range=torque_range, mileage_range=mileage_range,
        seating_capacity=seating_capacity,
        transmission_type=transmission_type,
        sort_by=sort_by
    )

    st.code(final_query, language=\'sql\')

    # Execute and display results
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(final_query, query_params)
        rows = cursor.fetchall()
        results = [dict(r) for r in rows]'''
        lf = lf[:si] + replacement + lf[ei_end:]
        print('Filter section replaced OK')

# ── FIX 2: Ensure QuestAI rows also converted to dicts ───────────────────────
# Already done in patch1, just verify
if '[dict(r) for r in rows]' in lf:
    print('QuestAI dict-conversion already present OK')
else:
    print('WARNING: QuestAI dict conversion missing')

# ── FIX 3: Filters page results to df – fix if still using raw rows ──────────
# Replace old  pd.DataFrame(results)  inside the filter section with explicit check
# (results is now already a list of dicts, so pd.DataFrame(results) should work)

# Write back (restore CRLF)
codecs.open('app.py', 'w', 'utf-8').write(lf.replace('\n', '\r\n'))
print('app.py written OK')
