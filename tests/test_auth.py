

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


def test_login_adulterated_token_toke(client, registered_user, auth_header):
    response = client.post(
        "/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    token = response.json()["access_token"]

    adulterated_token = token + "adulterated"

    response = client.get("/me", headers=auth_header(adulterated_token))

    assert response.status_code == 401


def test_login_invalid_token(client, registered_user, auth_header):
    response = client.post(
        "/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    token = response.json()["access_token"]

    invalid_token = token + "invalid"
    response = client.get("/me", headers=auth_header(invalid_token))
    assert response.status_code == 401


def test_login_expired_token(client, registered_user, auth_header):
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

    response = client.get("/me", headers=auth_header(expired_token))
    assert response.status_code == 401


def test_login_errors_are_indistinguishable(client, registered_user):
    wrong_password = client.post(
        "/login", data={"username": registered_user["email"], "password": "senhaerrada"}
    )
    unknown_user = client.post(
        "/login", data={"username": "aana@exemplo.com", "password": "senhaerrada"}
    )

    assert wrong_password.status_code == unknown_user.status_code
    assert wrong_password.json()["detail"] == unknown_user.json()["detail"]


