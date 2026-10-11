from datetime import datetime, timedelta, timezone

import jwt
import pytest

from src.app.config import settings


def test_me_with_valid_token(client, registered_user, auth_header):
    login = client.post(
        "/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    token = login.json()["access_token"]

    response = client.get("/me", headers=auth_header(token))

    assert response.status_code == 200
    assert response.json()["email"] == registered_user["email"]


FUTURE = datetime.now(timezone.utc) + timedelta(minutes=10)


def make_token(claims, key=settings.secret_key):
    return jwt.encode(claims, key, algorithm=settings.algorithm)


@pytest.mark.parametrize(
    "token",
    [
        "isso-nao-e-um-token",
        make_token(
            {"sub": "ana@exemplo.com", "exp": FUTURE},
            key="outra-chave-de-teste-com-mais-de-32-bytes",
        ),  # outra chave
        make_token({"sub": "...", "exp": FUTURE}),  # usuário inexistente
        make_token({"exp": FUTURE}),  # sem sub
    ],
    ids=["nao-e-jwt", "outra-chave", "usuario-inexistente", "sem-sub"],
)
def test_me_rejects_invalid_tokens(client, registered_user, token, auth_header):
    response = client.get("/me", headers=auth_header(token))
    assert response.status_code == 401
