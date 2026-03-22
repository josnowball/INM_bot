import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import get_settings


def generate_code(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


async def send_verification_email(to_email: str, code: str) -> bool:
    settings = get_settings()
    if not settings.smtp_user:
        # Dev mode — just print
        print(f"[DEV] Verification code for {to_email}: {code}")
        return True

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Verify your email — CitaFácil"
    msg["From"] = settings.smtp_user
    msg["To"] = to_email

    html = f"""
    <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto; padding: 32px;">
        <h2 style="color: #1a1a2e;">Verify your email</h2>
        <p>Your verification code is:</p>
        <div style="background: #f0f0f5; border-radius: 8px; padding: 20px; text-align: center;
                    font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #1a1a2e;">
            {code}
        </div>
        <p style="color: #666; font-size: 14px; margin-top: 16px;">
            This code expires in 15 minutes. If you didn't request this, ignore this email.
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
        <p style="color: #999; font-size: 12px;">
            CitaFácil — One-click appointment booking for INM &amp; SRE
        </p>
    </div>
    """
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_user, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False
