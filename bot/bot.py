"""
CitaFacil Telegram Bot — entry point.
Trilingual (EN/ZH/ES) with BotCommand menu and backend API integration.

Usage:
    TELEGRAM_BOT_TOKEN=xxx API_BASE_URL=http://localhost:8000 python bot.py
"""

import os
import sys
from telegram import BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from api_client import CitaFacilAPI
from handlers.start import (
    start,
    help_command,
    lang_command,
    lang_callback,
    show_lang_picker_callback,
    profile_callback,
    appointments_callback,
    get_registration_handler,
)
from handlers.inm import get_inm_handler
from handlers.sre import get_sre_handler
from handlers.captcha_handler import captcha_reply_handler
from handlers.tip import tip_command, tip_callback


async def post_init(application):
    """Set default command menu + init API client."""
    await application.bot.set_my_commands([
        BotCommand("start", "Menu principal"),
        BotCommand("inm", "Agendar cita INM"),
        BotCommand("sre", "Agendar cita SRE"),
        BotCommand("lang", "Cambiar idioma / Change language"),
        BotCommand("tip", "Tip the author / Propina"),
        BotCommand("help", "Ayuda / Help"),
    ])

    # Init API client and store in bot_data for all handlers
    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    application.bot_data["api"] = CitaFacilAPI(base_url=api_url)


async def post_shutdown(application):
    """Cleanup API client."""
    api = application.bot_data.get("api")
    if api:
        await api.close()


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("ERROR: Set TELEGRAM_BOT_TOKEN environment variable")
        sys.exit(1)

    app = (
        ApplicationBuilder()
        .token(token)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # ── Conversation handlers (must be added before generic callbacks) ──
    app.add_handler(get_registration_handler())
    app.add_handler(get_inm_handler())
    app.add_handler(get_sre_handler())

    # ── Commands ──
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("lang", lang_command))
    app.add_handler(CommandHandler("tip", tip_command))

    # ── Callback queries ──
    app.add_handler(CallbackQueryHandler(lang_callback, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(show_lang_picker_callback, pattern="^show_lang_picker$"))
    app.add_handler(CallbackQueryHandler(profile_callback, pattern="^profile$"))
    app.add_handler(CallbackQueryHandler(appointments_callback, pattern="^appointments$"))
    app.add_handler(CallbackQueryHandler(tip_callback, pattern="^tip_"))

    # ── CAPTCHA reply handler (catches text replies during booking) ──
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        captcha_reply_handler,
    ), group=1)  # group=1 so it doesn't interfere with conversation handlers

    print("CitaFacil bot started. Polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
