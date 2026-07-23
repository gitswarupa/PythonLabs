from fake_api.config import APIConfig
from fake_api.response import Response
from fake_api.utils.oauth import create_jwt


def check_api_key(config):
    if config.client_api_key != config.expected_api_key:
        return Response(
            status_code=401,
            error="Unauthorized",
        )

    return None


class AuthManager:
    @staticmethod
    def authenticate(client_id: str, client_secret: str) -> str | None:
        config = APIConfig()

        if (
            client_id != config.expected_client_id
            or client_secret != config.expected_client_secret
        ):
            return None

        return create_jwt(
            client_id=client_id,
            signing_secret=config.jwt_signing_secret,
        )
