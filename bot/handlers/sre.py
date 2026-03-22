"""
SRE / MiConsulado appointment booking conversation — trilingual (EN/ZH/ES).
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

from .i18n import (
    t, get_lang, proc_name,
    SRE_PROCEDURES, SRE_OFFICES,
)

SELECT_PROCEDURE, ENTER_EMAIL, ENTER_PASSWORD, SELECT_OFFICE, CONFIRM = range(5)


def _procedure_keyboard(lang: str):
    keyboard = []
    row = []
    for key in SRE_PROCEDURES:
        label = proc_name(SRE_PROCEDURES, key, lang)
        row.append(InlineKeyboardButton(label, callback_data=f"sre_proc_{key}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(t("btn_cancel", lang), callback_data="sre_cancel")])
    return InlineKeyboardMarkup(keyboard)


def _office_keyboard(lang: str):
    keyboard = []
    row = []
    for key in SRE_OFFICES:
        label = proc_name(SRE_OFFICES, key, lang)
        row.append(InlineKeyboardButton(label, callback_data=f"sre_office_{key}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(t("btn_cancel", lang), callback_data="sre_cancel")])
    return InlineKeyboardMarkup(keyboard)


async def sre_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    text = t("sre_title", lang)
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

    procedure_key = query.data.replace("sre_proc_", "")
    context.user_data["sre_procedure"] = procedure_key

    await query.edit_message_text(t("sre_enter_email", lang), parse_mode="Markdown")
    return ENTER_EMAIL


async def enter_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    context.user_data["sre_email"] = update.message.text.strip()

    await update.message.reply_text(t("sre_enter_password", lang), parse_mode="Markdown")
    return ENTER_PASSWORD


async def enter_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    context.user_data["sre_password"] = update.message.text.strip()

    # Delete the password message for security
    try:
        await update.message.delete()
    except Exception:
        pass

    await update.message.reply_text(
        t("sre_credentials_received", lang),
        parse_mode="Markdown",
        reply_markup=_office_keyboard(lang),
    )
    return SELECT_OFFICE


async def select_office(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)

    office_key = query.data.replace("sre_office_", "")
    context.user_data["sre_office"] = office_key

    procedure = proc_name(SRE_PROCEDURES, context.user_data["sre_procedure"], lang)
    office = proc_name(SRE_OFFICES, office_key, lang)
    email = context.user_data.get("sre_email", "")

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("btn_book_now", lang), callback_data="sre_confirm"),
            InlineKeyboardButton(t("btn_cancel", lang), callback_data="sre_cancel"),
        ]
    ])

    text = t("sre_confirm", lang).format(procedure=procedure, office=office, email=email)
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
    return CONFIRM


async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)

    proc_key = context.user_data.get("sre_procedure")
    office_key = context.user_data.get("sre_office")
    procedure = proc_name(SRE_PROCEDURES, proc_key, lang)
    office = proc_name(SRE_OFFICES, office_key, lang)

    await query.edit_message_text(t("sre_booking_progress", lang), parse_mode="Markdown")

    # TODO: Call the FastAPI SRE booking endpoint via httpx
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=t("sre_booking_done", lang).format(procedure=procedure, office=office),
        parse_mode="Markdown",
    )

    # Clear credentials from memory immediately
    context.user_data.pop("sre_password", None)
    context.user_data.pop("sre_email", None)

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    # Clear any stored credentials
    context.user_data.pop("sre_password", None)
    context.user_data.pop("sre_email", None)

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(t("cancelled", lang))
    else:
        await update.message.reply_text(t("cancelled", lang))
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
