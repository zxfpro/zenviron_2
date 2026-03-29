from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from apps.backend.login_m_backend.config import Settings
from apps.backend.login_m_backend.email_service import FakeEmailSender
from apps.backend.login_m_backend.main import create_app
from apps.backend.login_m_backend.sms_service import FakeSmsSender


@pytest.fixture()
def fake_sender() -> FakeEmailSender:
    return FakeEmailSender()


@pytest.fixture()
def fake_sms_sender() -> FakeSmsSender:
    return FakeSmsSender()


@pytest.fixture()
def client(fake_sender: FakeEmailSender, fake_sms_sender: FakeSmsSender, tmp_path) -> TestClient:
    db_file = tmp_path / "test_login_m.db"
    settings = Settings(
        jwt_secret="test-secret-with-at-least-32-bytes",
        database_url=f"sqlite:///{db_file}",
        use_fake_smtp=True,
        code_ttl_minutes=10,
    )
    app = create_app(settings=settings, email_sender=fake_sender, sms_sender=fake_sms_sender)
    with TestClient(app) as c:
        yield c



def extract_code(body: str) -> str:
    match = re.search(r"(\d{6})", body)
    if not match:
        raise AssertionError("verification code not found")
    return match.group(1)
