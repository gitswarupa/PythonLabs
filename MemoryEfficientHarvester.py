"""
MemoryEfficientHarvester.py

- Streams products from DummyJSON (https://dummyjson.com/docs/products)
- Uses generators to avoid building large in-memory structures
- Filters "HIGH risk" products deterministically
- Writes matches directly to CSV
- Measures execution time and peak memory via tracemalloc
- Optionally reports RSS via `psutil` if available
"""

from __future__ import annotations
import csv
import gc
import math
import time
import tracemalloc
from typing import Callable, Dict, Generator, Any

import requests

BASE_URL = "https://dummyjson.com/products"
PER_PAGE_DEFAULT = 10
OUT_CSV = "high_risk_products.csv"


def page_generator(session: requests.Session, base_url: str, per_page: int = PER_PAGE_DEFAULT) -> Generator[Dict[str, Any], None, None]:
	"""Yield product dicts from DummyJSON one page at a time."""
	# Get total count first
	resp = session.get(f"{base_url}?limit=1&skip=0", timeout=10)
	resp.raise_for_status()
	meta = resp.json()
	total = int(meta.get("total", 0))
	if total == 0:
		return

	pages = math.ceil(total / per_page)
	for page_idx in range(pages):
		skip = page_idx * per_page
		url = f"{base_url}?limit={per_page}&skip={skip}"
		resp = session.get(url, timeout=20)
		resp.raise_for_status()
		payload = resp.json()
		items = payload.get("products", [])
		for item in items:
			yield item


def default_risk_classifier(product: Dict[str, Any]) -> bool:
	"""
	Deterministic rule that marks some products HIGH risk for the lab:
	- product id divisible by 17, OR
	- rating < 3.0, OR
	- price > 500
	Adjust rules as needed for your testing dataset.
	"""
	try:
		pid = int(product.get("id", -1))
		rating = float(product.get("rating", 5.0))
		price = float(product.get("price", 0.0))
	except Exception:
		return False

	if pid % 17 == 0:
		return True
	if rating < 3.0:
		return True
	if price > 500:
		return True
	return False


def stream_high_risk_to_csv(
	base_url: str = BASE_URL,
	per_page: int = PER_PAGE_DEFAULT,
	out_path: str = OUT_CSV,
	risk_fn: Callable[[Dict[str, Any]], bool] = default_risk_classifier,
) -> tuple[int, int, list[str]]:
	"""
	Fetch pages and write HIGH risk products to CSV. Returns number of matches written.
	This function is memory-efficient: at most one page and one record live at a time.
	"""
	matches_written = 0
	total_scanned = 0
	high_ids: list[str] = []
	session = requests.Session()

	with open(out_path, "w", newline="", encoding="utf-8") as fh:
		writer = csv.writer(fh)
		# minimal fields to reduce memory footprint on disk and in Python structures
		writer.writerow(["id", "title", "price", "rating", "category", "risk_note"])

		for product in page_generator(session, base_url, per_page):
			total_scanned += 1
			if risk_fn(product):
				# write only required columns immediately
				writer.writerow(
					[
						product.get("id"),
						product.get("title"),
						product.get("price"),
						product.get("rating"),
						product.get("category"),
						"HIGH",
					]
				)
				# record id for the final metrics summary (small list)
				pid = product.get("id")
				try:
					high_ids.append(str(pid))
				except Exception:
					pass
				matches_written += 1

	session.close()
	return matches_written, total_scanned, high_ids


def profile_function(func, *args, **kwargs):
	"""
	Profile a function's execution time and memory (tracemalloc).
	Prints execution time and peak memory allocated by Python objects.
	"""
	gc.disable()
	tracemalloc.start()
	start = time.perf_counter()
	try:
		result = func(*args, **kwargs)
	finally:
		elapsed = time.perf_counter() - start
		current, peak = tracemalloc.get_traced_memory()
		tracemalloc.stop()
		gc.enable()

	# collect metrics
	metrics: dict[str, float | None] = {
		"elapsed_sec": elapsed,
		"net_alloc_bytes": current,
		"peak_alloc_bytes": peak,
		"process_rss_bytes": None,
	}

	try:
		import psutil
		import os

		proc = psutil.Process(os.getpid())
		rss = proc.memory_info().rss
		metrics["process_rss_bytes"] = rss
	except Exception:
		metrics["process_rss_bytes"] = None

	print(f"[{func.__name__}] Execution Time: {metrics['elapsed_sec']:.6f} seconds")
	print(f"[{func.__name__}] Net Allocated Memory: {metrics['net_alloc_bytes'] / (1024 * 1024):.4f} MB")
	print(f"[{func.__name__}] Peak Memory Allocation: {metrics['peak_alloc_bytes'] / (1024 * 1024):.4f} MB")
	if metrics["process_rss_bytes"] is not None:
		print(f"[{func.__name__}] Process RSS: {metrics['process_rss_bytes'] / (1024 * 1024):.4f} MB")

	return result, metrics


def main():
	print("Memory-Efficient Harvester (DummyJSON products)")
	per_page = PER_PAGE_DEFAULT  # tune to simulate larger pages: e.g., 50, 100
	print(f"Using per_page={per_page}, writing output to: {OUT_CSV}")

	# Run and profile the streaming harvester
	(result, metrics) = profile_function(stream_high_risk_to_csv, BASE_URL, per_page, OUT_CSV, default_risk_classifier)
	matches_written, total_scanned, high_ids = result

	print(f"Matches written: {matches_written}")
	print(f"Total scanned: {total_scanned}")

	# Write metrics summary to CSV (overwrites/creates)
	metrics_csv = "harvest_metrics.csv"
	with open(metrics_csv, "w", newline="", encoding="utf-8") as mh:
		mwriter = csv.writer(mh)
		mwriter.writerow([
			"timestamp",
			"per_page",
			"matches_written",
			"total_scanned",
			"elapsed_sec",
			"net_alloc_mb",
			"peak_alloc_mb",
			"process_rss_mb",
		])
		rss_mb = metrics["process_rss_bytes"] / (1024 * 1024) if metrics["process_rss_bytes"] else None
		mwriter.writerow([
			time.strftime("%Y-%m-%d %H:%M:%S"),
			per_page,
			matches_written,
			total_scanned,
			f"{metrics['elapsed_sec']:.6f}",
			f"{metrics['net_alloc_bytes'] / (1024 * 1024):.6f}",
			f"{metrics['peak_alloc_bytes'] / (1024 * 1024):.6f}",
			f"{rss_mb:.6f}" if rss_mb is not None else "",
		])
	print(f"Wrote metrics to: {metrics_csv}")


if __name__ == "__main__":
	main()
