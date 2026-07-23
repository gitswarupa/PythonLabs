# Fake Enterprise API

A simulated enterprise REST API implemented entirely in Python for automation practice.

The API is designed to mimic common REST API behavior without requiring a web server or internet connection. Students interact with Python objects while learning concepts that directly transfer to real-world API automation.

---

# Installation

Clone or download the project.

From the project root execute:

```bash
uv sync
```

Run the demo application:

```bash
uv run python main.py
```

---

# Creating an API Client

Import the API and create a client.

```python
from fake_api import FakeAPI

api = FakeAPI(
    api_key="training-key"
)
```

If the API key is invalid, every request will return:

```
401 Unauthorized
```

---

# Available Resources

The API exposes four different resources.

```python
api.customers

api.applications

api.cases

api.alerts
```

Each resource supports the same CRUD operations.

---

# Response Object

Every request returns a `Response` object.

```python
response = api.customers.get(1)
```

## Available Properties

| Property | Description |
|----------|-------------|
| status_code | Simulated HTTP status code |
| ok | Returns True if request succeeded |
| data | Returned data |
| error | Error message |
| processing_time_ms | Simulated network latency |
| request_id | Unique request identifier |
| timestamp | Request timestamp |

Example

```python
print(response.status_code)

print(response.ok)

print(response.data)

print(response.error)

print(response.processing_time_ms)

print(response.request_id)

print(response.timestamp)
```

To display the entire response as JSON:

```python
print(response.json())
```

---

# GET All Records

Retrieve all records.

```python
response = api.customers.list()
```

---

# GET One Record

Retrieve a single record by ID.

```python
response = api.customers.get(15)
```

---

# Create a Record (POST)

```python
response = api.customers.create(
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "country": "US",
        "credit_score": 760,
        "risk_level": "LOW",
        "status": "ACTIVE",
    }
)
```

Returns

```
201 Created
```

---

# Replace a Record (PUT)

Replace an existing resource.

```python
response = api.customers.update(
    15,
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "country": "Canada",
        "credit_score": 800,
        "risk_level": "LOW",
        "status": "ACTIVE",
    },
)
```

---

# Partial Update (PATCH)

Update only specific fields.

```python
response = api.customers.patch(
    15,
    {
        "credit_score": 820,
        "risk_level": "LOW",
    },
)
```

---

# Delete a Record

```python
response = api.customers.delete(15)
```

---

# Pagination

Retrieve data in pages.

```python
response = api.customers.list(
    page=2,
    page_size=25,
)
```

Returned structure:

```python
response.data

{
    "page": 2,
    "page_size": 25,
    "total_records": 10000,
    "total_pages": 400,
    "has_previous": True,
    "has_next": True,
    "data": [...]
}
```

---

# Searching

Search across all searchable fields.

```python
response = api.customers.list(
    search="john"
)
```

---

# Filtering

## Exact Match

```python
response = api.customers.list(
    country="US"
)
```

---

## Multiple Filters

```python
response = api.customers.list(
    country="US",
    risk_level="HIGH",
)
```

---

## Greater Than

```python
response = api.customers.list(
    credit_score__gt=700
)
```

---

## Greater Than or Equal

```python
response = api.customers.list(
    credit_score__gte=700
)
```

---

## Less Than

```python
response = api.customers.list(
    credit_score__lt=500
)
```

---

## Less Than or Equal

```python
response = api.customers.list(
    credit_score__lte=650
)
```

---

## Contains

```python
response = api.customers.list(
    first_name__contains="jo"
)
```

---

## Starts With

```python
response = api.customers.list(
    email__startswith="john"
)
```

---

## Ends With

```python
response = api.customers.list(
    email__endswith="@example.com"
)
```

---

# Sorting

Ascending order:

```python
response = api.customers.list(
    sort="credit_score"
)
```

Descending order:

```python
response = api.customers.list(
    sort="credit_score",
    order="desc",
)
```

---

# Combining Features

```python
response = api.customers.list(
    page=3,
    page_size=20,
    country="US",
    risk_level="HIGH",
    credit_score__gte=700,
    search="smith",
    sort="credit_score",
    order="desc",
)
```

---

# Authentication

Correct API key:

```python
api = FakeAPI(
    api_key="training-key"
)
```

Incorrect API key:

```python
api = FakeAPI(
    api_key="wrong-key"
)
```

Returns

```
401 Unauthorized
```

---

# Simulated Status Codes

| Status Code | Meaning |
|--------------|---------|
| 200 | Success |
| 201 | Resource Created |
| 401 | Unauthorized |
| 404 | Resource Not Found |
| 500 | Internal Server Error |
| 504 | Gateway Timeout |

---

# Available Operations

Every resource supports the same operations.

## Customers

```python
api.customers.list()

api.customers.get()

api.customers.create()

api.customers.update()

api.customers.patch()

api.customers.delete()
```

---

## Applications

```python
api.applications.list()

api.applications.get()

api.applications.create()

api.applications.update()

api.applications.patch()

api.applications.delete()
```

---

## Cases

```python
api.cases.list()

api.cases.get()

api.cases.create()

api.cases.update()

api.cases.patch()

api.cases.delete()
```

---

## Alerts

```python
api.alerts.list()

api.alerts.get()

api.alerts.create()

api.alerts.update()

api.alerts.patch()

api.alerts.delete()
```

---

# Complete Example

```python
from fake_api import FakeAPI

api = FakeAPI(api_key="training-key")

response = api.customers.list(
    page=1,
    page_size=25,
    country="US",
    risk_level="HIGH",
    credit_score__gte=700,
    sort="credit_score",
    order="desc",
)

if response.ok:

    print(f"Returned {len(response.data['data'])} records")

    for customer in response.data["data"]:

        print(
            customer["customer_id"],
            customer["first_name"],
            customer["last_name"],
            customer["credit_score"],
        )

else:

    print(response.status_code)

    print(response.error)
```

---

# Best Practices

- Always verify `response.ok` before processing the response.
- Handle common errors such as `401`, `404`, and `500`.
- Use pagination when retrieving large datasets.
- Filter data whenever possible instead of downloading all records.
- Use sorting to retrieve records in the desired order.
- Measure and log `processing_time_ms` for performance analysis.
- Inspect `request_id` when troubleshooting requests.

---

# Suggested Practice Exercises

1. Retrieve the first page of customers.
2. Find all customers with a credit score greater than 750.
3. Search for customers whose first name contains "John".
4. Retrieve all HIGH risk customers in the US.
5. Sort customers by credit score in descending order.
6. Create a new customer.
7. Update an existing customer using PUT.
8. Update only the customer's credit score using PATCH.
9. Delete a customer.
10. Export all HIGH risk customers to a CSV file.
11. Measure the average response time of 100 API calls.
12. Implement retry logic for simulated server errors.
13. Retrieve every page of customers and calculate the average credit score.
14. Generate a report showing the number of customers by country.
15. Find the top 20 customers with the highest credit scores.

---

Happy automating!