import pytest


def test_register_success(client):
    payload = {"email": "ana@example.com", "password": "senha123"}

    response = client.post("/register", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == payload["email"]
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email(client):
    payload = [
        {"email": "ana@example.com", "password": "senha123"},
        {"email": "ana@example.com", "password": "outrasenha"},
    ]

    assert payload[0]["email"] == payload[1]["email"]

    first = client.post("/register", json=payload[0])
    second = client.post("/register", json=payload[1])

    assert first.status_code == 201
    assert second.status_code == 409


def test_register_is_case_insensitive(client):
    email = "Ana@example.com"

    first = client.post("/register", json={"email": email, "password": "senha1234"})
    second = client.post(
        "/register", json={"email": email.lower(), "password": "senha1234"}
    )

    assert first.json()["email"] == email.lower()
    assert second.status_code == 409


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "ana@example.com", "password": "123"},  # senha curta
        {"email": "isso-nao-e-email", "password": "senha1234"},  # e-mail inválido
        {
            "email": "ana@example.com",
            "password": "ç" * 37,
        },  # 37 caracteres, mas 74 bytes
        {"password": "senha1234"},  # falta o e-mail
    ],
    ids=["senha-curta", "email-invalido", "senha-acima-de-72-bytes", "sem-email"],
)
def test_register_invalid_input(client, payload):
    response = client.post("/register", json=payload)
    assert response.status_code == 422


@pytest.fixture
def registered_user(client):
    credentials = {"email": "ana@exemplo.com", "password": "senha123"}
    client.post("/register", json=credentials)
    return credentials


def test_login_success(client, registered_user):
    response = client.post(
        "/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_invalid_credentials(client, registered_user):
    response = client.post(
        "/login", data={"username": registered_user["email"], "password": "senhaerrada"}
    )

    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/login", data={"username": "anas@example.com", "password": "senha123"}
    )

    assert response.status_code == 401


def test_login_adulterated_token_token(client, registered_user):
    response = client.post(
        "/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    token = response.json()["access_token"]

    adulterated_token = token + "adulterated"

    response = client.get(
        "/me", headers={"Authorization": f"Bearer {adulterated_token}"}
    )

    assert response.status_code == 401


def test_login_invalid_token(client, registered_user):
    response = client.post(
        "/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    token = response.json()["access_token"]

    invalid_token = token + "invalid"
    response = client.get("/me", headers={"Authorization": f"Bearer {invalid_token}"})
    assert response.status_code == 401


def test_login_expired_token(client, registered_user):
    from datetime import datetime, timedelta, timezone

    import jwt

    from src.app.config import settings

    expired_token = jwt.encode(
        {
            "sub": registered_user["email"],
            "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
        },
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    response = client.get("/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401


def test_me_with_valid_token(client, registered_user):
    login = client.post(
        "/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    token = login.json()["access_token"]

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == registered_user["email"]


def test_login_errors_are_indistinguishable(client, registered_user):
    wrong_password = client.post(
        "/login", data={"username": registered_user["email"], "password": "senhaerrada"}
    )
    unknown_user = client.post(
        "/login", data={"username": "aana@exemplo.com", "password": "senhaerrada"}
    )

    assert wrong_password.status_code == unknown_user.status_code
    assert wrong_password.json()["detail"] == unknown_user.json()["detail"]
