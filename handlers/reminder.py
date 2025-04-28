# handlers/reminder.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.db import get_chat_settings, set_reminder_days, update_last_update
from utils.lang import get_text
from utils.common import send_typing_action

# זיכרון זמני
user_states = {}

def generate_days_keyboard():
    """יוצר מקלדת ימים 1-30"""
    keyboard = []
    for row in range(1, 31, 5):
        buttons = [
            InlineKeyboardButton(str(i), callback_data=f"reminder_{i}")
            for i in range(row, min(row+5, 31))
        ]
        keyboard.append(buttons)
    return InlineKeyboardMarkup(keyboard)

@send_typing_action
async def reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    settings = get_chat_settings(chat_id)
    current_days = settings.get("reminder_days", 3)

    await update.message.reply_text(
        f"{get_text(chat_id, 'current_reminder').format(current_days)}\n\n"
        f"{get_text(chat_id, 'send_new_reminder')}",
        reply_markup=generate_days_keyboard()
    )

    user_states[chat_id] = "awaiting_reminder_update"

@send_typing_action
async def handle_reminder_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if user_states.get(chat_id) != "awaiting_reminder_update":
        return  # מתעלמים אם לא מחכים

    if not text.isdigit():
        await update.message.reply_text(get_text(chat_id, "invalid_reminder"))
        return

    days = int(text)
    if not (1 <= days <= 30):
        await update.message.reply_text(get_text(chat_id, "invalid_reminder"))
        return

    set_reminder_days(chat_id, days)
    update_last_update(chat_id)

    await update.message.reply_text(
        get_text(chat_id, "reminder_updated").format(days)
    )
    user_states.pop(chat_id, None)

async def handle_reminder_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id
    data = query.data

    if not data.startswith("reminder_"):
        return

    try:
        days = int(data.split("_")[1])
    except (IndexError, ValueError):
        await query.edit_message_text("❗ Invalid reminder selection.")
        return

    if not (1 <= days <= 30):
        await query.edit_message_text("❗ Invalid number of days.")
        return

    set_reminder_days(chat_id, days)
    update_last_update(chat_id)

    await query.edit_message_text(
        get_text(chat_id, "reminder_updated").format(days)
    )
    user_states.pop(chat_id, None)
