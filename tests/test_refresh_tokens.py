from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from src.app.models import RefreshToken
from src.app.security import hash_refresh_token


def login(client, registered_user):
    response = client.post(
        "/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    return response.json()


def test_refresh_valid_rotates_token(client, registered_user, db_session):
    pair = login(client, registered_user)

    response = client.post(
        "/refresh",
        json={"refresh_token": pair["refresh_token"]},
    )

    assert response.status_code == 200
    new_pair = response.json()
    assert new_pair["access_token"] != pair["access_token"]
    assert new_pair["refresh_token"] != pair["refresh_token"]

    old_hash = hash_refresh_token(pair["refresh_token"])
    old_token = db_session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == old_hash)
    )

    assert old_token is not None
    assert old_token.revoked is True


def test_refresh_expired_token_returns_401(client, registered_user, db_session):
    pair = login(client, registered_user)
    old_hash = hash_refresh_token(pair["refresh_token"])

    stored = db_session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == old_hash)
    )
    assert stored is not None

    stored.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db_session.commit()

    response = client.post(
        "/refresh",
        json={"refresh_token": pair["refresh_token"]},
    )

    assert response.status_code == 401


def test_refresh_revoked_token_revokes_all_user_tokens(
    client, registered_user, db_session
):
    pair = login(client, registered_user)

    first_refresh = client.post(
        "/refresh",
        json={"refresh_token": pair["refresh_token"]},
    )
    assert first_refresh.status_code == 200

    reuse = client.post(
        "/refresh",
        json={"refresh_token": pair["refresh_token"]},
    )
    assert reuse.status_code == 401

    current_hash = hash_refresh_token(first_refresh.json()["refresh_token"])
    current = db_session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == current_hash)
    )

    assert current is not None
    assert current.revoked is True


def test_logout_revokes_refresh_token(client, registered_user):
    pair = login(client, registered_user)

    response = client.post(
        "/logout",
        json={"refresh_token": pair["refresh_token"]},
    )
    assert response.status_code == 204

    reuse = client.post(
        "/refresh",
        json={"refresh_token": pair["refresh_token"]},
    )
    assert reuse.status_code == 401


def test_reuse_revoked_token_revokes_all_user_tokens(
    client, registered_user, db_session
):
    pair = login(client, registered_user)

    rotated = client.post(
        "/refresh",
        json={"refresh_token": pair["refresh_token"]},
    )
    assert rotated.status_code == 200

    current_refresh_token = rotated.json()["refresh_token"]

    reuse = client.post(
        "/refresh",
        json={"refresh_token": pair["refresh_token"]},
    )
    assert reuse.status_code == 401

    current_hash = hash_refresh_token(current_refresh_token)
    current = db_session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == current_hash)
    )
    assert current is not None
    assert current.revoked is True


def test_refresh_rejects_empty_token(client):
    response = client.post("/refresh", json={"refresh_token": ""})
    assert response.status_code == 422


def test_logout_rejects_missing_token(client):
    response = client.post("/logout", json={})
    assert response.status_code == 422


def test_refresh_revoked_token_returns_401(client, registered_user):
    pair = login(client, registered_user)

    first_use = client.post(
        "/refresh",
        json={"refresh_token": pair["refresh_token"]},
    )
    assert first_use.status_code == 200

    reuse = client.post(
        "/refresh",
        json={"refresh_token": pair["refresh_token"]},
    )
    assert reuse.status_code == 401
