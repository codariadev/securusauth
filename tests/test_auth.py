@pytest.mark.parametrize(
        "payload",
        [
            {"email": "ana@example.com", "password": "senha123"},
            {"email": "joao@example.com", "password": "outrasenha"}
        ]
)

def test_register_success(client, payload):
    response = client.post(
        "/register", json=payload
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "ana@example.com"
    assert "password" not in body
    assert "hashed_password" not in body