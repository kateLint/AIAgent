# handlers/callback.py

from telegram import Update
from telegram.ext import ContextTypes
from utils.lang import get_text, set_language, TEXTS
import logging

async def handle_general_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    chat_id = query.message.chat.id

    logging.debug(f"General callback received: {data} from chat {chat_id}")

    if data.startswith("lang_"):
        lang_code = data.split("_")[1]

        set_language(chat_id, lang_code)

        await query.edit_message_text(
            text=get_text(chat_id, "language_selected"),
            parse_mode="Markdown"
        )
        await query.message.reply_text(
            text=get_text(chat_id, "start_message"),
            parse_mode="Markdown"
        )

    elif data == "noop":
        await query.answer()

    else:
        logging.warning(f"⚠️ Unknown callback received: '{data}' from chat {chat_id}")
        await query.edit_message_text(
            text="⚠️ Action not recognized. Please try again.\nIf the problem persists, type /start to reset."
        )
