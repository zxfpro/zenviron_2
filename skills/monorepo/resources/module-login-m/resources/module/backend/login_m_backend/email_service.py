from __future__ import annotations

import smtplib
from dataclasses import dataclass
from email.mime.text import MIMEText


@dataclass(frozen=True)
class OutboxEmail:
    to_email: str
    subject: str
    body: str


class EmailSender:
    def send(self, to_email: str, subject: str, body: str) -> None:
        raise NotImplementedError


class SmtpEmailSender(EmailSender):
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        sender: str,
        use_ssl: bool = True,
    ) -> None:
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._sender = sender
        self._use_ssl = use_ssl

    def send(self, to_email: str, subject: str, body: str) -> None:
        msg = MIMEText(body, "plain", "utf-8")
        msg["From"] = self._sender
        msg["To"] = to_email
        msg["Subject"] = subject

        if self._use_ssl:
            with smtplib.SMTP_SSL(self._host, self._port) as client:
                if self._user:
                    client.login(self._user, self._password)
                client.sendmail(self._sender, [to_email], msg.as_string())
            return

        with smtplib.SMTP(self._host, self._port) as client:
            client.starttls()
            if self._user:
                client.login(self._user, self._password)
            client.sendmail(self._sender, [to_email], msg.as_string())


class FakeEmailSender(EmailSender):
    def __init__(self) -> None:
        self.outbox: list[OutboxEmail] = []

    def send(self, to_email: str, subject: str, body: str) -> None:
        self.outbox.append(OutboxEmail(to_email=to_email, subject=subject, body=body))
