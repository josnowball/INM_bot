"""
/tip command — voluntary donations for CitaFacil.
Free forever, but users can tip if they want.
"""

import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .i18n import get_lang


# Default tip link — override with STRIPE_TIP_LINK env var
STRIPE_TIP_LINK = os.getenv("STRIPE_TIP_LINK", "")
PAYPAL_LINK = os.getenv("PAYPAL_TIP_LINK", "")

TIP_TEXT = {
    "en": (
        "☕ *Tip the Author*\n\n"
        "CitaFacil is 100% free, forever. No ads, no premium tiers.\n\n"
        "If it saved you time and frustration, consider leaving a tip.\n"
        "Every contribution helps keep the servers running.\n\n"
        "Thank you for your support! 🙏"
    ),
    "zh": (
        "☕ *给作者打赏*\n\n"
        "CitaFacil 永久免费。没有广告，没有付费功能。\n\n"
        "如果它帮你节省了时间和精力，可以考虑打赏一下。\n"
        "每一份支持都有助于维持服务器运行。\n\n"
        "感谢你的支持！🙏"
    ),
    "es": (
        "☕ *Dale Propina al Autor*\n\n"
        "CitaFacil es 100% gratis, para siempre. Sin anuncios, sin planes premium.\n\n"
        "Si te ahorro tiempo y frustracion, considera dejar una propina.\n"
        "Cada contribucion ayuda a mantener los servidores funcionando.\n\n"
        "Gracias por tu apoyo! 🙏"
    ),
}


async def tip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    text = TIP_TEXT.get(lang, TIP_TEXT["es"])

    buttons = []
    if STRIPE_TIP_LINK:
        labels = {"en": "💳 Tip via Stripe", "zh": "💳 通过 Stripe 打赏", "es": "💳 Propina via Stripe"}
        buttons.append([InlineKeyboardButton(labels.get(lang, labels["es"]), url=STRIPE_TIP_LINK)])
    if PAYPAL_LINK:
        labels = {"en": "🅿️ Tip via PayPal", "zh": "🅿️ 通过 PayPal 打赏", "es": "🅿️ Propina via PayPal"}
        buttons.append([InlineKeyboardButton(labels.get(lang, labels["es"]), url=PAYPAL_LINK)])

    if not buttons:
        # No links configured — show placeholder
        text += "\n\n_(Tip links coming soon!)_"

    keyboard = InlineKeyboardMarkup(buttons) if buttons else None
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)


async def tip_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Thank you! / ¡Gracias! / 谢谢！")
