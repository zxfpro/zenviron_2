from __future__ import annotations

from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class SmsCodeMessage:
    phone: str
    code: str


class SmsSender:
    def send_code(self, phone: str, code: str) -> None:
        raise NotImplementedError


class FakeSmsSender(SmsSender):
    def __init__(self) -> None:
        self.outbox: list[SmsCodeMessage] = []

    def send_code(self, phone: str, code: str) -> None:
        self.outbox.append(SmsCodeMessage(phone=phone, code=code))


class WebhookSmsSender(SmsSender):
    """
    Generic SMS bridge sender.

    This is used as a pragmatic Volcengine integration point:
    route SMS through your existing gateway/webhook service.
    """

    def __init__(
        self,
        endpoint: str,
        ak: str,
        sk: str,
        sign_name: str,
        template_id: str,
        timeout_seconds: int = 10,
    ) -> None:
        self._endpoint = endpoint
        self._ak = ak
        self._sk = sk
        self._sign_name = sign_name
        self._template_id = template_id
        self._timeout_seconds = timeout_seconds

    def send_code(self, phone: str, code: str) -> None:
        headers = {
            "Content-Type": "application/json",
        }
        # Do not print or expose credentials in logs.
        payload = {
            "phone": phone,
            "code": code,
            "sign_name": self._sign_name,
            "template_id": self._template_id,
            "provider": "volcengine",
            "ak": self._ak,
            "sk": self._sk,
        }
        resp = requests.post(
            self._endpoint,
            json=payload,
            headers=headers,
            timeout=self._timeout_seconds,
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"sms webhook failed: {resp.status_code}")
