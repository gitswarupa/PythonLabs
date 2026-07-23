from __future__ import annotations

from fake_api.response import Response
from fake_api.utils.delay import simulate_delay
from fake_api.utils.oauth import validate_jwt


class ProtectedResource:
    def __init__(self, config) -> None:
        self.config = config

    def get(self, bearer_token: str | None = None) -> Response:
        elapsed = simulate_delay(
            self.config.min_delay,
            self.config.max_delay,
        )

        if not bearer_token:
            return Response(
                status_code=401,
                error="Unauthorized",
                processing_time_ms=elapsed,
            )

        token = bearer_token.removeprefix("Bearer ").strip()
        if not validate_jwt(token, self.config.jwt_signing_secret):
            return Response(
                status_code=401,
                error="Unauthorized",
                processing_time_ms=elapsed,
            )

        return Response(
            status_code=200,
            data={
                "resource": "protected-resource",
                "message": "Access Granted",
            },
            processing_time_ms=elapsed,
        )
