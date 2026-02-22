from __future__ import annotations

import json
import smtplib
from email.message import EmailMessage
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parents[1] / "email_log.jsonl"


def send_email(to: str, subject: str, body: str, smtp_host: str | None = None, smtp_port: int = 587,
               smtp_user: str | None = None, smtp_pass: str | None = None, from_addr: str | None = None):
    payload = {"to": to, "subject": subject, "body": body}

    if smtp_host and smtp_user and smtp_pass:
        msg = EmailMessage()
        msg["From"] = from_addr or smtp_user
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        payload["delivery"] = "smtp"
    else:
        # Local fallback for hackathon/demo environments without external email credentials.
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
        payload["delivery"] = "logged"

    return payload
