from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_user_registration():
    response = client.post(
        "/api/v1/users/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "Test@12345",
        },
    )
    # allow created / already exists / bad request
    assert response.status_code in (201, 400, 409)
    if response.status_code == 201:
        assert response.json()["email"] == "test@example.com"


def test_user_login():
    # First register (idempotent)
    client.post(
        "/api/v1/users/register",
        json={
            "email": "login_test@example.com",
            "username": "login_test",
            "full_name": "Login Test",
            "password": "Test@12345",
        },
    )

    # Then login using form data, matching users.py login route
    response = client.post(
        "/api/v1/users/login",
        data={
            "username": "login_test@example.com",
            "password": "Test@12345",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
