from fastapi.testclient import TestClient

from apps.backend.login_m_backend.email_service import FakeEmailSender
from apps.backend.login_m_backend.sms_service import FakeSmsSender
from tests.conftest import extract_code


def register_user(client: TestClient, fake_sender: FakeEmailSender, email: str, password: str) -> None:
    r = client.post("/auth/register/email/code", json={"email": email})
    assert r.status_code == 200
    code = extract_code(fake_sender.outbox[-1].body)
    r = client.post(
        "/auth/register_with_code",
        json={"email": email, "code": code, "password": password},
    )
    assert r.status_code == 200


def test_email_register_login_me_flow(client: TestClient, fake_sender: FakeEmailSender) -> None:
    register_user(client, fake_sender, "alice@example.com", "StrongPass123")

    login = client.post("/auth/login", json={"email": "alice@example.com", "password": "StrongPass123"})
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    data = me.json()
    assert data["email"] == "alice@example.com"


def test_password_reset_flow(client: TestClient, fake_sender: FakeEmailSender) -> None:
    register_user(client, fake_sender, "bob@example.com", "OldPassword123")
    forgot = client.post("/auth/password/forgot", json={"email": "bob@example.com"})
    assert forgot.status_code == 200
    reset_code = extract_code(fake_sender.outbox[-1].body)

    reset = client.post(
        "/auth/password/reset",
        json={"email": "bob@example.com", "code": reset_code, "new_password": "NewPassword123"},
    )
    assert reset.status_code == 200

    old_login = client.post("/auth/login", json={"email": "bob@example.com", "password": "OldPassword123"})
    assert old_login.status_code == 400

    new_login = client.post("/auth/login", json={"email": "bob@example.com", "password": "NewPassword123"})
    assert new_login.status_code == 200


def test_phone_login_flow(client: TestClient, fake_sms_sender: FakeSmsSender) -> None:
    send = client.post("/auth/phone/code", json={"phone": "13800000000"})
    assert send.status_code == 200
    code = fake_sms_sender.outbox[-1].code

    login = client.post("/auth/phone/login", json={"phone": "13800000000", "code": code})
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["phone"] == "13800000000"


def test_reject_reused_code(client: TestClient, fake_sender: FakeEmailSender) -> None:
    register_user(client, fake_sender, "reuse@example.com", "StrongPass123")
    forgot = client.post("/auth/password/forgot", json={"email": "reuse@example.com"})
    assert forgot.status_code == 200
    reset_code = extract_code(fake_sender.outbox[-1].body)

    first = client.post(
        "/auth/password/reset",
        json={"email": "reuse@example.com", "code": reset_code, "new_password": "NewPassword123"},
    )
    assert first.status_code == 200

    second = client.post(
        "/auth/password/reset",
        json={"email": "reuse@example.com", "code": reset_code, "new_password": "AnotherPassword123"},
    )
    assert second.status_code == 400


def test_unauthorized_me(client: TestClient) -> None:
    me = client.get("/auth/me")
    assert me.status_code == 401


def test_forgot_password_unregistered_email(client: TestClient) -> None:
    resp = client.post("/auth/password/forgot", json={"email": "ghost@example.com"})
    assert resp.status_code == 400


def test_rate_limit_on_send_code(client: TestClient) -> None:
    email = "limit@example.com"
    last_status = 200
    for _ in range(6):
        resp = client.post("/auth/register/email/code", json={"email": email})
        last_status = resp.status_code
    assert last_status == 429
