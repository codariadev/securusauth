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
    

def test_register_is_case_insensitive(client):
    email = "Ana@example.com"

    first = client.post("/register", json={"email": email, "password": "senha1234"})
    second = client.post("/register", json={"email": email.lower(), "password": "senha1234"})

    assert first.json()["email"] == email.lower()
    assert second.status_code == 409

@pytest.mark.parametrize(
    "payload",
    [
        {"email": "ana@example.com", "password": "123"},      # senha curta
        {"email": "isso-nao-e-email", "password": "senha1234"},             # e-mail inválido
        {"email": "ana@example.com", "password": "ç" * 37},   # 37 caracteres, mas 74 bytes
        {"password": "senha1234"},                             # falta o e-mail
    ],
    ids=["senha-curta", "email-invalido", "senha-acima-de-72-bytes", "sem-email"],
)

def test_register_invalid_input(client, payload):
    response = client.post("/register", json=payload)
    assert response.status_code == 422