def test_register_success(client):
    response = client.post(
        "/register", json={"email": "ana@example.com", "password": "senha123"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "ana@example.com"
    assert "password" not in body
    assert "hashed_password" not in body