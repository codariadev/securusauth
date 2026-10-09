import pytest

def test_register_success(client):
    payload = {"email": "ana@example.com", "password": "senha123"}

    response = client.post(
        "/register", json=payload
    )

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

    