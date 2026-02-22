import ai

test_queries = [
    "A sedan under 17 lakhs",
    "A diesel SUV",
    "A petrol hatchback in Chennai",
    "BMW automatic cars",
    "sedan above 9 million"
]

for query in test_queries:
    print(f"Query: {query}")
    try:
        sql = ai.convert_to_sql(query)
        print(f"SQL: {sql}\n")
    except Exception as e:
        print(f"Error: {e}\n")
