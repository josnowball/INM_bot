"""
INM appointment booking conversation — trilingual, wired to backend API.
"""

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
)

from .i18n import (
    t, get_lang, proc_name,
    INM_PROCEDURES, INM_OFFICES,
)

SELECT_PROCEDURE, SELECT_OFFICE, CONFIRM = range(3)


def _procedure_keyboard(lang: str):
    keyboard = []
    row = []
    for key in INM_PROCEDURES:
        label = proc_name(INM_PROCEDURES, key, lang)
        row.append(InlineKeyboardButton(label, callback_data=f"inm_proc_{key}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(t("btn_cancel", lang), callback_data="inm_cancel")])
    return InlineKeyboardMarkup(keyboard)


def _office_keyboard(lang: str):
    keyboard = []
    row = []
    for key in INM_OFFICES:
        label = proc_name(INM_OFFICES, key, lang)
        row.append(InlineKeyboardButton(label, callback_data=f"inm_office_{key}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(t("btn_cancel", lang), callback_data="inm_cancel")])
    return InlineKeyboardMarkup(keyboard)


async def inm_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)

    # Check if user has account
    if not context.user_data.get("auth_token"):
        text = t("need_account", lang)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("btn_register", lang), callback_data="register_start")]
        ])
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        else:
            await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
        return ConversationHandler.END

    text = t("inm_title", lang)
    kb = _procedure_keyboard(lang)

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    return SELECT_PROCEDURE


async def select_procedure(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)

    procedure_key = query.data.replace("inm_proc_", "")
    context.user_data["inm_procedure"] = procedure_key

    name = proc_name(INM_PROCEDURES, procedure_key, lang)
    text = f"📋 *{name}*\n\n{t('inm_select_office', lang)}"

    await query.edit_message_text(
        text, parse_mode="Markdown", reply_markup=_office_keyboard(lang),
    )
    return SELECT_OFFICE


async def select_office(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)

    office_key = query.data.replace("inm_office_", "")
    context.user_data["inm_office"] = office_key

    procedure = proc_name(INM_PROCEDURES, context.user_data["inm_procedure"], lang)
    office = proc_name(INM_OFFICES, office_key, lang)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("btn_book_now", lang), callback_data="inm_confirm"),
            InlineKeyboardButton(t("btn_cancel", lang), callback_data="inm_cancel"),
        ]
    ])

    text = t("inm_confirm", lang).format(procedure=procedure, office=office)
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
    return CONFIRM


async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User confirmed — call backend API to book INM appointment."""
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)

    proc_key = context.user_data.get("inm_procedure")
    office_key = context.user_data.get("inm_office")
    procedure = proc_name(INM_PROCEDURES, proc_key, lang)
    office = proc_name(INM_OFFICES, office_key, lang)
    token = context.user_data.get("auth_token")
    api = context.bot_data.get("api")

    await query.edit_message_text(t("inm_booking_progress", lang), parse_mode="Markdown")

    try:
        # Submit booking to backend
        result = await api.book_inm(
            token=token,
            procedure_type=proc_key,
            preferred_office=office_key,
        )
        appointment_id = result["id"]

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=t("booking_submitted", lang),
            parse_mode="Markdown",
        )

        # Start background polling for status
        asyncio.create_task(
            _poll_and_notify(context, query.message.chat_id, api, token, appointment_id, lang)
        )

    except Exception as e:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=t("booking_error", lang).format(error=str(e)),
            parse_mode="Markdown",
        )

    return ConversationHandler.END


async def _poll_and_notify(context, chat_id, api, token, appointment_id, lang):
    """Background task: poll appointment status and notify user."""
    try:
        result = await api.poll_appointment_status(token, appointment_id, max_wait=300, interval=10)

        if result["status"] == "booked":
            text = t("inm_booking_done", lang).format(
                procedure=result.get("procedure_type", ""),
                office=result.get("office_location", ""),
            )
            if result.get("confirmation_code"):
                text += f"\n\n*Confirmation:* `{result['confirmation_code']}`"
        elif result["status"] == "failed":
            text = t("booking_error", lang).format(error=result.get("error_message", "Unknown error"))
        else:
            text = t("booking_submitted", lang)  # Still processing

        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Error checking booking status: {e}",
        )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(t("cancelled", lang))
    else:
        await update.message.reply_text(t("cancelled", lang))
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
