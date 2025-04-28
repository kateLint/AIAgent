# handlers/list.py

from telegram import Update
from telegram.ext import ContextTypes
from utils.common import format_item_display
from utils import db
from utils.lang import get_text

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    items = db.list_items(chat_id)

    if not items:
        await update.message.reply_text(get_text(chat_id, "empty_list"))
        return

    message = get_text(chat_id, "list_title") + "\n\n"
    for idx, item_row in enumerate(items, start=1):
        formatted_item = format_item_display(item_row, chat_id)
        message += f"{idx}. {formatted_item}\n"

    await update.message.reply_text(message.strip())
