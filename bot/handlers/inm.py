"""
INM appointment booking conversation flow via Telegram.
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

# Conversation states
SELECT_PROCEDURE, SELECT_OFFICE, CONFIRM = range(3)

INM_PROCEDURES = {
    "residencia_temporal": "Residencia Temporal",
    "residencia_permanente": "Residencia Permanente",
    "cambio_condicion": "Cambio de Condición",
    "renovacion_residencia": "Renovación de Residencia",
    "permiso_salida_regreso": "Permiso de Salida y Regreso",
    "regularizacion": "Regularización Migratoria",
}

INM_OFFICES = {
    "cdmx_polanco": "CDMX — Polanco",
    "cdmx_centro": "CDMX — Centro",
    "guadalajara": "Guadalajara",
    "monterrey": "Monterrey",
    "cancun": "Cancún",
    "merida": "Mérida",
    "puebla": "Puebla",
    "tijuana": "Tijuana",
    "queretaro": "Querétaro",
    "playa_del_carmen": "Playa del Carmen",
    "san_miguel_allende": "San Miguel de Allende",
    "puerto_vallarta": "Puerto Vallarta",
}


async def inm_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point — show procedure selection."""
    keyboard = []
    row = []
    for key, name in INM_PROCEDURES.items():
        row.append(InlineKeyboardButton(name, callback_data=f"inm_proc_{key}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="inm_cancel")])

    text = (
        "📋 *INM Appointment Booking*\n\n"
        "Select the type of procedure you need:"
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
    """User selected a procedure — now pick office."""
    query = update.callback_query
    await query.answer()

    procedure_key = query.data.replace("inm_proc_", "")
    context.user_data["inm_procedure"] = procedure_key

    keyboard = []
    row = []
    for key, name in INM_OFFICES.items():
        row.append(InlineKeyboardButton(name, callback_data=f"inm_office_{key}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="inm_cancel")])

    proc_name = INM_PROCEDURES.get(procedure_key, procedure_key)
    await query.edit_message_text(
        f"📋 *{proc_name}*\n\nSelect your preferred INM office:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return SELECT_OFFICE


async def select_office(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User selected office — show confirmation."""
    query = update.callback_query
    await query.answer()

    office_key = query.data.replace("inm_office_", "")
    context.user_data["inm_office"] = office_key

    proc_name = INM_PROCEDURES.get(context.user_data["inm_procedure"], "")
    office_name = INM_OFFICES.get(office_key, "")

    keyboard = [
        [
            InlineKeyboardButton("✅ Book Now", callback_data="inm_confirm"),
            InlineKeyboardButton("❌ Cancel", callback_data="inm_cancel"),
        ]
    ]

    await query.edit_message_text(
        f"📋 *Confirm INM Appointment*\n\n"
        f"*Procedure:* {proc_name}\n"
        f"*Office:* {office_name}\n\n"
        f"We'll use your saved profile data to fill out the solicitud.\n"
        f"Make sure your profile is complete before proceeding.\n\n"
        f"Ready to book?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CONFIRM


async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User confirmed — initiate booking via API."""
    query = update.callback_query
    await query.answer()

    proc = context.user_data.get("inm_procedure")
    office = context.user_data.get("inm_office")

    await query.edit_message_text(
        f"⏳ *Booking in progress...*\n\n"
        f"We're filling out your solicitud and looking for available slots.\n"
        f"This may take 1-2 minutes. We'll notify you when done.",
        parse_mode="Markdown",
    )

    # TODO: Call the FastAPI booking endpoint here
    # For now, send a placeholder response
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=(
            "📋 *Booking submitted!*\n\n"
            f"*Procedure:* {INM_PROCEDURES.get(proc, proc)}\n"
            f"*Office:* {INM_OFFICES.get(office, office)}\n"
            f"*Status:* Pending\n\n"
            "We'll send you a confirmation once the appointment is secured.\n"
            "Check /appointments to see the status."
        ),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Booking cancelled. Use /start to go back to the menu.")
    return ConversationHandler.END


def get_inm_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CommandHandler("inm", inm_start),
            CallbackQueryHandler(inm_start, pattern="^inm_start$"),
        ],
        states={
            SELECT_PROCEDURE: [
                CallbackQueryHandler(select_procedure, pattern="^inm_proc_"),
                CallbackQueryHandler(cancel, pattern="^inm_cancel$"),
            ],
            SELECT_OFFICE: [
                CallbackQueryHandler(select_office, pattern="^inm_office_"),
                CallbackQueryHandler(cancel, pattern="^inm_cancel$"),
            ],
            CONFIRM: [
                CallbackQueryHandler(confirm_booking, pattern="^inm_confirm$"),
                CallbackQueryHandler(cancel, pattern="^inm_cancel$"),
            ],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^inm_cancel$")],
    )
