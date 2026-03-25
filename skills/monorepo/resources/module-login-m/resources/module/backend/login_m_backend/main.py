from __future__ import annotations

import random
import re
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from .config import Settings, load_settings
from .db import Database
from .email_service import EmailSender, FakeEmailSender, SmtpEmailSender
from .models import EmailRegisterCode, PasswordResetCode, PhoneLoginCode, User
from .rate_limit import InMemoryRateLimiter, LimitRule
from .sms_service import FakeSmsSender, SmsSender, WebhookSmsSender
from .schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    PhoneCodeRequest,
    PhoneLoginRequest,
    RegisterWithCodeRequest,
    ResetPasswordRequest,
    SendEmailCodeRequest,
    TokenResponse,
    UserMeResponse,
)
from .security import create_access_token, decode_access_token, hash_password, verify_password

bearer_scheme = HTTPBearer(auto_error=False)



def _generate_code() -> str:
    return f"{random.randint(0, 999999):06d}"



def _sanitize_phone(phone: str) -> str:
    return re.sub(r"\s+", "", phone)


def _utc_now_naive() -> datetime:
    # Store and compare datetimes as naive UTC for SQLite compatibility.
    return datetime.now(UTC).replace(tzinfo=None)



def create_app(
    settings: Settings | None = None,
    email_sender: EmailSender | None = None,
    sms_sender: SmsSender | None = None,
) -> FastAPI:
    cfg = settings or load_settings()
    db = Database(cfg.database_url)
    limiter = InMemoryRateLimiter()
    sender: EmailSender
    if email_sender:
        sender = email_sender
    elif cfg.use_fake_smtp:
        sender = FakeEmailSender()
    else:
        sender = SmtpEmailSender(
            host=cfg.smtp_host,
            port=cfg.smtp_port,
            user=cfg.smtp_user,
            password=cfg.smtp_pass,
            sender=cfg.smtp_from,
            use_ssl=cfg.smtp_ssl,
        )
    phone_sender: SmsSender
    if sms_sender:
        phone_sender = sms_sender
    elif cfg.sms_provider == "webhook" and cfg.sms_webhook_endpoint:
        phone_sender = WebhookSmsSender(
            endpoint=cfg.sms_webhook_endpoint,
            ak=cfg.sms_ak,
            sk=cfg.sms_sk,
            sign_name=cfg.sms_sign_name,
            template_id=cfg.sms_template_id,
        )
    else:
        phone_sender = FakeSmsSender()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        db.create_all()
        yield

    app = FastAPI(title="login_m API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.settings = cfg
    app.state.db = db
    app.state.email_sender = sender
    app.state.sms_sender = phone_sender
    app.state.rate_limiter = limiter

    def get_session() -> Session:
        return next(db.get_session())

    def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
        session: Session = Depends(get_session),
    ) -> User:
        if not credentials:
            raise HTTPException(status_code=401, detail="未登录")
        try:
            payload = decode_access_token(credentials.credentials, cfg.jwt_secret)
            user_id = UUID(payload["sub"])
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=401, detail="登录状态无效") from exc

        user = session.get(User, user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="用户不可用")
        return user

    def _check_rate_limit(request: Request, label: str, identifier: str) -> None:
        ip = request.client.host if request.client else "unknown"
        key = f"{label}:{identifier}:{ip}"
        ok = limiter.hit(key, LimitRule(max_requests=5, window_seconds=60))
        if not ok:
            raise HTTPException(status_code=429, detail="请求过于频繁，请稍后重试")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/auth/register/email/code")
    def send_register_email_code(
        payload: SendEmailCodeRequest,
        request: Request,
        session: Session = Depends(get_session),
    ) -> dict[str, bool]:
        _check_rate_limit(request, "register_email_code", payload.email)
        exists = session.exec(select(User).where(User.email == payload.email)).first()
        if exists:
            raise HTTPException(status_code=400, detail="邮箱已注册")

        code = _generate_code()
        session.add(
            EmailRegisterCode(
                email=payload.email,
                code=code,
                expires_at=_utc_now_naive() + timedelta(minutes=cfg.code_ttl_minutes),
            )
        )
        session.commit()
        sender.send(payload.email, "login_m 注册验证码", f"您的验证码是：{code}，10分钟内有效。")
        return {"ok": True}

    @app.post("/auth/register_with_code")
    def register_with_code(payload: RegisterWithCodeRequest, session: Session = Depends(get_session)) -> dict[str, bool]:
        exists = session.exec(select(User).where(User.email == payload.email)).first()
        if exists:
            raise HTTPException(status_code=400, detail="邮箱已注册")

        rec = session.exec(
            select(EmailRegisterCode)
            .where(EmailRegisterCode.email == payload.email)
            .where(EmailRegisterCode.code == payload.code)
            .where(EmailRegisterCode.used.is_(False))
            .order_by(EmailRegisterCode.id.desc())
        ).first()
        if not rec or rec.expires_at < _utc_now_naive():
            raise HTTPException(status_code=400, detail="验证码无效或已过期")

        rec.used = True
        session.add(rec)
        session.add(User(email=payload.email, hashed_password=hash_password(payload.password)))
        session.commit()
        return {"ok": True}

    @app.post("/auth/login", response_model=TokenResponse)
    def login(payload: LoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
        user = session.exec(select(User).where(User.email == payload.email)).first()
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=400, detail="邮箱或密码错误")

        token = create_access_token(subject=str(user.id), secret=cfg.jwt_secret, minutes=cfg.jwt_exp_minutes)
        return TokenResponse(access_token=token)

    @app.post("/auth/password/forgot")
    def forgot_password(
        payload: ForgotPasswordRequest,
        request: Request,
        session: Session = Depends(get_session),
    ) -> dict[str, bool]:
        _check_rate_limit(request, "forgot_password", payload.email)
        user = session.exec(select(User).where(User.email == payload.email)).first()
        if not user:
            raise HTTPException(status_code=400, detail="邮箱未注册")

        code = _generate_code()
        session.add(
            PasswordResetCode(
                user_id=user.id,
                code=code,
                expires_at=_utc_now_naive() + timedelta(minutes=cfg.code_ttl_minutes),
            )
        )
        session.commit()
        sender.send(payload.email, "login_m 重置密码验证码", f"您的验证码是：{code}，10分钟内有效。")
        return {"ok": True}

    @app.post("/auth/password/reset")
    def reset_password(payload: ResetPasswordRequest, session: Session = Depends(get_session)) -> dict[str, bool]:
        user = session.exec(select(User).where(User.email == payload.email)).first()
        if not user:
            raise HTTPException(status_code=400, detail="重置失败")

        rec = session.exec(
            select(PasswordResetCode)
            .where(PasswordResetCode.user_id == user.id)
            .where(PasswordResetCode.code == payload.code)
            .where(PasswordResetCode.used.is_(False))
            .order_by(PasswordResetCode.id.desc())
        ).first()
        if not rec or rec.expires_at < _utc_now_naive():
            raise HTTPException(status_code=400, detail="验证码无效或已过期")

        rec.used = True
        user.hashed_password = hash_password(payload.new_password)
        session.add(rec)
        session.add(user)
        session.commit()
        return {"ok": True}

    @app.post("/auth/phone/code")
    def send_phone_code(payload: PhoneCodeRequest, request: Request, session: Session = Depends(get_session)) -> dict[str, bool]:
        phone = _sanitize_phone(payload.phone)
        _check_rate_limit(request, "phone_code", phone)
        code = _generate_code()
        session.add(
            PhoneLoginCode(
                phone=phone,
                code=code,
                expires_at=_utc_now_naive() + timedelta(minutes=cfg.code_ttl_minutes),
            )
        )
        session.commit()
        try:
            phone_sender.send_code(phone=phone, code=code)
        except Exception as exc:  # noqa: BLE001
            if not cfg.sms_soft_fail:
                raise HTTPException(status_code=500, detail="短信发送失败，请稍后重试") from exc
        return {"ok": True}

    @app.post("/auth/phone/login", response_model=TokenResponse)
    def phone_login(payload: PhoneLoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
        phone = _sanitize_phone(payload.phone)
        rec = session.exec(
            select(PhoneLoginCode)
            .where(PhoneLoginCode.phone == phone)
            .where(PhoneLoginCode.code == payload.code)
            .where(PhoneLoginCode.used.is_(False))
            .order_by(PhoneLoginCode.id.desc())
        ).first()
        if not rec or rec.expires_at < _utc_now_naive():
            raise HTTPException(status_code=400, detail="验证码无效或已过期")

        user = session.exec(select(User).where(User.phone == phone)).first()
        if not user:
            user = User(phone=phone, hashed_password=hash_password(UUID(int=0).hex))
            session.add(user)
            session.flush()

        rec.used = True
        session.add(rec)
        session.commit()
        token = create_access_token(subject=str(user.id), secret=cfg.jwt_secret, minutes=cfg.jwt_exp_minutes)
        return TokenResponse(access_token=token)

    @app.get("/auth/me", response_model=UserMeResponse)
    def me(user: User = Depends(get_current_user)) -> UserMeResponse:
        return UserMeResponse(id=str(user.id), email=user.email, phone=user.phone, is_active=user.is_active)

    return app


app = create_app()
