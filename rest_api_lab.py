import time
from typing import Any

import requests

# --- Configuration (separated from request logic) ---
REQUEST_TIMEOUT = 10

POST_URL = "https://httpbingo.org/post"
BAD_REQUEST_URL = "https://httpbingo.org/status/400"

CUSTOM_HEADERS = {
    "User-Agent": "PayloadArchitect/2.0 (Protocol-Mutation-Client)",
}

# 3-level nested payload: records -> [ { data: { ... } } ]
VALID_PAYLOAD = {
    "records": [
        {
            "data": {
                "name": "Protocol Investigator Report",
                "is_active": True,
                "count": 42,
            }
        }
    ]
}

# Incomplete payload used to trigger validation / 400 handling
INVALID_PAYLOAD = {
    "records": [
        {
            "data": {},
        }
    ]
}

REQUIRED_DATA_FIELDS = ("name", "is_active", "count")


def validate_payload_schema(payload: dict[str, Any]) -> list[str]:
    missing_fields: list[str] = []

    records = payload.get("records")
    if not isinstance(records, list) or not records:
        missing_fields.append("records")
        return missing_fields

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            missing_fields.append(f"records[{index}]")
            continue

        data = record.get("data")
        if not isinstance(data, dict):
            missing_fields.append(f"records[{index}].data")
            continue

        for field in REQUIRED_DATA_FIELDS:
            if field not in data:
                missing_fields.append(f"records[{index}].data.{field}")

    return missing_fields


def extract_missing_fields_from_response(response: requests.Response) -> list[str]:
    missing_fields: list[str] = []

    try:
        error_body = response.json()
    except ValueError:
        return missing_fields

    if isinstance(error_body, dict):
        if isinstance(error_body.get("missing_fields"), list):
            missing_fields.extend(str(field) for field in error_body["missing_fields"])

        if isinstance(error_body.get("errors"), list):
            for error in error_body["errors"]:
                if isinstance(error, dict) and error.get("field"):
                    missing_fields.append(str(error["field"]))
                elif isinstance(error, str):
                    missing_fields.append(error)

        if isinstance(error_body.get("detail"), list):
            for detail in error_body["detail"]:
                if isinstance(detail, dict):
                    field_path = detail.get("loc") or detail.get("field")
                    if field_path:
                        if isinstance(field_path, list):
                            missing_fields.append(".".join(str(part) for part in field_path))
                        else:
                            missing_fields.append(str(field_path))

    return missing_fields


def log_missing_fields(missing_fields: list[str]) -> None:
    print("[VALIDATION FEEDBACK]:")
    if not missing_fields:
        print("  [MISSING_FIELD]: none reported")
        return

    for field in missing_fields:
        print(f"  [MISSING_FIELD]: {field}")


def handle_bad_request(response: requests.Response, payload: dict[str, Any]) -> None:
    print("[ERROR]: 400 Bad Request caught")

    missing_fields = extract_missing_fields_from_response(response)
    if not missing_fields:
        missing_fields = validate_payload_schema(payload)

    log_missing_fields(missing_fields)


def dispatch_post_mutation(
    label: str,
    url: str,
    payload: dict[str, Any],
) -> requests.Response:
    print(f"\n{'=' * 60}")
    print(f"Initiating payload dispatch... [{label}]")
    print("[METHOD]: POST")
    print(f"[HEADERS]: {CUSTOM_HEADERS}")
    print(f"[BODY]: {payload}")

    start = time.perf_counter()
    response = requests.post(
        url,
        json=payload,
        headers=CUSTOM_HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    response_headers = {
        "Server": response.headers.get("Server", ""),
        "Content-Type": response.headers.get("Content-Type", ""),
    }

    print(f"[STATUS]: {response.status_code} {response.reason}")
    print(f"[EXECUTION_TIME]: {elapsed_ms}ms")
    print(f"[HEADERS]: {response_headers}")

    return response


def run_invalid_payload_mission() -> None:
    print("\n--- Phase 1: Invalid payload (validation / 400 handling) ---")

    missing_before_dispatch = validate_payload_schema(INVALID_PAYLOAD)
    if missing_before_dispatch:
        print("[PRE-CHECK]: schema validation failed before dispatch")
        log_missing_fields(missing_before_dispatch)

    response = dispatch_post_mutation(
        "Invalid record mutation",
        BAD_REQUEST_URL,
        INVALID_PAYLOAD,
    )

    if response.status_code == 400:
        handle_bad_request(response, INVALID_PAYLOAD)


def run_valid_payload_mission() -> None:
    print("\n--- Phase 2: Valid payload (server mutation) ---")

    missing_fields = validate_payload_schema(VALID_PAYLOAD)
    if missing_fields:
        print("[PRE-CHECK]: valid payload failed local schema check")
        log_missing_fields(missing_fields)
        return

    response = dispatch_post_mutation(
        "Valid record mutation",
        POST_URL,
        VALID_PAYLOAD,
    )

    if response.ok:
        echoed = response.json().get("json", {})
        record = echoed.get("records", [{}])[0].get("data", {})
        print(
            f"[RESULT]: mutation accepted -> "
            f"name={record.get('name')}, "
            f"is_active={record.get('is_active')}, "
            f"count={record.get('count')}"
        )


def main() -> None:
    print("Laboratory 2: The Payload Architect")
    run_invalid_payload_mission()
    run_valid_payload_mission()


if __name__ == "__main__":
    main()
