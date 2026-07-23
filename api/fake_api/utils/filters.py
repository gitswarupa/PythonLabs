"""
Filtering utilities for the Fake Enterprise API.

Supported operators

field=value

field__gt
field__gte
field__lt
field__lte
field__contains
field__startswith
field__endswith
"""

from __future__ import annotations

from typing import Any


def apply_filters(
    records: list[dict[str, Any]],
    filters: dict[str, Any],
) -> list[dict[str, Any]]:
    results = records

    for expression, value in filters.items():
        if "__" in expression:
            field, operator = expression.split("__", 1)
        else:
            field = expression
            operator = "eq"

        if operator == "eq":
            results = [
                r
                for r in results
                if str(r.get(field)).lower() == str(value).lower()
            ]

        elif operator == "gt":
            results = [r for r in results if r.get(field, 0) > value]

        elif operator == "gte":
            results = [r for r in results if r.get(field, 0) >= value]

        elif operator == "lt":
            results = [r for r in results if r.get(field, 0) < value]

        elif operator == "lte":
            results = [r for r in results if r.get(field, 0) <= value]

        elif operator == "contains":
            results = [
                r
                for r in results
                if str(value).lower() in str(r.get(field, "")).lower()
            ]

        elif operator == "startswith":
            results = [
                r
                for r in results
                if str(r.get(field, "")).lower().startswith(str(value).lower())
            ]

        elif operator == "endswith":
            results = [
                r
                for r in results
                if str(r.get(field, "")).lower().endswith(str(value).lower())
            ]

    return results
