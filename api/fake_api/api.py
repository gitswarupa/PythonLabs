"""
Main entry point for the Fake Enterprise API.

Students should only need to instantiate FakeAPI and then use the
resource collections (customers, applications, cases, alerts).
"""

from __future__ import annotations
from .config import APIConfig
from .resources.alerts import AlertsResource
from .resources.applications import ApplicationsResource
from .resources.cases import CasesResource
from .resources.customers import CustomersResource
from .resources.protected import ProtectedResource
from .response import Response
from .utils.auth import AuthManager


class FakeAPI:
    """
    Main SDK class.

    Supports two authentication mechanisms:

    1. API Key (Labs 1-2)

        api = FakeAPI(api_key="training-key")

    2. Client Credentials (Lab 3)

        api = FakeAPI()

        api.authenticate(
            client_id,
            client_secret,
        )
    """

    def __init__(
        self,
        api_key: str = "",
    ) -> None:
        # Server configuration
        self.config = APIConfig(
            client_api_key=api_key,
        )

        # Resources
        self.customers = CustomersResource(self.config)
        self.applications = ApplicationsResource(self.config)
        self.cases = CasesResource(self.config)
        self.alerts = AlertsResource(self.config)
        self.protected = ProtectedResource(self.config)

    def authenticate(
        self,
        client_id: str,
        client_secret: str,
    ) -> Response:
        """
        Simulates an OAuth2 Client Credentials authentication flow.

        Returns:
            200 -> access token generated
            401 -> invalid client credentials
        """

        token = AuthManager.authenticate(
            client_id,
            client_secret,
        )

        if token is None:
            return Response(
                status_code=401,
                error="Invalid client credentials.",
            )

        self.config.access_token = token

        return Response(
            status_code=200,
            data={
                "access_token": token,
                "token_type": "Bearer",
                "expires_in": 1800,
            },
        )

    def logout(self) -> None:
        """
        Clears the current access token.
        """

        self.config.access_token = None

    @property
    def authenticated(self) -> bool:
        """
        Returns True if either authentication mechanism is active.
        """

        return (
            self.config.client_api_key == self.config.expected_api_key
            or self.config.access_token is not None
        )

    def __repr__(self) -> str:
        return f"<FakeAPI authenticated={self.authenticated}>"