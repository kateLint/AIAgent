# handlers/suggest.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from utils.common import format_item_display
from utils import db
from utils.lang import get_text

# Suggested Items (basic)
SUGGESTED_ITEMS = [
    "Milk", "Bread", "Eggs", "Cheese", "Tomatoes",
    "Cucumbers", "Apples", "Bananas", "Rice", "Pasta"
]

DEFAULT_UNIT = 'pcs'

async def send_suggest_buttons(update, context):
    chat_id = update.effective_chat.id
    selected = context.user_data.get("selected_suggested_items", [])

    keyboard = []
    temp_row = []

    for item in SUGGESTED_ITEMS:
        prefix = "✅" if item in selected else "⬜"
        button = InlineKeyboardButton(f"{prefix} {item}", callback_data=f"select_suggest:{item}")
        temp_row.append(button)
        if len(temp_row) == 2:
            keyboard.append(temp_row)
            temp_row = []

    if temp_row:
        keyboard.append(temp_row)

    if selected:
        keyboard.append([
            InlineKeyboardButton(get_text(chat_id, "add_selected_items"), callback_data="confirm_suggest")
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(get_text(chat_id, "choose_suggested_items"), reply_markup=reply_markup)

async def handle_suggest_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id

    selected = context.user_data.get("selected_suggested_items", [])

    if data.startswith("select_suggest:"):
        item = data.split(":")[1]
        if item in selected:
            selected.remove(item)
        else:
            selected.append(item)
        context.user_data["selected_suggested_items"] = selected

        # Rebuild the keyboard dynamically
        keyboard = []
        temp_row = []
        for sug_item in SUGGESTED_ITEMS:
            prefix = "✅" if sug_item in selected else "⬜"
            button = InlineKeyboardButton(f"{prefix} {sug_item}", callback_data=f"select_suggest:{sug_item}")
            temp_row.append(button)
            if len(temp_row) == 2:
                keyboard.append(temp_row)
                temp_row = []
        if temp_row:
            keyboard.append(temp_row)
        if selected:
            keyboard.append([
                InlineKeyboardButton("➕ Add Selected Items", callback_data="confirm_suggest")
            ])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text("Select items to add:", reply_markup=reply_markup)

    elif data == "confirm_suggest":
        added = []
        for item_name in selected:
            if not db.item_exists(chat_id, item_name):
                db.add_item(chat_id, item_name, quantity=1, unit=DEFAULT_UNIT)
                added.append(item_name)

        context.user_data["selected_suggested_items"] = []
        if added:
            formatted = [f"- {name}" for name in added]
            await query.edit_message_text(f"{get_text(chat_id, 'added_to_list')}\n" + "\n".join(formatted))
        else:
            await query.edit_message_text(get_text(chat_id, "no_items_added"))
