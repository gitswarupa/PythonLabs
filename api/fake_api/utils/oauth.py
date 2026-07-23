from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time


def _b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def create_jwt(client_id: str, signing_secret: str, expires_in: int = 3600) -> str:
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64url_encode(
        json.dumps(
            {
                "sub": client_id,
                "exp": int(time.time()) + expires_in,
                "scope": "protected:read",
            }
        ).encode()
    )
    signing_input = f"{header}.{payload}".encode()
    signature = _b64url_encode(
        hmac.new(signing_secret.encode(), signing_input, hashlib.sha256).digest()
    )
    return f"{header}.{payload}.{signature}"


def validate_jwt(token: str, signing_secret: str) -> bool:
    try:
        header, payload, signature = token.split(".")
    except ValueError:
        return False

    signing_input = f"{header}.{payload}".encode()
    expected_signature = _b64url_encode(
        hmac.new(signing_secret.encode(), signing_input, hashlib.sha256).digest()
    )

    if not hmac.compare_digest(signature, expected_signature):
        return False

    try:
        claims = json.loads(_b64url_decode(payload))
    except (json.JSONDecodeError, ValueError):
        return False

    return int(claims.get("exp", 0)) >= int(time.time())
