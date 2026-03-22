"""
SRE / MiConsulado appointment booking conversation flow via Telegram.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

SELECT_PROCEDURE, ENTER_EMAIL, ENTER_PASSWORD, SELECT_OFFICE, CONFIRM = range(5)

SRE_PROCEDURES = {
    "pasaporte_primera_vez": "Pasaporte — Primera Vez",
    "pasaporte_renovacion": "Pasaporte — Renovación",
    "visa_canje": "Canje de Visa",
    "carta_naturalizacion": "Carta de Naturalización",
    "apostilla": "Apostilla",
    "legalizacion": "Legalización de Documentos",
}

SRE_OFFICES = {
    "cdmx_tlatelolco": "CDMX — Tlatelolco",
    "cdmx_polanco": "CDMX — Polanco",
    "guadalajara": "Guadalajara",
    "monterrey": "Monterrey",
    "puebla": "Puebla",
    "cancun": "Cancún",
    "merida": "Mérida",
    "tijuana": "Tijuana",
    "queretaro": "Querétaro",
}


async def sre_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = []
    row = []
    for key, name in SRE_PROCEDURES.items():
        row.append(InlineKeyboardButton(name, callback_data=f"sre_proc_{key}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="sre_cancel")])

    text = (
        "🛂 *SRE / MiConsulado Appointment*\n\n"
        "Select the type of service you need:"
    )

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
        )
    return SELECT_PROCEDURE


async def select_procedure(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    procedure_key = query.data.replace("sre_proc_", "")
    context.user_data["sre_procedure"] = procedure_key

    await query.edit_message_text(
        "🔐 *MiConsulado Login*\n\n"
        "Please enter your MiConsulado email address.\n\n"
        "_We do NOT store your credentials. They are used once for this booking and immediately discarded._",
        parse_mode="Markdown",
    )
    return ENTER_EMAIL


async def enter_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["sre_email"] = update.message.text.strip()

    await update.message.reply_text(
        "Now enter your MiConsulado password.\n\n"
        "🔒 _Your password is used once and never stored. "
        "Delete this message after sending if you'd like._",
        parse_mode="Markdown",
    )
    return ENTER_PASSWORD


async def enter_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["sre_password"] = update.message.text.strip()

    # Try to delete the password message for security
    try:
        await update.message.delete()
    except Exception:
        pass

    keyboard = []
    row = []
    for key, name in SRE_OFFICES.items():
        row.append(InlineKeyboardButton(name, callback_data=f"sre_office_{key}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="sre_cancel")])

    await update.message.reply_text(
        "✅ Credentials received (not stored).\n\n"
        "Select your preferred SRE office:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return SELECT_OFFICE


async def select_office(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    office_key = query.data.replace("sre_office_", "")
    context.user_data["sre_office"] = office_key

    proc_name = SRE_PROCEDURES.get(context.user_data["sre_procedure"], "")
    office_name = SRE_OFFICES.get(office_key, "")

    keyboard = [
        [
            InlineKeyboardButton("✅ Book Now", callback_data="sre_confirm"),
            InlineKeyboardButton("❌ Cancel", callback_data="sre_cancel"),
        ]
    ]

    await query.edit_message_text(
        f"🛂 *Confirm SRE Appointment*\n\n"
        f"*Service:* {proc_name}\n"
        f"*Office:* {office_name}\n"
        f"*MiConsulado:* {context.user_data.get('sre_email', '')}\n\n"
        f"Ready to book?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CONFIRM


async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    proc = context.user_data.get("sre_procedure")
    office = context.user_data.get("sre_office")

    await query.edit_message_text(
        "⏳ *Booking in progress...*\n\n"
        "Logging into MiConsulado and searching for available slots.\n"
        "This may take 1-2 minutes.",
        parse_mode="Markdown",
    )

    # TODO: Call the FastAPI SRE booking endpoint
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=(
            "🛂 *Booking submitted!*\n\n"
            f"*Service:* {SRE_PROCEDURES.get(proc, proc)}\n"
            f"*Office:* {SRE_OFFICES.get(office, office)}\n"
            f"*Status:* Pending\n\n"
            "We'll notify you when the appointment is confirmed.\n"
            "Check /appointments for status."
        ),
        parse_mode="Markdown",
    )

    # Clear credentials from memory
    context.user_data.pop("sre_password", None)
    context.user_data.pop("sre_email", None)

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Clear any stored credentials
    context.user_data.pop("sre_password", None)
    context.user_data.pop("sre_email", None)

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Booking cancelled. Use /start for the menu.")
    else:
        await update.message.reply_text("Booking cancelled. Use /start for the menu.")
    return ConversationHandler.END


def get_sre_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CommandHandler("sre", sre_start),
            CallbackQueryHandler(sre_start, pattern="^sre_start$"),
        ],
        states={
            SELECT_PROCEDURE: [
                CallbackQueryHandler(select_procedure, pattern="^sre_proc_"),
                CallbackQueryHandler(cancel, pattern="^sre_cancel$"),
            ],
            ENTER_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_email),
            ],
            ENTER_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_password),
            ],
            SELECT_OFFICE: [
                CallbackQueryHandler(select_office, pattern="^sre_office_"),
                CallbackQueryHandler(cancel, pattern="^sre_cancel$"),
            ],
            CONFIRM: [
                CallbackQueryHandler(confirm_booking, pattern="^sre_confirm$"),
                CallbackQueryHandler(cancel, pattern="^sre_cancel$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(cancel, pattern="^sre_cancel$"),
        ],
    )
