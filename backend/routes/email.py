from __future__ import annotations

import os
from fastapi import APIRouter
from pydantic import BaseModel

from backend.tools.send_email import send_email

router = APIRouter(prefix="/api", tags=["email"])


class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str


@router.post("/email")
def email(req: EmailRequest):
    res = send_email(
        to=req.to,
        subject=req.subject,
        body=req.body,
        smtp_host=os.getenv("SMTP_HOST"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER"),
        smtp_pass=os.getenv("SMTP_PASS"),
        from_addr=os.getenv("SMTP_FROM"),
    )
    return {"ok": True, "result": res}
