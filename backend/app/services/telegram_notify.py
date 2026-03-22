"""
Send Telegram notifications directly from the backend.
Used by background tasks to notify users when bookings complete/fail.
"""

import httpx
from app.config import get_settings


MESSAGES = {
    "booked": {
        "en": (
            "✅ *Appointment Booked!*\n\n"
            "*Service:* {service}\n"
            "*Procedure:* {procedure}\n"
            "*Date:* {date}\n"
            "*Time:* {time}\n"
            "*Office:* {office}\n"
            "*Confirmation:* `{code}`\n\n"
            "Save your confirmation code. Good luck!"
        ),
        "zh": (
            "✅ *预约成功！*\n\n"
            "*服务：* {service}\n"
            "*事项：* {procedure}\n"
            "*日期：* {date}\n"
            "*时间：* {time}\n"
            "*地点：* {office}\n"
            "*确认码：* `{code}`\n\n"
            "请保存确认码。祝顺利！"
        ),
        "es": (
            "✅ *Cita Agendada!*\n\n"
            "*Servicio:* {service}\n"
            "*Tramite:* {procedure}\n"
            "*Fecha:* {date}\n"
            "*Hora:* {time}\n"
            "*Oficina:* {office}\n"
            "*Confirmacion:* `{code}`\n\n"
            "Guarda tu codigo de confirmacion. Buena suerte!"
        ),
    },
    "failed": {
        "en": "❌ *Booking Failed*\n\n*Reason:* {error}\n\nPlease try again with /inm or /sre.",
        "zh": "❌ *预约失败*\n\n*原因：* {error}\n\n请使用 /inm 或 /sre 重试。",
        "es": "❌ *Cita Fallida*\n\n*Razon:* {error}\n\nIntenta de nuevo con /inm o /sre.",
    },
}


async def send_telegram_message(chat_id: str, text: str, parse_mode: str = "Markdown"):
    """Send a message via Telegram Bot API."""
    settings = get_settings()
    token = settings.telegram_bot_token
    if not token:
        print(f"[notify] No bot token — would send to {chat_id}: {text[:80]}...")
        return

    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode,
                },
            )
        except Exception as e:
            print(f"[notify] Failed to send Telegram message: {e}")


async def notify_booking_result(chat_id: str, appointment: dict, lang: str = "es"):
    """Send booking result notification to user's Telegram."""
    status = appointment.get("status", "failed")
    templates = MESSAGES.get(status, MESSAGES["failed"])
    template = templates.get(lang, templates.get("es", ""))

    if status == "booked":
        text = template.format(
            service=appointment.get("service", "").upper(),
            procedure=appointment.get("procedure_type", ""),
            date=appointment.get("appointment_date", "TBD"),
            time=appointment.get("appointment_time", "TBD"),
            office=appointment.get("office_location", "TBD"),
            code=appointment.get("confirmation_code", "N/A"),
        )
    else:
        text = template.format(
            error=appointment.get("error_message", "Unknown error"),
        )

    await send_telegram_message(chat_id, text)
