# app/mailer.py
import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", "no-reply@example.com")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "https://example.com")

def build_invite_email(to_email: str, invite_token: str):
    # Link the user will click (frontend page can POST to /accept-invite)
    accept_url = f"{FRONTEND_BASE_URL}/accept-invite?email={to_email}&token={invite_token}"

    subject = "You’re invited to L&D SaaS"
    html = f"""
    <p>Hi,</p>
    <p>You’ve been invited to L&D SaaS. Click the button below to set your password and activate your account.</p>
    <p><a href="{accept_url}" style="background:#0ea5e9;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none;">Accept Invitation</a></p>
    <p>Or copy this link:<br>{accept_url}</p>
    <p>This link expires in 48 hours.</p>
    """
    text = f"""You’ve been invited to L&D SaaS.
Open this link to accept (expires in 48h):
{accept_url}
"""
    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(text)
    msg.add_alternative(html, subtype="html")
    return msg

def send_email(msg: EmailMessage):
    if not (SMTP_HOST and SMTP_PORT and SMTP_USER and SMTP_PASS):
        # Don’t crash the app if SMTP is not configured
        print("WARN: SMTP not configured; skipping send.")
        return
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)
