from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "login_m"
    jwt_secret: str = "change-me-in-env"
    jwt_exp_minutes: int = 60
    database_url: str = "sqlite:///./login_m.db"
    smtp_host: str = "smtp.qq.com"
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_pass: str = ""
    smtp_from: str = "noreply@loginm.local"
    smtp_ssl: bool = True
    use_fake_smtp: bool = True
    sms_provider: str = "mock"
    sms_soft_fail: bool = True
    sms_webhook_endpoint: str = ""
    sms_sign_name: str = ""
    sms_template_id: str = ""
    sms_ak: str = ""
    sms_sk: str = ""
    code_ttl_minutes: int = 10


def _load_email_resource_file() -> tuple[str, str]:
    resource_path = Path(os.getenv("RESOURCE_EMAIL_FILE", "../docs/resource/email.md"))
    if not resource_path.exists():
        return "", ""

    sender = ""
    smtp_pass = ""
    content = resource_path.read_text(encoding="utf-8")
    for raw in content.splitlines():
        line = raw.strip()
        if line.startswith("发送验证码邮箱") and ":" in line:
            sender = line.split(":", 1)[1].strip()
        elif line.lower().startswith("smtp") and ":" in line:
            smtp_pass = line.split(":", 1)[1].strip()
    return sender, smtp_pass



def load_settings() -> Settings:
    sender_from_resource, smtp_from_resource = _load_email_resource_file()
    smtp_user = os.getenv("SMTP_USER", sender_from_resource)
    smtp_pass = os.getenv("SMTP_PASS", smtp_from_resource)
    smtp_from = os.getenv("SMTP_FROM", smtp_user or "noreply@loginm.local")
    use_fake_smtp = os.getenv("USE_FAKE_SMTP", "").lower() == "true"
    if not os.getenv("USE_FAKE_SMTP"):
        use_fake_smtp = not bool(smtp_user and smtp_pass)

    return Settings(
        jwt_secret=os.getenv("JWT_SECRET", "change-me-in-env"),
        jwt_exp_minutes=int(os.getenv("JWT_EXP_MINUTES", "60")),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./login_m.db"),
        smtp_host=os.getenv("SMTP_HOST", "smtp.qq.com"),
        smtp_port=int(os.getenv("SMTP_PORT", "465")),
        smtp_user=smtp_user,
        smtp_pass=smtp_pass,
        smtp_from=smtp_from,
        smtp_ssl=os.getenv("SMTP_SSL", "true").lower() == "true",
        use_fake_smtp=use_fake_smtp,
        sms_provider=os.getenv("SMS_PROVIDER", "mock"),
        sms_soft_fail=os.getenv("SMS_SOFT_FAIL", "true").lower() == "true",
        sms_webhook_endpoint=os.getenv("SMS_WEBHOOK_ENDPOINT", ""),
        sms_sign_name=os.getenv("VOLC_SMS_SIGN_NAME", ""),
        sms_template_id=os.getenv("VOLC_SMS_TEMPLATE_ID", ""),
        sms_ak=os.getenv("VOLC_SMS_AK", os.getenv("TOS_AK", "")),
        sms_sk=os.getenv("VOLC_SMS_SK", os.getenv("TOS_SK", "")),
        code_ttl_minutes=int(os.getenv("CODE_TTL_MINUTES", "10")),
    )
