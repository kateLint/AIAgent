# handlers/add.py

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from utils import db
from utils.lang import get_text
from utils.common import clean_item_name

import logging

DEFAULT_UNIT = 'pcs'

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = " ".join(context.args).strip()

    logging.debug(f"/add received text: '{text}' from chat_id: {chat_id}")

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    if not text:
        await update.message.reply_text(get_text(chat_id, "ask_what_to_add"))
        context.user_data["mode"] = "awaiting_add"
        return

    item_name = clean_item_name(text)

    if db.item_exists(chat_id, item_name):
        await update.message.reply_text(get_text(chat_id, "already_exists"))
    else:
        db.add_item(chat_id, item_name, quantity=1, unit=DEFAULT_UNIT)
        await update.message.reply_text(f"✅ {item_name} {get_text(chat_id, 'added_successfully')}")

async def handle_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if context.user_data.get("mode") != "awaiting_add":
        return

    items = [item.strip() for item in text.split(",") if item.strip()]
    if not items:
        await update.message.reply_text(get_text(chat_id, "invalid_items"))
        return

    added = []
    skipped = []

    for item in items:
        item_name = clean_item_name(item)
        if db.item_exists(chat_id, item_name):
            skipped.append(item_name)
        else:
            db.add_item(chat_id, item_name, quantity=1, unit=DEFAULT_UNIT)
            added.append(item_name)
 
    if added:
        added_items = "\n".join(f"- {i}" for i in added)
        response += _( "response_added" ).format(items=added_items) + "\n"

    if skipped:
        skipped_items = "\n".join(f"- {i}" for i in skipped)
        response += _( "response_skipped" ).format(items=skipped_items)   

    await update.message.reply_text(response.strip())
    context.user_data.pop("mode", None)
