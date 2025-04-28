# handlers/start.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.lang import get_text, set_language, available_languages

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # הכנת כפתורים לבחירת שפה
    buttons = [
        [InlineKeyboardButton(flag, callback_data=f"set_lang:{code}")]
        for flag, code in available_languages().items()
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        get_text(chat_id, "choose_language"),
        reply_markup=keyboard
    )

async def handle_language_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("set_lang:"):
        lang_code = data.split(":")[1]
        chat_id = query.message.chat.id

        # שמירת השפה
        set_language(chat_id, lang_code)

        await query.edit_message_text(
            get_text(chat_id, "language_selected")
        )
