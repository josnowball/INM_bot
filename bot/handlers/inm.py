"""
INM appointment booking conversation — trilingual (EN/ZH/ES).
"""

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
    """Build procedure selection keyboard."""
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
    """Build office selection keyboard."""
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
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)

    proc_key = context.user_data.get("inm_procedure")
    office_key = context.user_data.get("inm_office")
    procedure = proc_name(INM_PROCEDURES, proc_key, lang)
    office = proc_name(INM_OFFICES, office_key, lang)

    await query.edit_message_text(t("inm_booking_progress", lang), parse_mode="Markdown")

    # TODO: Call the FastAPI booking endpoint via httpx
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=t("inm_booking_done", lang).format(procedure=procedure, office=office),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


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
