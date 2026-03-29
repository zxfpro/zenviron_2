from apps.backend.login_m_backend.email_service import FakeEmailSender
from apps.backend.login_m_backend.rate_limit import InMemoryRateLimiter, LimitRule


def test_fake_email_sender_records_messages() -> None:
    sender = FakeEmailSender()
    sender.send("u@example.com", "subject", "body")
    assert len(sender.outbox) == 1
    msg = sender.outbox[0]
    assert msg.to_email == "u@example.com"
    assert msg.subject == "subject"


def test_in_memory_rate_limiter_blocks_after_limit() -> None:
    limiter = InMemoryRateLimiter()
    rule = LimitRule(max_requests=2, window_seconds=60)
    assert limiter.hit("k", rule) is True
    assert limiter.hit("k", rule) is True
    assert limiter.hit("k", rule) is False
