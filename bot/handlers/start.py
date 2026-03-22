from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


WELCOME_TEXT = """
🇲🇽 *CitaFácil — Appointment Booking Bot*

Skip the headache of booking government appointments.
We handle the tedious form-filling so you don't have to.

*Available services:*
📋 *INM* — Immigration appointments (residencia, cambio de condición, etc.)
🛂 *SRE* — Passport & visa appointments via MiConsulado

*How it works:*
1️⃣ Create your profile (fill in once, reuse forever)
2️⃣ Choose your procedure
3️⃣ We book the appointment for you

🔒 Your data is encrypted with AES-256 at rest.
We never store MiConsulado passwords.

Use /help for all commands.
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📋 Book INM Appointment", callback_data="inm_start"),
            InlineKeyboardButton("🛂 Book SRE Appointment", callback_data="sre_start"),
        ],
        [
            InlineKeyboardButton("👤 My Profile", callback_data="profile"),
            InlineKeyboardButton("📅 My Appointments", callback_data="appointments"),
        ],
        [
            InlineKeyboardButton("🌐 Open Website", url="https://citafacil.app"),
        ],
    ]
    await update.message.reply_text(
        WELCOME_TEXT,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


HELP_TEXT = """
*Commands:*
/start — Main menu
/inm — Book INM appointment
/sre — Book SRE appointment
/profile — View/update your profile
/appointments — View your appointments
/link — Link your Telegram to your web account
/help — Show this message

*Need help?* Visit our website or contact support.
"""


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")
