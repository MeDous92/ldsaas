from jose import jwt

from security import (
    JWT_ISSUER,
    JWT_SECRET,
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)


def test_password_hash_round_trip():
    hashed = hash_password("super-secret")
    assert verify_password("super-secret", hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_access_token_payload():
    token = create_access_token(123, "admin")
    payload = jwt.decode(
        token,
        JWT_SECRET,
        algorithms=["HS256"],
        audience="access",
        issuer=JWT_ISSUER,
    )
    assert payload["sub"] == "123"
    assert payload["role"] == "admin"


def test_refresh_token_payload():
    token = create_refresh_token(456, "manager")
    payload = jwt.decode(
        token,
        JWT_SECRET,
        algorithms=["HS256"],
        audience="refresh",
        issuer=JWT_ISSUER,
    )
    assert payload["sub"] == "456"
    assert payload["role"] == "manager"
