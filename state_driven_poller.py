import logging
import random
import time
from typing import Final

import requests
from requests import Response

TARGET_URL: Final = "https://httpbun.com/status/200,503,429"
REQUEST_TIMEOUT: Final = 5.0
MAX_ATTEMPTS: Final = 5
BASE_BACKOFF: Final = 1.0
MAX_BACKOFF: Final = 10.0
JITTER_FACTOR: Final = 0.5
RETRY_STATUS_CODES: Final = frozenset({429, 503})

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )


def calculate_backoff(attempt: int) -> float:
    delay = min(BASE_BACKOFF * (2 ** (attempt - 1)), MAX_BACKOFF)
    jitter = random.uniform(0, delay * JITTER_FACTOR)
    return delay + jitter


def fetch_with_retries(url: str) -> Response | None:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        logger.info(f"[INFO] Attempt {attempt}: requesting {url}")
        start = time.perf_counter()

        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            elapsed = time.perf_counter() - start
            logger.info(
                f"[INFO] Received status {response.status_code} {response.reason} "
                f"after {elapsed:.2f}s"
            )

            if response.status_code == 200:
                logger.info("[SUCCESS] Attempt %d: 200 OK. Payload retrieved.", attempt)
                return response

            if response.status_code in RETRY_STATUS_CODES:
                backoff = calculate_backoff(attempt)
                logger.warning("[WARNING] Attempt %d failed: %d %s", attempt, response.status_code, response.reason)
                logger.info("[INFO] Calculating backoff... Sleeping for %.2fs", backoff)
                time.sleep(backoff)
                continue

            response.raise_for_status()
            return response

        except requests.RequestException as exc:
            elapsed = time.perf_counter() - start
            if attempt == MAX_ATTEMPTS:
                logger.error("[ERROR] Attempt %d failed after %.2fs: %s", attempt, elapsed, exc)
                break

            backoff = calculate_backoff(attempt)
            logger.warning("[WARNING] Attempt %d failed after %.2fs: %s", attempt, elapsed, exc)
            logger.info("[INFO] Calculating backoff... Sleeping for %.2fs", backoff)
            time.sleep(backoff)

    return None


def main() -> None:
    configure_logging()
    logger.info("Laboratory 4: The State-Driven Poller")
    response = fetch_with_retries(TARGET_URL)

    if response is None:
        logger.error("[ERROR] Mission failed after %d attempts.", MAX_ATTEMPTS)
        return

    logger.info("[INFO] Successful response received.")
    logger.info("[INFO] Response status: %s %s", response.status_code, response.reason)
    logger.info("[INFO] Response headers: %s", dict(response.headers))
    logger.info("[INFO] Response body: %s", response.text.strip())


if __name__ == "__main__":
    main()
