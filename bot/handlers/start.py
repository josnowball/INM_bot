"""
/start, /help, /lang handlers — trilingual (EN/ZH/ES).
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ContextTypes

from .i18n import t, get_lang


# ── Language picker ──────────────────────────────────────────────────

LANG_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("English", callback_data="lang_en"),
        InlineKeyboardButton("中文", callback_data="lang_zh"),
        InlineKeyboardButton("Espanol", callback_data="lang_es"),
    ]
])


async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show language picker."""
    lang = get_lang(context)
    await update.message.reply_text(
        t("pick_lang", lang),
        reply_markup=LANG_KEYBOARD,
    )


async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User tapped a language button."""
    query = update.callback_query
    await query.answer()

    lang = query.data.replace("lang_", "")  # "en", "zh", or "es"
    context.user_data["lang"] = lang

    await query.edit_message_text(t("lang_set", lang))

    # Update the command menu for this user's language
    await _set_commands_for_user(context, lang, query.from_user.id)


async def _set_commands_for_user(context, lang: str, user_id: int):
    """Set the BotCommand menu (☰ button) in the user's language."""
    commands_by_lang = {
        "en": [
            BotCommand("start", "Main menu"),
            BotCommand("inm", "Book INM appointment"),
            BotCommand("sre", "Book SRE appointment"),
            BotCommand("lang", "Change language"),
            BotCommand("help", "Help & commands"),
        ],
        "zh": [
            BotCommand("start", "主菜单"),
            BotCommand("inm", "预约 INM 移民局"),
            BotCommand("sre", "预约 SRE 护照/签证"),
            BotCommand("lang", "更改语言"),
            BotCommand("help", "帮助与命令"),
        ],
        "es": [
            BotCommand("start", "Menu principal"),
            BotCommand("inm", "Agendar cita INM"),
            BotCommand("sre", "Agendar cita SRE"),
            BotCommand("lang", "Cambiar idioma"),
            BotCommand("help", "Ayuda y comandos"),
        ],
    }
    cmds = commands_by_lang.get(lang, commands_by_lang["es"])

    # Set per-chat commands so each user sees their own language
    try:
        from telegram import BotCommandScopeChat
        await context.bot.set_my_commands(
            cmds,
            scope=BotCommandScopeChat(chat_id=user_id),
        )
    except Exception:
        # Fallback: set default commands
        await context.bot.set_my_commands(cmds)


# ── /start ───────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main menu — if no language set yet, show picker first."""
    lang = context.user_data.get("lang")

    if not lang:
        # First time user — show language picker
        await update.message.reply_text(
            "🇲🇽 *CitaFacil*\n\n"
            "🌐 Choose your language / 请选择语言 / Elige tu idioma:",
            parse_mode="Markdown",
            reply_markup=LANG_KEYBOARD,
        )
        return

    keyboard = [
        [
            InlineKeyboardButton(t("btn_inm", lang), callback_data="inm_start"),
            InlineKeyboardButton(t("btn_sre", lang), callback_data="sre_start"),
        ],
        [
            InlineKeyboardButton(t("btn_profile", lang), callback_data="profile"),
            InlineKeyboardButton(t("btn_appointments", lang), callback_data="appointments"),
        ],
        [
            InlineKeyboardButton(t("btn_lang", lang), callback_data="show_lang_picker"),
        ],
    ]

    await update.message.reply_text(
        t("welcome", lang),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_lang_picker_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline button to change language from the main menu."""
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)
    await query.edit_message_text(
        t("pick_lang", lang),
        reply_markup=LANG_KEYBOARD,
    )


# ── /help ────────────────────────────────────────────────────────────

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    await update.message.reply_text(t("help", lang), parse_mode="Markdown")


# ── Menu callbacks (profile, appointments) ───────────────────────────

async def profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)
    await query.edit_message_text(t("profile", lang), parse_mode="Markdown")


async def appointments_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)
    await query.edit_message_text(t("appointments", lang), parse_mode="Markdown")
