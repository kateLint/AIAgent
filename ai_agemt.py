# Telegram Shopping Bot with advanced features:
# - /edit for quantity updates
# - category support
# - multilingual support (Hebrew/English)

import logging
import sqlite3
import re
import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# === Setup ===
logging.basicConfig(level=logging.INFO)
TOKEN = "7694241161:AAGkVV-m6LXanYzrv2vuWpbImIaJ4etBsbs"

# === Language Support ===
LANG = {
    "he": {
        "commands": """
פקודות זמינות:
/add <פריט> ➡️ הוספת פריט לרשימה
/list ➡️ הצגת כל הרשימה
/delete ➡️ מחיקת פריט לפי מספר
/clear ➡️ ניקוי כל הרשימה
/suggest ➡️ הצעת פריטים בסיסיים חסרים
/edit <שם פריט> x<כמות> ➡️ עריכת כמות
""",
        "start": "שלום! אני סוכן הקניות שלך. הנה הפקודות הזמינות:",
        "empty_list": "הרשימה ריקה כרגע.",
        "deleted": "הרשימה נוקתה ✅",
        "choose_delete": "בחר מספרים למחיקה (למשל: 1,3):",
        "choose_suggest": "בחר פריטים להוספה (למשל: 2x3,1):",
        "already_exists": "כבר קיים ברשימה.",
        "added": "הוספתי",
        "removed": "מחקתי",
        "updated": "עודכן ל"
    },
    "en": {
        "commands": """
Available commands:
/add <item> ➡️ Add item to the list
/list ➡️ Show shopping list
/delete ➡️ Delete by number
/clear ➡️ Clear all items
/suggest ➡️ Suggest missing basics
/edit <item name> x<quantity> ➡️ Edit quantity
""",
        "start": "Hello! I'm your shopping agent. Here are your available commands:",
        "empty_list": "The list is currently empty.",
        "deleted": "The list has been cleared ✅",
        "choose_delete": "Choose item numbers to delete (e.g., 1,3):",
        "choose_suggest": "Choose items to add (e.g., 2x3,1):",
        "already_exists": "already exists in your list.",
        "added": "Added",
        "removed": "Removed",
        "updated": "Updated to"
    }
}

