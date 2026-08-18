import requests


def fetch_cursor_data_w_generators(base_url: str, max_pages: int = 4, batch_size: int = 10):
	"""Generator that simulates cursor/next-page token paging.

	This implementation queries `{base_url}/get` (compatible with httpbun/httpbin-style
	echo endpoints) to demonstrate how a cursor token might be passed in `args`.
	For environments without network access you can keep the same function but
	replace the HTTP call with synthetic data generation.
	"""
	next_token = "token_page_1"
	page_count = 0

	print(f"\n\n\nFetching data using Cursor/Next-Page Token + Generators (Batch Size: {batch_size})")

	while True:
		if not next_token:
			break

		params = {"batch_size": batch_size, "cursor": next_token}

		try:
			response = requests.get(f"{base_url}/get", params=params, timeout=5)
			response.raise_for_status()
			data = response.json()
			raw_cursor = data.get("args", {}).get("cursor", None)
			current_cursor = raw_cursor[0] if isinstance(raw_cursor, list) else raw_cursor
		except Exception:
			# If the network call fails, fall back to a deterministic synthetic cursor value
			page_count += 1
			current_cursor = f"token_page_{page_count}"
			page_items = [f"Record--{i} Page-{page_count} (synthetic)" for i in range(1, batch_size + 1)]
			yield page_items, current_cursor
			if page_count >= max_pages:
				break
			next_token = f"token_page_{page_count + 1}"
			continue

		page_count += 1
		page_items = [
			f"Record--{i} Page-{page_count} Cursor/Next-Page Token w Generators" for i in range(1, batch_size + 1)
		]

		yield page_items, current_cursor

		if page_count >= max_pages:
			break

		next_token = f"token_page_{page_count + 1}"


if __name__ == "__main__":
	for batch, token in fetch_cursor_data_w_generators("https://httpbun.com", max_pages=3, batch_size=5):
		print(f"Retrieved batch using token: '{token}': {batch}")
