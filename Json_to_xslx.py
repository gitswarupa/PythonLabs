import pandas as pd
data = [
    {
        "id": 1,
        "name": "test1",
        "dob": "1990-01-02",
        "contact": {"email": "test1@example.com", "phone": "123-456-7890"},
        "location": {"city": "franklin", "state": "TN", "zip": "37064"},
    },
    {
        "id": 2,
        "name": "test2",
        "dob": "1990-01-03",
        "contact": {"email": "test2@example.com", "phone": "123-456-7890"},
        "location": {"city": "SPRING HILL", "state": "TN", "zip": "37174"},
    },
]
print(f"Nested JSON: \n{data}")
df = pd.json_normalize(data)
print(f"Normalized DataFrame: \n{df}")
# * Output to excel files-openpyxl to be installed  and officer viewer extension
df.to_excel(
    "df_normalized.xlsx", index=False, sheet_name="Normalized Orders"
)