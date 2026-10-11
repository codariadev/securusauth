from datetime import datetime, timezone

import jwt

from src.app.config import settings
from src.app.security import create_access_token, get_password_hash, verify_password


def test_hash_is_not_the_plain_password():
    password = "senha123"

    hashed = get_password_hash(password)

    assert hashed != password
    assert hashed.startswith("$2b$")


def test_same_password_generates_different_hashes():
    password = "senha123"

    first = get_password_hash(password)
    second = get_password_hash(password)

    assert first != second
    assert verify_password(password, first)
    assert verify_password(password, second)


def test_verify_password():
    hashed = get_password_hash("senha123")

    assert verify_password("senha123", hashed) is True
    assert verify_password("senhaerrada", hashed) is False


def test_access_token_contains_sub_and_exp():
    token = create_access_token({"sub": "ana@exemplo.com"})

    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

    assert payload["sub"] == "ana@exemplo.com"
    assert "exp" in payload
    assert payload["exp"] > datetime.now(timezone.utc).timestamp()
