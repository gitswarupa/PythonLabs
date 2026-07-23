from __future__ import annotations

from fake_api.response import Response
from fake_api.utils.delay import simulate_delay
from fake_api.utils.oauth import create_jwt


class AuthResource:
    def __init__(self, config) -> None:
        self.config = config

    def exchange_token(
        self,
        client_id: str,
        client_secret: str,
        grant_type: str = "client_credentials",
    ) -> Response:
        elapsed = simulate_delay(
            self.config.min_delay,
            self.config.max_delay,
        )

        if grant_type != "client_credentials":
            return Response(
                status_code=400,
                error="unsupported_grant_type",
                processing_time_ms=elapsed,
            )

        if (
            client_id != self.config.expected_client_id
            or client_secret != self.config.expected_client_secret
        ):
            return Response(
                status_code=401,
                error="invalid_client",
                processing_time_ms=elapsed,
            )

        access_token = create_jwt(
            client_id=client_id,
            signing_secret=self.config.jwt_signing_secret,
        )

        return Response(
            status_code=200,
            data={
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": 3600,
            },
            processing_time_ms=elapsed,
        )
