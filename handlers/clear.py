# handlers/clear.py

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from utils.db import clear_items
from utils.lang import get_text

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    try:
        clear_items()
        await update.message.reply_text("✅ " + get_text(chat_id, "cleared"))
    except Exception as e:
        await update.message.reply_text(f"❗ Error clearing list: {e}")
