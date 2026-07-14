"""Regex extraction helpers for product codes, prices, and dates.

Functions
- `extract_from_text(text) -> list[dict]`: Returns a list of dicts with
  keys `product_code`, `price`, and `date` found in `text`.

The implementation prefers a single-pattern search (product + price + date)
and falls back to independent extraction with best-effort pairing.
"""

from __future__ import annotations

import re
import json
from typing import List, Dict, Optional


def extract_from_text(text: str) -> List[Dict[str, Optional[object]]]:
	"""Extract product codes, prices, and dates from unstructured text.

	Returns a list of dictionaries with keys: `product_code` (str),
	`price` (float) and `date` (str in YYYY-MM-DD) where available.
	"""

	# Try to capture product, price, and date in a single pass using proximity.
	combined_re = re.compile(
		r"(?P<product>[A-Z]{3}-\d{3,6}).{0,120}?\$?\s?(?P<price>\d{1,3}(?:,\d{3})*(?:\.\d{2})).{0,200}?(?P<date>20\d{2}-\d{2}-\d{2})",
		re.S,
	)

	results: List[Dict[str, Optional[object]]] = []
	for m in combined_re.finditer(text):
		prod = m.group("product")
		price = float(m.group("price").replace(",", ""))
		date = m.group("date")
		results.append({"product_code": prod, "price": price, "date": date})

	if results:
		return results

	# Fallback: extract each type independently and pair by occurrence order.
	prods = re.findall(r"\b[A-Z]{3}-\d{3,6}\b", text)
	prices = re.findall(r"\$\s?(\d{1,3}(?:,\d{3})*(?:\.\d{2}))", text)
	dates = re.findall(r"\b(20\d{2}-\d{2}-\d{2})\b", text)

	# If we have full triples, align by index.
	n = min(len(prods), len(prices), len(dates))
	if n > 0:
		for i in range(n):
			results.append(
				{
					"product_code": prods[i],
					"price": float(prices[i].replace(",", "")),
					"date": dates[i],
				}
			)
		return results

	# If no complete triples, produce best-effort entries using available items.
	maxn = max(len(prods), len(prices), len(dates))
	for i in range(maxn):
		prod = prods[i] if i < len(prods) else None
		price = float(prices[i].replace(",", "")) if i < len(prices) else None
		date = dates[i] if i < len(dates) else None
		results.append({"product_code": prod, "price": price, "date": date})

	return results


if __name__ == "__main__":
	# Example usage / quick smoke test using the sample from the lab brief.
	sample = (
		"log_entry_09: proc_error %$!\n"
		"item: PRD-9981 priced at $45.99 .. user_id_none..\n"
		"2023-11-01\nend_log."
	)

	extracted = extract_from_text(sample)
	print(json.dumps(extracted, indent=2))
