"""
In-memory fake database used by the Fake Enterprise API.

All data is generated at startup using a fixed random seed so every
student works with exactly the same dataset.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

SEED = 42

CUSTOMER_COUNT = 10_000
APPLICATION_COUNT = 50_000
CASE_COUNT = 15_000
ALERT_COUNT = 20_000

random.seed(SEED)

# ---------------------------------------------------------------------
# Sample values
# ---------------------------------------------------------------------

FIRST_NAMES = [
    "John",
    "Jane",
    "Alice",
    "Bob",
    "Michael",
    "Sarah",
    "David",
    "Emily",
    "Daniel",
    "Olivia",
    "Robert",
    "Sophia",
    "William",
    "Emma",
    "James",
    "Isabella",
]

LAST_NAMES = [
    "Smith",
    "Johnson",
    "Brown",
    "Taylor",
    "Miller",
    "Wilson",
    "Moore",
    "Clark",
    "Lewis",
    "Walker",
    "Young",
    "Hall",
    "Allen",
    "King",
    "Scott",
]

COUNTRIES = ["US", "Canada", "Mexico", "Costa Rica", "Brazil", "UK"]

RISK_LEVELS = ["LOW", "MEDIUM", "HIGH"]

CUSTOMER_STATUS = ["ACTIVE", "INACTIVE"]

APPLICATION_STATUS = ["PENDING", "UNDER_REVIEW", "APPROVED", "REJECTED"]

LOAN_PRODUCTS = ["AUTO", "PERSONAL", "MORTGAGE", "CREDIT_CARD"]

CASE_STATUS = ["OPEN", "IN_PROGRESS", "ESCALATED", "CLOSED"]

PRIORITIES = ["LOW", "MEDIUM", "HIGH"]

ALERT_SEVERITY = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

ALERT_CATEGORY = ["IDENTITY", "PAYMENT", "ACCOUNT", "DOCUMENT"]

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def random_date() -> str:
    """Return a random ISO date in the last 5 years."""

    days = random.randint(0, 365 * 5)

    dt = datetime.now() - timedelta(days=days)

    return dt.isoformat(timespec="seconds")


def random_name():
    return (random.choice(FIRST_NAMES), random.choice(LAST_NAMES))


# ---------------------------------------------------------------------
# Customer generation
# ---------------------------------------------------------------------


def generate_customers():
    customers = []

    for customer_id in range(1, CUSTOMER_COUNT + 1):
        first, last = random_name()

        customers.append(
            {
                "customer_id": customer_id,
                "first_name": first,
                "last_name": last,
                "email": (
                    f"{first.lower()}.{last.lower()}{customer_id}@example.com"
                ),
                "country": random.choice(COUNTRIES),
                "credit_score": random.randint(300, 850),
                "risk_level": random.choice(RISK_LEVELS),
                "status": random.choice(CUSTOMER_STATUS),
                "created_at": random_date(),
                "updated_at": random_date(),
            }
        )

    return customers


# ---------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------


def generate_applications():
    applications = []

    for application_id in range(1, APPLICATION_COUNT + 1):
        applications.append(
            {
                "application_id": application_id,
                "customer_id": random.randint(1, CUSTOMER_COUNT),
                "product": random.choice(LOAN_PRODUCTS),
                "amount": random.randint(1000, 100000),
                "status": random.choice(APPLICATION_STATUS),
                "created_at": random_date(),
            }
        )

    return applications


# ---------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------


def generate_cases():
    cases = []

    for case_id in range(1, CASE_COUNT + 1):
        cases.append(
            {
                "case_id": case_id,
                "customer_id": random.randint(1, CUSTOMER_COUNT),
                "priority": random.choice(PRIORITIES),
                "status": random.choice(CASE_STATUS),
                "owner": f"Agent {random.randint(1, 50)}",
                "created_at": random_date(),
            }
        )

    return cases


# ---------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------


def generate_alerts():
    alerts = []

    for alert_id in range(1, ALERT_COUNT + 1):
        alerts.append(
            {
                "alert_id": alert_id,
                "customer_id": random.randint(1, CUSTOMER_COUNT),
                "severity": random.choice(ALERT_SEVERITY),
                "category": random.choice(ALERT_CATEGORY),
                "status": random.choice(CASE_STATUS),
                "created_at": random_date(),
            }
        )

    return alerts


# ---------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------

DATABASE = {
    "customers": generate_customers(),
    "applications": generate_applications(),
    "cases": generate_cases(),
    "alerts": generate_alerts(),
}
