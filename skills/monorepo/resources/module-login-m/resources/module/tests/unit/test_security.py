from apps.backend.login_m_backend.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password() -> None:
    raw = "Password123!"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_token_create_and_decode() -> None:
    secret = "unit-test-secret-with-at-least-32-bytes"
    token = create_access_token(subject="abc-123", secret=secret, minutes=5)
    payload = decode_access_token(token, secret)
    assert payload["sub"] == "abc-123"
    assert payload["exp"] > payload["iat"]
