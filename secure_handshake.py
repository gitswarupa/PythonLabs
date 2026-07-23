import os
import sys
from pathlib import Path

from dotenv import load_dotenv

API_PATH = Path(__file__).parent / "api"
sys.path.insert(0, str(API_PATH))

from fake_api import FakeAPI  # noqa: E402


def load_credentials() -> tuple[str, str]:
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError("CLIENT_ID and CLIENT_SECRET must be set in .env")

    return client_id, client_secret


def main() -> None:
    print("[AUTH] Loading credentials from .env...")
    client_id, client_secret = load_credentials()

    api = FakeAPI()

    print("[REQ] GET /protected-resource")
    initial_response = api.protected.get()
    print(f"[RESP] {initial_response.status_code} {initial_response.error}")

    print("[AUTH] Initiating Token Exchange...")
    token_response = api.authenticate(
        client_id=client_id,
        client_secret=client_secret,
    )

    if not token_response.ok:
        print(f"[AUTH] Token exchange failed: {token_response.error}")
        return

    access_token = token_response.data["access_token"]
    print("[AUTH] Successfully acquired JWT (REDACTED)")

    print("[REQ] GET /protected-resource with Bearer")
    protected_response = api.protected.get(bearer_token=access_token)

    if protected_response.ok:
        print("[RESP] 200 OK - Access Granted")
    else:
        print(f"[RESP] {protected_response.status_code} {protected_response.error}")


if __name__ == "__main__":
    main()
