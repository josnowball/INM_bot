"""
/start, /help, /lang, registration flow — trilingual (EN/ZH/ES).
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from .i18n import t, get_lang


# ── Registration conversation states ─────────────────────────────────
REG_EMAIL, REG_PASSWORD, REG_VERIFY, REG_NAME, REG_NATIONALITY, REG_BIRTHDATE, REG_PASSPORT, REG_PHONE = range(8)


# ── Language picker ──────────────────────────────────────────────────

LANG_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("English", callback_data="lang_en"),
        InlineKeyboardButton("中文", callback_data="lang_zh"),
        InlineKeyboardButton("Espanol", callback_data="lang_es"),
    ]
])


async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    await update.message.reply_text(t("pick_lang", lang), reply_markup=LANG_KEYBOARD)


async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.replace("lang_", "")
    context.user_data["lang"] = lang
    await query.edit_message_text(t("lang_set", lang))
    await _set_commands_for_user(context, lang, query.from_user.id)


async def _set_commands_for_user(context, lang: str, user_id: int):
    commands_by_lang = {
        "en": [
            BotCommand("start", "Main menu"),
            BotCommand("inm", "Book INM appointment"),
            BotCommand("sre", "Book SRE appointment"),
            BotCommand("lang", "Change language"),
            BotCommand("tip", "Tip the author"),
            BotCommand("help", "Help & commands"),
        ],
        "zh": [
            BotCommand("start", "主菜单"),
            BotCommand("inm", "预约 INM 移民局"),
            BotCommand("sre", "预约 SRE 护照/签证"),
            BotCommand("lang", "更改语言"),
            BotCommand("tip", "给作者打赏"),
            BotCommand("help", "帮助与命令"),
        ],
        "es": [
            BotCommand("start", "Menu principal"),
            BotCommand("inm", "Agendar cita INM"),
            BotCommand("sre", "Agendar cita SRE"),
            BotCommand("lang", "Cambiar idioma"),
            BotCommand("tip", "Propina al autor"),
            BotCommand("help", "Ayuda y comandos"),
        ],
    }
    cmds = commands_by_lang.get(lang, commands_by_lang["es"])
    try:
        from telegram import BotCommandScopeChat
        await context.bot.set_my_commands(cmds, scope=BotCommandScopeChat(chat_id=user_id))
    except Exception:
        await context.bot.set_my_commands(cmds)


# ── /start ───────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang")

    # Auto-login returning users
    if not context.user_data.get("auth_token"):
        api = context.bot_data.get("api")
        if api:
            try:
                chat_id = str(update.effective_chat.id)
                result = await api.login_by_telegram(chat_id)
                if result:
                    context.user_data["auth_token"] = result["access_token"]
            except Exception:
                pass

    if not lang:
        await update.message.reply_text(
            "🇲🇽 *CitaFacil*\n\n"
            "🌐 Choose your language / 请选择语言 / Elige tu idioma:",
            parse_mode="Markdown",
            reply_markup=LANG_KEYBOARD,
        )
        return

    has_account = bool(context.user_data.get("auth_token"))

    buttons = [
        [
            InlineKeyboardButton(t("btn_inm", lang), callback_data="inm_start"),
            InlineKeyboardButton(t("btn_sre", lang), callback_data="sre_start"),
        ],
    ]

    if has_account:
        buttons.append([
            InlineKeyboardButton(t("btn_profile", lang), callback_data="profile"),
            InlineKeyboardButton(t("btn_appointments", lang), callback_data="appointments"),
        ])
    else:
        buttons.append([
            InlineKeyboardButton(t("btn_register", lang), callback_data="register_start"),
        ])

    buttons.append([
        InlineKeyboardButton(t("btn_lang", lang), callback_data="show_lang_picker"),
    ])

    await update.message.reply_text(
        t("welcome", lang),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def show_lang_picker_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)
    await query.edit_message_text(t("pick_lang", lang), reply_markup=LANG_KEYBOARD)


# ── /help ────────────────────────────────────────────────────────────

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    await update.message.reply_text(t("help", lang), parse_mode="Markdown")


# ── Profile (shows real data from API) ───────────────────────────────

async def profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)
    token = context.user_data.get("auth_token")
    api = context.bot_data.get("api")

    if not token or not api:
        await query.edit_message_text(t("need_account", lang), parse_mode="Markdown")
        return

    try:
        profile = await api.get_profile(token)
        pct = profile.get("completion_pct", 0)
        name = profile.get("first_name") or "—"
        nationality = profile.get("nationality") or "—"
        passport = profile.get("passport_number") or "—"
        phone = profile.get("phone") or "—"

        text = (
            f"👤 *Profile* ({pct}% complete)\n\n"
            f"*Name:* {name} {profile.get('last_name', '')}\n"
            f"*Nationality:* {nationality}\n"
            f"*Passport:* {passport}\n"
            f"*Phone:* {phone}\n\n"
            f"Use the website to edit your full profile."
        )
        await query.edit_message_text(text, parse_mode="Markdown")
    except Exception as e:
        await query.edit_message_text(f"Error loading profile: {e}")


# ── Appointments (shows real data from API) ──────────────────────────

async def appointments_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)
    token = context.user_data.get("auth_token")
    api = context.bot_data.get("api")

    if not token or not api:
        await query.edit_message_text(t("need_account", lang), parse_mode="Markdown")
        return

    try:
        appts = await api.list_appointments(token)
        if not appts:
            await query.edit_message_text(t("appointments", lang), parse_mode="Markdown")
            return

        status_emoji = {
            "pending": "⏳", "in_progress": "🔄",
            "booked": "✅", "failed": "❌",
        }
        lines = ["📅 *Your Appointments*\n"]
        for a in appts[:10]:
            emoji = status_emoji.get(a["status"], "❓")
            date = a.get("appointment_date") or "TBD"
            code = a.get("confirmation_code")
            code_str = f" | `{code}`" if code else ""
            lines.append(
                f"{emoji} {a['service'].upper()} — {a['procedure_type']}\n"
                f"    {date}{code_str}"
            )

        await query.edit_message_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await query.edit_message_text(f"Error loading appointments: {e}")


# ── Registration Conversation ────────────────────────────────────────

async def reg_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)

    if context.user_data.get("auth_token"):
        await query.edit_message_text(t("already_registered", lang), parse_mode="Markdown")
        return ConversationHandler.END

    await query.edit_message_text(t("reg_start", lang), parse_mode="Markdown")
    return REG_EMAIL


async def reg_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    email = update.message.text.strip()

    if "@" not in email:
        await update.message.reply_text("Please enter a valid email address.")
        return REG_EMAIL

    context.user_data["reg_email"] = email
    await update.message.reply_text(t("reg_password", lang), parse_mode="Markdown")
    return REG_PASSWORD


async def reg_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    password = update.message.text.strip()

    # Delete the password message
    try:
        await update.message.delete()
    except Exception:
        pass

    if len(password) < 8:
        await update.message.reply_text("Password must be at least 8 characters. Try again:")
        return REG_PASSWORD

    context.user_data["reg_password"] = password
    api = context.bot_data.get("api")
    email = context.user_data["reg_email"]
    chat_id = str(update.effective_chat.id)

    try:
        result = await api.register(
            email=email,
            password=password,
            telegram_chat_id=chat_id,
        )
        context.user_data["auth_token"] = result["access_token"]
        # Clear password from memory
        context.user_data.pop("reg_password", None)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=t("reg_verify", lang).format(email=email),
            parse_mode="Markdown",
        )
        return REG_VERIFY
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            error_msg = "Email already registered. Use /start to login."
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=t("reg_error", lang).format(error=error_msg),
            parse_mode="Markdown",
        )
        return ConversationHandler.END


async def reg_verify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    code = update.message.text.strip()
    token = context.user_data.get("auth_token")
    api = context.bot_data.get("api")

    try:
        await api.verify_email(token, code)
        await update.message.reply_text(t("reg_profile_name", lang), parse_mode="Markdown")
        return REG_NAME
    except Exception:
        await update.message.reply_text("Invalid code. Please check your email and try again:")
        return REG_VERIFY


async def reg_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    full_name = update.message.text.strip()
    parts = full_name.split(maxsplit=1)
    context.user_data["profile_first_name"] = parts[0]
    context.user_data["profile_last_name"] = parts[1] if len(parts) > 1 else ""

    await update.message.reply_text(t("reg_profile_nationality", lang), parse_mode="Markdown")
    return REG_NATIONALITY


async def reg_nationality(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    context.user_data["profile_nationality"] = update.message.text.strip()
    await update.message.reply_text(t("reg_profile_birthdate", lang), parse_mode="Markdown")
    return REG_BIRTHDATE


async def reg_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    context.user_data["profile_birth_date"] = update.message.text.strip()
    await update.message.reply_text(t("reg_profile_passport", lang), parse_mode="Markdown")
    return REG_PASSPORT


async def reg_passport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    context.user_data["profile_passport"] = update.message.text.strip()
    await update.message.reply_text(t("reg_profile_phone", lang), parse_mode="Markdown")
    return REG_PHONE


async def reg_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    phone = update.message.text.strip()
    token = context.user_data.get("auth_token")
    api = context.bot_data.get("api")

    # Save all profile data
    try:
        await api.update_profile(token, {
            "first_name": context.user_data.get("profile_first_name", ""),
            "last_name": context.user_data.get("profile_last_name", ""),
            "nationality": context.user_data.get("profile_nationality", ""),
            "birth_date": context.user_data.get("profile_birth_date", ""),
            "passport_number": context.user_data.get("profile_passport", ""),
            "phone": phone,
        })
    except Exception as e:
        await update.message.reply_text(f"Profile save error: {e}")

    # Cleanup temp data
    for k in ["profile_first_name", "profile_last_name", "profile_nationality",
              "profile_birth_date", "profile_passport", "reg_email"]:
        context.user_data.pop(k, None)

    await update.message.reply_text(t("reg_done", lang), parse_mode="Markdown")
    return ConversationHandler.END


async def reg_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(context)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(t("cancelled", lang))
    else:
        await update.message.reply_text(t("cancelled", lang))
    return ConversationHandler.END


def get_registration_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(reg_start, pattern="^register_start$"),
        ],
        states={
            REG_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_email)],
            REG_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_password)],
            REG_VERIFY: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_verify)],
            REG_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_name)],
            REG_NATIONALITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_nationality)],
            REG_BIRTHDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_birthdate)],
            REG_PASSPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_passport)],
            REG_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_phone)],
        },
        fallbacks=[
            CommandHandler("cancel", reg_cancel),
            CommandHandler("start", reg_cancel),
        ],
    )
