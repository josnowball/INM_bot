"""
CitaFácil Telegram Bot — entry point.

Usage:
    TELEGRAM_BOT_TOKEN=xxx python bot.py
"""

import os
import sys
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from handlers.start import start, help_command
from handlers.inm import get_inm_handler
from handlers.sre import get_sre_handler


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("ERROR: Set TELEGRAM_BOT_TOKEN environment variable")
        sys.exit(1)

    app = ApplicationBuilder().token(token).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Conversation handlers
    app.add_handler(get_inm_handler())
    app.add_handler(get_sre_handler())

    # Generic callback handler for menu buttons
    app.add_handler(CallbackQueryHandler(handle_menu_callback))

    print("Bot started. Polling...")
    app.run_polling()


async def handle_menu_callback(update, context):
    """Handle menu buttons that aren't part of a conversation."""
    query = update.callback_query
    data = query.data

    if data == "profile":
        await query.answer()
        await query.edit_message_text(
            "👤 *Your Profile*\n\n"
            "To manage your profile, visit the website or use these commands:\n"
            "• Your profile data is used to auto-fill appointment forms\n"
            "• Fill it in once, reuse for every booking\n\n"
            "🌐 Visit the website to complete your profile.",
            parse_mode="Markdown",
        )
    elif data == "appointments":
        await query.answer()
        await query.edit_message_text(
            "📅 *Your Appointments*\n\n"
            "No appointments yet.\n"
            "Use /inm or /sre to book one!",
            parse_mode="Markdown",
        )
    else:
        await query.answer("Unknown action")


if __name__ == "__main__":
    main()
