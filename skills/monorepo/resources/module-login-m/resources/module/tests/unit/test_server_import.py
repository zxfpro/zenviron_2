from apps.backend.login_m_backend.server import app


def test_server_app_importable() -> None:
    assert app is not None
