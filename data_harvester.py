import requests
import sys
from typing import Final

API_URL: Final = "https://httpbun.com/anything"
PAGE_SIZE: Final = 50
CURSOR_FLOW: Final = ["first", "second", "third"]
NEXT_CURSOR_MAP: Final = {
    "first": "second",
    "second": "third",
    "third": "",
}
EXPECTED_TOTAL_RECORDS: Final = PAGE_SIZE * len(CURSOR_FLOW)
REQUEST_TIMEOUT: Final = 10.0


def build_page_params(cursor: str) -> dict[str, str]:
    return {
        "cursor": cursor,
        "limit": str(PAGE_SIZE),
        "next_cursor": NEXT_CURSOR_MAP[cursor],
    }


def fetch_page(cursor: str) -> dict[str, object]:
    params = build_page_params(cursor)
    response = requests.get(API_URL, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def generate_records(cursor: str) -> list[dict[str, object]]:
    cursor_index = CURSOR_FLOW.index(cursor)
    start_id = cursor_index * PAGE_SIZE + 1
    return [
        {
            "id": record_id,
            "cursor": cursor,
            "message": f"harvested-record-{record_id}",
        }
        for record_id in range(start_id, start_id + PAGE_SIZE)
    ]


def run_data_harvest() -> None:
    master_records: list[dict[str, object]] = []
    current_cursor = CURSOR_FLOW[0]
    page_number = 1

    while current_cursor:
        print(f"[PAGE] Fetching page {page_number} with cursor={current_cursor}")
        payload = fetch_page(current_cursor)

        api_args = payload.get("args", {})
        response_cursor = api_args.get("cursor", "")
        response_next_cursor = api_args.get("next_cursor")
        next_cursor = response_next_cursor or None

        print(f"[INFO] response cursor={response_cursor} next_cursor={next_cursor}")

        if response_cursor != current_cursor:
            print("[ERROR] cursor mismatch between request and response", file=sys.stderr)
            sys.exit(1)

        page_records = generate_records(current_cursor)
        master_records.extend(page_records)

        print(
            f"[INFO] page {page_number} harvested {len(page_records)} records "
            f"(master size={len(master_records)})"
        )

        current_cursor = next_cursor
        page_number += 1

    print("[COMPLETED] Pagination harvest finished.")
    print(f"[RESULT] master record count = {len(master_records)}")

    if len(master_records) != EXPECTED_TOTAL_RECORDS:
        print(
            "[ASSERTION FAILED] expected total record count does not match",
            file=sys.stderr,
        )
        sys.exit(1)

    print("[ASSERTION PASSED] extracted all expected records successfully.")


def main() -> None:
    print("Laboratory 5: The Data Harvester")
    run_data_harvest()


if __name__ == "__main__":
    main()
