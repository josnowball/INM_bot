"""
SRE / MiConsulado appointment booking — trilingual, wired to API with slot selection.
"""

import asyncio
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

SELECT_PROCEDURE, ENTER_EMAIL, ENTER_PASSWORD, SELECT_OFFICE, CONFIRM, SELECT_SLOT = range(6)


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

    try:
        await update.message.delete()
    except Exception:
        pass

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=t("sre_credentials_received", lang),
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
    """User confirmed — check slots via API, then let them pick."""
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)

    proc_key = context.user_data.get("sre_procedure")
    office_key = context.user_data.get("sre_office")
    token = context.user_data.get("auth_token")
    api = context.bot_data.get("api")

    sre_email = context.user_data.get("sre_email", "")
    sre_password = context.user_data.get("sre_password", "")

    await query.edit_message_text(
        t("booking_checking_slots", lang), parse_mode="Markdown",
    )

    try:
        # Try to check available slots first
        result = await api.check_sre_slots(
            token=token,
            procedure_type=proc_key,
            mi_consulado_email=sre_email,
            mi_consulado_password=sre_password,
            preferred_office=office_key,
        )

        slots = result.get("slots", [])
        session_id = result.get("session_id", "")

        if not slots:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=t("no_slots", lang),
                parse_mode="Markdown",
            )
            _clear_credentials(context)
            return ConversationHandler.END

        # Store session_id for slot confirmation
        context.user_data["sre_session_id"] = session_id

        # Show slots as inline keyboard
        keyboard = []
        for slot in slots[:8]:  # Max 8 buttons
            label = f"{slot['date']} {slot['time']}"
            if slot.get("availability") == "high":
                label = f"🟢 {label}"
            elif slot.get("availability") == "medium":
                label = f"🟡 {label}"
            else:
                label = f"🟠 {label}"
            keyboard.append([InlineKeyboardButton(
                label,
                callback_data=f"sre_slot_{slot['date']}_{slot['time']}",
            )])
        keyboard.append([InlineKeyboardButton(t("btn_cancel", lang), callback_data="sre_cancel")])

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=t("slots_found", lang).format(count=len(slots)),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return SELECT_SLOT

    except Exception as e:
        error_str = str(e)
        # If slot checking isn't implemented yet, fall back to direct booking
        if "404" in error_str or "not found" in error_str.lower():
            return await _fallback_direct_book(context, query, lang, api, token,
                                                proc_key, office_key, sre_email, sre_password)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=t("booking_error", lang).format(error=error_str),
            parse_mode="Markdown",
        )
        _clear_credentials(context)
        return ConversationHandler.END


async def select_slot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User picked a time slot — confirm it."""
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)

    # Parse "sre_slot_2026-03-25_10:00"
    data = query.data.replace("sre_slot_", "")
    parts = data.rsplit("_", 1)
    date = parts[0] if parts else ""
    time = parts[1] if len(parts) > 1 else ""

    session_id = context.user_data.get("sre_session_id", "")
    token = context.user_data.get("auth_token")
    api = context.bot_data.get("api")

    await query.edit_message_text(
        t("slot_selected", lang).format(date=date, time=time),
        parse_mode="Markdown",
    )

    try:
        result = await api.confirm_sre_slot(token, session_id, date, time)
        appointment_id = result.get("id", "")

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=t("booking_submitted", lang),
            parse_mode="Markdown",
        )

        # Poll for final status
        if appointment_id:
            asyncio.create_task(
                _poll_and_notify(context, query.message.chat_id, api, token, appointment_id, lang)
            )

    except Exception as e:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=t("booking_error", lang).format(error=str(e)),
            parse_mode="Markdown",
        )

    _clear_credentials(context)
    return ConversationHandler.END


async def _fallback_direct_book(context, query, lang, api, token,
                                 proc_key, office_key, sre_email, sre_password):
    """Fallback: direct book without slot selection (if check-slots endpoint not ready)."""
    try:
        result = await api.book_sre(
            token=token,
            procedure_type=proc_key,
            mi_consulado_email=sre_email,
            mi_consulado_password=sre_password,
            preferred_office=office_key,
        )
        appointment_id = result["id"]

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=t("booking_submitted", lang),
            parse_mode="Markdown",
        )

        asyncio.create_task(
            _poll_and_notify(context, query.message.chat_id, api, token, appointment_id, lang)
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=t("booking_error", lang).format(error=str(e)),
            parse_mode="Markdown",
        )

    _clear_credentials(context)
    return ConversationHandler.END


async def _poll_and_notify(context, chat_id, api, token, appointment_id, lang):
    """Background polling for booking result."""
    try:
        result = await api.poll_appointment_status(token, appointment_id, max_wait=300, interval=10)

        if result["status"] == "booked":
            text = t("sre_booking_done", lang).format(
                procedure=result.get("procedure_type", ""),
                office=result.get("office_location", ""),
            )
            if result.get("confirmation_code"):
                text += f"\n\n*Confirmation:* `{result['confirmation_code']}`"
            if result.get("appointment_date"):
                text += f"\n*Date:* {result['appointment_date']}"
            if result.get("appointment_time"):
                text += f" at {result['appointment_time']}"
        elif result["status"] == "failed":
            text = t("booking_error", lang).format(error=result.get("error_message", "Unknown error"))
        else:
            text = t("booking_submitted", lang)

        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"Status check error: {e}")


def _clear_credentials(context):
    """Clear MiConsulado credentials from memory."""
    context.user_data.pop("sre_password", None)
    context.user_data.pop("sre_email", None)
    context.user_data.pop("sre_session_id", None)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    _clear_credentials(context)

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
            SELECT_SLOT: [
                CallbackQueryHandler(select_slot, pattern="^sre_slot_"),
                CallbackQueryHandler(cancel, pattern="^sre_cancel$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(cancel, pattern="^sre_cancel$"),
        ],
    )
