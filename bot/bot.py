"""
CitaFacil Telegram Bot — entry point.
Trilingual (EN/ZH/ES) with BotCommand menu.

Usage:
    TELEGRAM_BOT_TOKEN=xxx python bot.py
"""

import os
import sys
from telegram import BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
)

from handlers.start import (
    start,
    help_command,
    lang_command,
    lang_callback,
    show_lang_picker_callback,
    profile_callback,
    appointments_callback,
)
from handlers.inm import get_inm_handler
from handlers.sre import get_sre_handler


async def post_init(application):
    """Set default command menu (Spanish) on startup.
    Per-user language menus are set when they pick a language."""
    await application.bot.set_my_commands([
        BotCommand("start", "Menu principal"),
        BotCommand("inm", "Agendar cita INM"),
        BotCommand("sre", "Agendar cita SRE"),
        BotCommand("lang", "Cambiar idioma / Change language / 更改语言"),
        BotCommand("help", "Ayuda / Help / 帮助"),
    ])


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("ERROR: Set TELEGRAM_BOT_TOKEN environment variable")
        sys.exit(1)

    app = (
        ApplicationBuilder()
        .token(token)
        .post_init(post_init)
        .build()
    )

    # ── Conversation handlers (must be added before generic callbacks) ──
    app.add_handler(get_inm_handler())
    app.add_handler(get_sre_handler())

    # ── Commands ──
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("lang", lang_command))

    # ── Callback queries (language picker, menu buttons) ──
    app.add_handler(CallbackQueryHandler(lang_callback, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(show_lang_picker_callback, pattern="^show_lang_picker$"))
    app.add_handler(CallbackQueryHandler(profile_callback, pattern="^profile$"))
    app.add_handler(CallbackQueryHandler(appointments_callback, pattern="^appointments$"))

    print("CitaFacil bot started. Polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
