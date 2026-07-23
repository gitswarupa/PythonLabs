import time


class RateLimiter:
    def __init__(self, max_requests=100):
        self.max_requests = max_requests

        self.requests = []

    def allow(self):
        now = time.time()

        self.requests = [t for t in self.requests if now - t < 60]

        if len(self.requests) >= self.max_requests:
            return False

        self.requests.append(now)

        return True
