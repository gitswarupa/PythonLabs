from dataclasses import dataclass


@dataclass(slots=True)
class APIConfig:
    # Server configuration
    expected_api_key: str = "training-key"

    # OAuth2 client credentials
    expected_client_id: str = "training-client"
    expected_client_secret: str = "training-secret"
    jwt_signing_secret: str = "training-secret"

    # Client API key
    client_api_key: str = ""

    # OAuth2 access token (set after authenticate())
    access_token: str | None = None

    # Artificial latency
    min_delay: float = 0.15
    max_delay: float = 0.75

    # Failure simulation
    failure_rate: float = 0.03
    timeout_rate: float = 0.01

    # Rate limiting
    rate_limit: int = 100

    # Pagination
    default_page_size: int = 25
    max_page_size: int = 100
