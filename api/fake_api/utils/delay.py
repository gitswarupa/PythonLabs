import random
import time


def simulate_delay(min_delay: float, max_delay: float) -> int:
    """
    Simulate network latency.

    Returns:
        Processing time in milliseconds.
    """

    delay = random.uniform(min_delay, max_delay)

    time.sleep(delay)

    return int(delay * 1000)
