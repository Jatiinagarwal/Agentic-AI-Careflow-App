from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
import smtplib

from app.config import get_settings


@dataclass
class EmailSendResult:
    status: str
    provider: str
    provider_message_id: str = ""
    error_message: str = ""
    sent_at: datetime | None = None


def _settings_ready() -> tuple[bool, str]:
    settings = get_settings()
    if not settings.email_enabled:
        return False, "EMAIL_ENABLED=false"
    if not settings.smtp_configured:
        return False, "SMTP settings are incomplete"
    return True, "SMTP configured"


def email_settings_safe() -> dict:
    settings = get_settings()
    configured, reason = _settings_ready()
    return {
        "email_enabled": settings.email_enabled,
        "smtp_configured": configured,
        "smtp_host": settings.smtp_host,
        "smtp_port": settings.smtp_port,
        "smtp_from_email": settings.smtp_from_email,
        "smtp_from_name": settings.smtp_from_name,
        "smtp_use_tls": settings.smtp_use_tls,
        "mode": "real_smtp" if configured else "mock_send",
        "warning": "Real SMTP sending is enabled. Confirm recipient, consent, and content before sending." if configured else f"Real email is disabled or incomplete ({reason}). Sending will be recorded as Mock Sent.",
    }


def send_patient_email(recipient_email: str, subject: str, body: str) -> EmailSendResult:
    settings = get_settings()
    configured, reason = _settings_ready()
    now = datetime.utcnow()

    if not configured:
        return EmailSendResult(
            status="Mock Sent",
            provider="mock",
            provider_message_id=f"mock-{make_msgid(domain='careflow.local').strip('<>')}",
            error_message=reason,
            sent_at=now,
        )

    message_id = make_msgid(domain="careflow-md.local")
    message = EmailMessage()
    message["From"] = formataddr((settings.smtp_from_name, settings.smtp_from_email))
    message["To"] = recipient_email
    message["Subject"] = subject
    message["Message-ID"] = message_id
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username and settings.smtp_password:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
        return EmailSendResult(
            status="Sent",
            provider="smtp",
            provider_message_id=message_id.strip("<>"),
            sent_at=now,
        )
    except Exception as exc:  # noqa: BLE001 - store safe operational message, never credentials
        return EmailSendResult(
            status="Failed",
            provider="smtp",
            error_message=str(exc),
            sent_at=None,
        )


def send_test_email(recipient_email: str, subject: str, body: str) -> EmailSendResult:
    settings = get_settings()
    if not settings.email_enabled:
        return EmailSendResult(status="Failed", provider="smtp", error_message="EMAIL_ENABLED must be true for test email endpoint")
    if not settings.smtp_configured:
        return EmailSendResult(status="Failed", provider="smtp", error_message="SMTP settings are incomplete")
    return send_patient_email(recipient_email, subject, body)