# === Database ===
conn = sqlite3.connect("shopping_list.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS shopping (
    chat_id INTEGER,
    item TEXT,
    category TEXT DEFAULT ''
)
""")
conn.commit()

# === State Memory ===
user_states = {}  # {chat_id: {mode: "delete"|"suggest", items: [...]}}
LANG_PREF = {}  # {chat_id: "he" or "en"}

BASIC_ITEMS = {"לחם", "חלב", "ביצים", "פסטה", "אורז", "מלח", "סוכר", "קפה", "ירקות", "פירות"}

# === DB Utils ===
def add_item(chat_id, item, category=""):
    cursor.execute("INSERT INTO shopping (chat_id, item, category) VALUES (?, ?, ?)", (chat_id, item, category))
    conn.commit()

def list_items(chat_id):
    cursor.execute("SELECT item FROM shopping WHERE chat_id = ?", (chat_id,))
    return cursor.fetchall()

def delete_item(chat_id, item):
    cursor.execute("DELETE FROM shopping WHERE chat_id = ? AND item = ?", (chat_id, item))
    conn.commit()

def item_exists(chat_id, item):
    cursor.execute("SELECT 1 FROM shopping WHERE chat_id = ? AND item = ?", (chat_id, item))
    return cursor.fetchone() is not None

def update_quantity(chat_id, item_base, qty):
    cursor.execute("SELECT item FROM shopping WHERE chat_id = ?", (chat_id,))
    for item in cursor.fetchall():
        if item_base in item[0]:
            new_item = f"{qty} × {item_base}" if qty > 1 else item_base
            cursor.execute("UPDATE shopping SET item = ? WHERE chat_id = ? AND item = ?", (new_item, chat_id, item[0]))
            conn.commit()
            return new_item
    return None

def get_all_chats():
    cursor.execute("SELECT DISTINCT chat_id FROM shopping")
    return [row[0] for row in cursor.fetchall()]

# === Utilities ===
def lang(chat_id):
    return LANG.get(LANG_PREF.get(chat_id, "he"))

async def show_available_commands(update: Update):
    await update.message.reply_text(lang(update.effective_chat.id)["commands"])

# === Command Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    LANG_PREF[update.effective_chat.id] = "he"
    await update.message.reply_text(lang(update.effective_chat.id)["start"])
    await show_available_commands(update)

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    item = " ".join(context.args)
    if not item:
        await update.message.reply_text("מה להוסיף?")
        return
    if not item_exists(update.effective_chat.id, item):
        add_item(update.effective_chat.id, item)
        await update.message.reply_text(f"{lang(update.effective_chat.id)['added']}: {item}")
    else:
        await update.message.reply_text(f"{item} {lang(update.effective_chat.id)['already_exists']}")
    await show_available_commands(update)

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = list_items(update.effective_chat.id)
    if not items:
        await update.message.reply_text(lang(update.effective_chat.id)["empty_list"])
    else:
        text = "\n".join(f"- {item[0]}" for item in items)
        await update.message.reply_text(text)
    await show_available_commands(update)

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = list_items(update.effective_chat.id)
    if not items:
        await update.message.reply_text(lang(update.effective_chat.id)["empty_list"])
        return
    numbered = "\n".join(f"{i+1}. {item[0]}" for i, item in enumerate(items))
    await update.message.reply_text(f"{lang(update.effective_chat.id)['choose_delete']}\n{numbered}")
    user_states[update.effective_chat.id] = {"mode": "delete", "items": [item[0] for item in items]}

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("DELETE FROM shopping WHERE chat_id = ?", (update.effective_chat.id,))
    conn.commit()
    await update.message.reply_text(lang(update.effective_chat.id)["deleted"])
    await show_available_commands(update)

async def suggest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    existing = {item[0] for item in list_items(update.effective_chat.id)}
    missing = list(BASIC_ITEMS - existing)
    if not missing:
        await update.message.reply_text("כל הפריטים הבסיסיים קיימים.")
        return
    numbered = "\n".join(f"{i+1}. {item}" for i, item in enumerate(missing))
    await update.message.reply_text(f"{lang(update.effective_chat.id)['choose_suggest']}\n{numbered}")
    user_states[update.effective_chat.id] = {"mode": "suggest", "items": missing}

async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = " ".join(context.args)
        match = re.match(r"(.+)\s*x(\d+)", text)
        if not match:
            await update.message.reply_text("שימוש: /edit <שם> x<כמות>")
            return
        item, qty = match.group(1).strip(), int(match.group(2))
        updated = update_quantity(update.effective_chat.id, item, qty)
        if updated:
            await update.message.reply_text(f"{lang(update.effective_chat.id)['updated']} {updated} ✅")
        else:
            await update.message.reply_text("הפריט לא נמצא ברשימה")
    except Exception as e:
        await update.message.reply_text(f"שגיאה: {e}")
    await show_available_commands(update)

async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    state = user_states.get(chat_id)
    if not state:
        return
    mode, items = state["mode"], state["items"]
    matches = re.findall(r"(\d+)(?:x(\d+))?", update.message.text)
    for idx_str, qty_str in matches:
        idx = int(idx_str) - 1
        qty = int(qty_str) if qty_str else 1
        if idx < 0 or idx >= len(items):
            continue
        base_item = items[idx]
        final_item = f"{qty} × {base_item}" if qty > 1 else base_item
        if mode == "suggest" and not item_exists(chat_id, final_item):
            add_item(chat_id, final_item)
            await update.message.reply_text(f"{lang(chat_id)['added']}: {final_item}")
        elif mode == "delete":
            delete_item(chat_id, base_item)
            await update.message.reply_text(f"{lang(chat_id)['removed']}: {base_item}")
    del user_states[chat_id]
    await show_available_commands(update)

async def reminder_task(app):
    for chat_id in get_all_chats():
        try:
            await app.bot.send_message(chat_id=chat_id, text="תזכורת לעדכן את רשימת הקניות 🛒 /list")
        except Exception as e:
            logging.error(f"Reminder error: {e}")

async def main():
    nest_asyncio.apply()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_command))
    app.add_handler(CommandHandler("delete", delete))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("suggest", suggest))
    app.add_handler(CommandHandler("edit", edit))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_selection))
    scheduler = AsyncIOScheduler(timezone="Asia/Jerusalem")
    scheduler.add_job(reminder_task, 'cron', args=[app], day_of_week="sun,wed", hour=10, minute=0)
    scheduler.start()
    print("הבוט פועל...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
