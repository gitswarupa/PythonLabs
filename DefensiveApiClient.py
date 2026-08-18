import argparse
import json
import logging
import random
import sys
import time
from json import JSONDecodeError
from typing import Final, Iterable

import requests
from requests import Response

# Config
TARGET_URL_DEFAULT: Final = "https://httpbun.com/status/200,503,504"
REQUEST_TIMEOUT: Final = 5.0
MAX_ATTEMPTS: Final = 6
BASE_BACKOFF: Final = 1.0
MAX_BACKOFF: Final = 10.0
JITTER_FACTOR: Final = 0.5
RETRY_STATUS_CODES: Final = frozenset({429, 503, 504})

logger = logging.getLogger(__name__)


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level, format="%(message)s")


def calculate_backoff(attempt: int) -> float:
    delay = min(BASE_BACKOFF * (2 ** (attempt - 1)), MAX_BACKOFF)
    jitter = random.uniform(0, delay * JITTER_FACTOR)
    return delay + jitter


def fetch_with_retries(url: str, timeout: float = REQUEST_TIMEOUT) -> Response | None:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        logger.info("[INFO] Attempt %d: requesting %s", attempt, url)
        start = time.perf_counter()
        try:
            resp = requests.get(url, timeout=timeout)
            elapsed = time.perf_counter() - start
            logger.info("[INFO] Received %d %s after %.2fs", resp.status_code, resp.reason, elapsed)

            if resp.status_code == 200:
                logger.info("[SUCCESS] Attempt %d: 200 OK. Payload retrieved.", attempt)
                return resp

            if resp.status_code in RETRY_STATUS_CODES:
                backoff = calculate_backoff(attempt)
                logger.warning("[WARN] Attempt %d: %d %s — will retry after %.2fs", attempt, resp.status_code, resp.reason, backoff)
                time.sleep(backoff)
                continue

            resp.raise_for_status()
            return resp

        except requests.RequestException as exc:
            elapsed = time.perf_counter() - start
            if attempt == MAX_ATTEMPTS:
                logger.error("[ERROR] Attempt %d failed after %.2fs: %s", attempt, elapsed, exc)
                break

            backoff = calculate_backoff(attempt)
            logger.warning("[WARN] Attempt %d failed after %.2fs: %s — sleeping %.2fs", attempt, elapsed, exc, backoff)
            time.sleep(backoff)

    return None


def safe_parse_json(text: str) -> object | None:
    if not text:
        logger.warning("[WARN] Empty response body")
        return None

    try:
        return json.loads(text)
    except JSONDecodeError:
        logger.warning("[WARN] JSON decode failed; trying light recovery")
    # Light recovery attempts
    cleaned = text.strip()
    # Trim common corruption: trailing commas, control characters
    cleaned = cleaned.rstrip(", \n\r\t\0")
    # If it's a wrapped object without final bracket, attempt to close it
    if cleaned and cleaned[-1] not in ("]", "}"):
        cleaned = cleaned + "]" if cleaned.lstrip().startswith("[") else cleaned + "}"
    try:
        return json.loads(cleaned)
    except JSONDecodeError:
        logger.error("[ERROR] Payload corrupted beyond light recovery")
        return None


def deduplicate_customers(items: Iterable[dict]) -> list[dict]:
    seen = set()
    out = []
    for item in items:
        if not isinstance(item, dict):
            continue
        key = item.get("id")
        if key is None:
            key = (item.get("email"), item.get("name"))
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def demo_corrupt_flow() -> int:
    """Local demo that feeds a corrupted JSON string to the parser and deduplicator.

    This avoids network dependencies and demonstrates recovery and deduplication.
    """
    logger.info("[DEMO] Running corrupted JSON demo")
    corrupted = '{"customers":[{"id":1,"name":"Alice"},{"id":1,"name":"Alice",],}'
    logger.info("[DEMO] Corrupted payload: %s", corrupted)
    parsed = safe_parse_json(corrupted)
    if parsed is None:
        logger.error("[DEMO] Demo: payload unrecoverable")
        return 2

    customers = parsed.get("customers") if isinstance(parsed, dict) else parsed
    if not isinstance(customers, list):
        logger.error("[DEMO] Demo: unexpected payload shape")
        return 3

    before = len(customers)
    cleaned = deduplicate_customers(customers)
    after = len(cleaned)
    logger.info("[DEMO] Deduplicated customers: %d -> %d", before, after)
    logger.info("[DEMO] Sample customers: %s", cleaned[:5])
    logger.info("[DEMO] Completed without traceback")
    return 0


def process_response(resp: Response) -> int:
    logger.info("[INFO] Response headers: %s", dict(resp.headers))
    body = resp.text
    parsed = safe_parse_json(body)
    if parsed is None:
        logger.error("[ERROR] Could not parse payload")
        return 2

    # Normalize to list of customers
    customers = []
    if isinstance(parsed, dict) and "customers" in parsed and isinstance(parsed["customers"], list):
        customers = parsed["customers"]
    elif isinstance(parsed, list):
        customers = parsed
    elif isinstance(parsed, dict):
        # single object -> treat as one customer
        customers = [parsed]
    else:
        logger.error("[ERROR] Unexpected payload shape")
        return 3

    before = len(customers)
    cleaned = deduplicate_customers(customers)
    after = len(cleaned)
    logger.info("[INFO] Deduplicated customers: %d -> %d", before, after)
    # For demo, print first few items
    logger.info("[INFO] Sample customers: %s", cleaned[:5])
    return 0


def main() -> None:
    configure_logging()
    parser = argparse.ArgumentParser(description="Defensive API client for httpbun")
    parser.add_argument("--url", "-u", default=TARGET_URL_DEFAULT, help="Target URL")
    parser.add_argument("--demo-corrupt", action="store_true", help="Run a local corrupted-JSON demo and exit")
    args = parser.parse_args()

    if getattr(args, "demo_corrupt", False):
        rc = demo_corrupt_flow()
        sys.exit(rc)

    resp = fetch_with_retries(args.url)
    if resp is None:
        logger.error("[ERROR] Mission failed after retries.")
        sys.exit(1)

    rc = process_response(resp)
    sys.exit(rc)


if __name__ == "__main__":
    main()