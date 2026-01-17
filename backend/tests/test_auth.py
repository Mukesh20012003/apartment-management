# backend/tests/test_auth.py
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def register_user(email: str, password: str, role: str = "resident"):
    return client.post(
        "/api/v1/users/register",
        json={
            "email": email,
            "password": password,
            "role": role,
            "full_name": "Test User",
            "username": email.split("@")[0],
            "phone_number": "9999999999",
        },
    )


def login_user(email: str, password: str):
    return client.post(
        "/api/v1/users/login",
        data={
            "username": email,
            "password": password,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


@pytest.fixture
def user_credentials():
    return {
        "email": "test_auth@example.com",
        "password": "Test@12345",
    }


def test_register(user_credentials):
    resp = register_user(
        email=user_credentials["email"],
        password=user_credentials["password"],
    )
    assert resp.status_code in (201, 400, 409)


def test_login_and_access_protected(user_credentials):
    # ensure user exists
    register_user(
        email=user_credentials["email"],
        password=user_credentials["password"],
    )

    # login
    resp = login_user(
        email=user_credentials["email"],
        password=user_credentials["password"],
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    token = body["access_token"]

    # call a protected endpoint, e.g. /users/me
    me_resp = client.get(
       "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == user_credentials["email"]
