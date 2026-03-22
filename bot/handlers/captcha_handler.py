"""
CAPTCHA reply handler — catches user's text replies when a CAPTCHA is pending.
Works with the backend's captcha_service via API.
"""

from telegram import Update
from telegram.ext import ContextTypes


async def captcha_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    If there's a pending CAPTCHA for this user, forward their reply as the solution.
    This handler runs in group=1 so it doesn't block conversation handlers.
    """
    if not update.message or not update.message.text:
        return

    chat_id = str(update.message.chat_id)
    token = context.user_data.get("auth_token")
    if not token:
        return

    api = context.bot_data.get("api")
    if not api:
        return

    # Check if there's a pending CAPTCHA for this user
    try:
        pending = await api.get_pending_captcha(token)
        if pending:
            solution = update.message.text.strip()
            await api.submit_captcha_solution(token, pending["captcha_id"], solution)
            await update.message.reply_text("✅ CAPTCHA answer sent. Processing...")
    except Exception:
        # No pending CAPTCHA or API error — ignore silently
        pass
