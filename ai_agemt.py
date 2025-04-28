import asyncio
import logging
import nest_asyncio
import asyncio
import logging
logging.basicConfig(level=logging.DEBUG)
from telegram.ext import ApplicationBuilder, PicklePersistence
from handlers.edit import send_bulk_edit, handle_bulk_edit_callback, handle_edit_callback
from handlers.delete import handle_delete, send_delete_buttons
from telegram import BotCommand, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from handlers.add import add_command, handle_add
from handlers.list import list_command
from handlers.delete import handle_delete_button, send_multi_select_delete, handle_multi_select_callback
from handlers.suggest import send_suggest_buttons, handle_suggest_callback
from handlers.edit import handle_edit
from handlers.reminder import handle_reminder_response, reminder, handle_reminder_button
from handlers.callback import handle_general_callback

from utils.lang import available_languages, get_text
from utils import db

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

# === Setup ===
logging.basicConfig(level=logging.INFO)

TOKEN = "7694241161:AAGkVV-m6LXanYzrv2vuWpbImIaJ4etBsbs"
# === Functions ===

persistence = PicklePersistence(filepath="bot_data")
app = ApplicationBuilder().token(TOKEN).persistence(persistence).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type

    db.add_chat(chat_id, chat_type)

    langs = available_languages()
    buttons = [
        [key for key in langs.keys()]
    ]

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(flag, callback_data=f"lang_{code}")]
         for flag, code in langs.items()]
    )

    await update.message.reply_text(
        get_text(chat_id, "choose_language"),
        reply_markup=keyboard
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    mode = context.user_data.get("mode")

    if mode == "awaiting_add":
        await handle_add(update, context)
    elif mode == "awaiting_delete":
        await handle_delete(update, context, forced_text=update.message.text.strip())
    elif mode == "awaiting_suggest":
        await handle_suggest(update, context)
    elif mode == "awaiting_edit":
        await handle_edit(update, context)
    elif mode == "awaiting_reminder":
        await handle_reminder_response(update, context)
    else:
        await update.message.reply_text(get_text(chat_id, "unknown_command"))

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    chat_id = update.effective_chat.id

    logging.debug(f"Received callback: {data} from chat_id: {chat_id}")

    if data.startswith("set_lang:"):
        lang_code = data.split(":")[1]
        from utils.lang import set_language, get_text
        logging.debug(f"Setting language to {lang_code} for chat_id: {chat_id}")

        set_language(chat_id, lang_code)

        await query.answer()
        await query.edit_message_text(get_text(chat_id, "language_selected"))
        await query.message.reply_text(get_text(chat_id, "start_message"))
    else:
        logging.debug(f"Passing to general callback handler: {data}")
        await handle_general_callback(update, context)

async def handle_delete_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("delete_item:"):
        item_id = int(data.split(":")[1])
        db.delete_item_by_id(item_id)
        await query.edit_message_text("✅ הפריט נמחק!")

async def send_reminders(app):
    for chat_id in db.get_chats_for_reminder():
        try:
            await app.bot.send_message(chat_id=chat_id, text="⏰ Reminder: Update your shopping list! /list")
        except Exception as e:
            logging.error(f"Failed to send reminder to {chat_id}: {e}")


# === Main ===
async def main():

    # Commands
    await app.bot.set_my_commands([
        BotCommand("start", "🚀 Start the bot"),
        BotCommand("add", "➕ Add an item"),
        BotCommand("list", "📋 Show shopping list"),
        BotCommand("delete", "🗑️ Delete an item"),
        BotCommand("suggest", "💡 Suggest basics"),
        BotCommand("edit", "✏️ Edit quantities"),
        BotCommand("reminder", "⏰ Manage reminders"),
    ])

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_command))
    app.add_handler(CommandHandler("list", list_command))
    app.add_handler(CommandHandler("delete", send_multi_select_delete))

    app.add_handler(CommandHandler("suggest", send_suggest_buttons))
    app.add_handler(CommandHandler("edit", send_bulk_edit))

    app.add_handler(CommandHandler("reminder", reminder))
    
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^\d{1,2}$'), handle_reminder_response))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))

    app.add_handler(CallbackQueryHandler(lambda update, context: update.callback_query.answer(), pattern=r"^noop$"))
    app.add_handler(CallbackQueryHandler(handle_bulk_edit_callback, pattern=r"^(bulk_decrease|bulk_increase|bulk_change_unit):\d+$|^bulk_confirm$"))
    app.add_handler(CallbackQueryHandler(handle_edit_callback, pattern=r"^(edit_select:|edit_decrease:|edit_increase:|edit_change_unit:|edit_back|edit_confirm)$"))
    app.add_handler(CallbackQueryHandler(handle_suggest_callback, pattern=r"^(select_suggest:|confirm_suggest)"))
    app.add_handler(CallbackQueryHandler(handle_reminder_button, pattern="^reminder_"))
    app.add_handler(CallbackQueryHandler(handle_multi_select_callback, pattern=r"^(select_item:\d+|confirm_delete|clear_all_items)$"))
    app.add_handler(CallbackQueryHandler(handle_delete_button, pattern=r"^delete_item:"))
    app.add_handler(CallbackQueryHandler(handle_callback_query))


    # Scheduler for Reminders
    scheduler = AsyncIOScheduler(timezone="Asia/Jerusalem")
    scheduler.add_job(send_reminders, "interval", days=1, args=[app])
    scheduler.start()

    print("🚀 Bot running...")
    await app.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())