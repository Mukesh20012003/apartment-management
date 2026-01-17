# backend/tests/test_tickets.py
from uuid import uuid4
from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
from app.database.session import SessionLocal
from app.models.resident import Resident
from app.models.user import User


def register_resident(email: str, password: str):
    return client.post(
       "/api/v1/users/register",
        json={
            "email": email,
            "password": password,
            "role": "resident",
            "full_name": "Resident User",
            "username": email.split("@")[0],
            "phone_number": "8888888888",
        },
    )


def login(email: str, password: str):
    return client.post(
        "/api/v1/users/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


def create_ticket(token: str):
    return client.post(
        "/tickets/",
        json={
            "title": "Test ticket from pytest",  # length > 10
            "description": "This is a longer test description for the ticket.",  # > 20 chars
            "category": "general",  # any string is fine
            "priority": "medium",   # matches TicketPriority
        },
        headers={"Authorization": f"Bearer {token}"},
    )




def test_create_and_get_ticket():
    email = "ticket_user@example.com"
    password = "Test@12345"

    # 1) Register resident user (via API helper)
    register_resident(email, password)

    # 2) Login
    login_resp = login(email, password)
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # 3) Create resident profile linked to this user and a real flat
    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()
    assert user is not None

    flat_id = UUID("75cf6b9e-d3c8-4d2f-af66-5f3ab73269dd")  # must exist in DB

    resident = db.query(Resident).filter_by(user_id=user.id).first()
    if resident is None:
        resident = Resident(
            user_id=user.id,
            flat_id=flat_id,
            # add any other NOT NULL fields required by Resident model
        )
        db.add(resident)
        db.commit()
        db.refresh(resident)

    db.close()

    # 4) Create ticket
    create_resp = create_ticket(token)
    print("TICKET CREATE STATUS:", create_resp.status_code)
    print("TICKET CREATE BODY:", create_resp.json())
    assert create_resp.status_code == 201
    ticket = create_resp.json()
    ticket_id = ticket["id"]

    # 5) Get ticket
    get_resp = client.get(
        f"/tickets/{ticket_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == ticket_id
