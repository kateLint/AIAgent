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
from telegram import BotCommand
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler
from telegram import ReplyKeyboardRemove


# === Setup ===
logging.basicConfig(level=logging.INFO)
TOKEN = "7694241161:AAGkVV-m6LXanYzrv2vuWpbImIaJ4etBsbs"

# === Language Support ===
LANG = {
    "he": {
        "commands": """
פקודות זמינות:
/add <פריט> ➡️ הוספת פריט לרשימה המשותפת
/list ➡️ הצגת כל הרשימה המשותפת
/delete ➡️ מחיקת פריט לפי מספר
/clear ➡️ ניקוי כל הרשימה
/suggest ➡️ הצעת פריטים בסיסיים חסרים
/edit <שם פריט> x<כמות> ➡️ עריכת כמות
""",
        "start": "שלום! אני סוכן הקניות שלך. הרשימה משותפת לכל המשתמשים. הנה הפקודות הזמינות:",
        "empty_list": "הרשימה המשותפת ריקה כרגע.",
        "deleted": "הרשימה המשותפת נוקתה ✅",
        "choose_delete": "בחר מספרים למחיקה (למשל: 1,3):",
        "choose_suggest": "בחר פריטים להוספה (למשל: 2x3,1):",
        "already_exists": "כבר קיים ברשימה המשותפת.",
        "added": "הוספתי",
        "removed": "מחקתי",
        "updated": "עודכן ל"
    },
    "en": {
        "commands": """
Available commands:
/add <item> ➡️ Add item to the shared list
/list ➡️ Show shared shopping list
/delete ➡️ Delete by number
/clear ➡️ Clear all items
/suggest ➡️ Suggest missing basics
/edit <item name> x<quantity> ➡️ Edit quantity
""",
        "start": "Hello! I'm your shopping agent. The list is shared among all users. Here are your available commands:",
        "empty_list": "The shared list is currently empty.",
        "deleted": "The shared list has been cleared ✅",
        "choose_delete": "Choose item numbers to delete (e.g., 1,3):",
        "choose_suggest": "Choose items to add (e.g., 2x3,1):",
        "already_exists": "already exists in the shared list.",
        "added": "Added",
        "removed": "Removed",
        "updated": "Updated to"
    }
}


# === Database ===
conn = sqlite3.connect("shopping_list.db", check_same_thread=False)
cursor = conn.cursor()

# Create shared shopping list table
cursor.execute("""
CREATE TABLE IF NOT EXISTS shopping (
    item TEXT,
    category TEXT DEFAULT ''
)
""")
# Create table to track users for reminders
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    chat_id INTEGER PRIMARY KEY
)
""")
conn.commit()

# === State Memory ===
user_states = {}  # {chat_id: {mode: "delete"|"suggest", items: [...]}}
LANG_PREF = {}  # {chat_id: "he" or "en"}

BASIC_ITEMS = {"גלידה", "חלב", "ביצים", "פסטה", "אורז", "מלח", "סוכר", "עגבניה", "מלפפון", "תפוחים"}

# === DB Utils ===
def add_item(item, category=""):
    try:
        cursor.execute("INSERT INTO shopping (item, category) VALUES (?, ?)", (item, category))
        conn.commit()
        logging.info(f"Item added successfully to DB: {item}")
    except Exception as e:
        logging.error(f"Error inserting item: {e}")

def list_items():
    cursor.execute("SELECT item FROM shopping")
    return cursor.fetchall()

def delete_item(item):
    cursor.execute("DELETE FROM shopping WHERE item = ?", (item,))
    conn.commit()

def item_exists(item):
    cursor.execute("SELECT 1 FROM shopping WHERE item = ?", (item,))
    return cursor.fetchone() is not None

def update_quantity(item_base, qty):
    cursor.execute("SELECT item FROM shopping")
    for (item_name,) in cursor.fetchall():
        # ניקוי שם הבסיס: הסרה של כמות ישנה אם קיימת
        clean_name = re.sub(r"^\d+\s*[×x]\s*", "", item_name).strip()

        if item_base.strip() == clean_name:
            # בניית שם חדש
            new_item_name = f"{qty} × {clean_name}" if qty > 1 else clean_name

            cursor.execute("UPDATE shopping SET item = ? WHERE item = ?", (new_item_name, item_name))
            conn.commit()
            return new_item_name
    return None


def add_user(chat_id):
    try:
        cursor.execute("INSERT OR IGNORE INTO users (chat_id) VALUES (?)", (chat_id,))
        conn.commit()
    except Exception as e:
        logging.error(f"Error adding user: {e}")

def get_all_users():
    cursor.execute("SELECT chat_id FROM users")
    return [row[0] for row in cursor.fetchall()]

def lang(chat_id):
    return LANG.get(LANG_PREF.get(chat_id, "he"))

async def show_available_commands(update: Update):
    await update.message.reply_text(lang(update.effective_chat.id)["commands"])

# === Command Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    LANG_PREF[chat_id] = "en"
    add_user(chat_id)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("ℹ️ Help", callback_data="show_help")]
    ])

    await update.message.reply_text(
        "👋 Welcome! What do you want to do?",
        reply_markup=ReplyKeyboardRemove(),
    )


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    item = " ".join(context.args).strip()

    if not item:
        await update.message.reply_text("📥 מה תרצי להוסיף לרשימת הקניות?")
        user_states[chat_id] = {"mode": "awaiting_add"}
        return

    try:
        if item_exists(item):
            await update.message.reply_text(f"⚠️ {item} {lang(chat_id)['already_exists']}")
        else:
            add_item(item)
            await update.message.reply_text(f"✅ {lang(chat_id)['added']}: {item}")
    except Exception as e:
        logging.error(f"Error in add: {e}")
        await update.message.reply_text(f"שגיאה בהוספה: {e}")
    
    

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    items = list_items()
    if not items:
        await update.message.reply_text(lang(chat_id)["empty_list"])
    else:
        text = "\n".join(f"{i+1}. {item[0]}" for i, item in enumerate(items))
        await update.message.reply_text(text)
    

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    items = list_items()

    if not items:
        await update.message.reply_text(f"📭 {lang(chat_id)['empty_list']}")
        return

    numbered = "\n".join(f"{i+1}. {item[0]}" for i, item in enumerate(items))
    await update.message.reply_text(f"{lang(chat_id)['choose_delete']}\n{numbered}")

    user_states[chat_id] = {
        "mode": "awaiting_delete",
        "items": [item[0] for item in items]
    }


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    cursor.execute("DELETE FROM shopping")
    conn.commit()
    await update.message.reply_text(lang(chat_id)["deleted"])
    

async def suggest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    existing_items = {item[0] for item in list_items()}
    missing_items = list(BASIC_ITEMS - existing_items)

    if not missing_items:
        await update.message.reply_text("✅ כל הפריטים הבסיסיים כבר קיימים ברשימה.")
        return

    numbered_missing = "\n".join(f"{i+1}. {item}" for i, item in enumerate(missing_items))
    await update.message.reply_text(f"🛒 פריטים בסיסיים זמינים להוספה:\n{numbered_missing}\n\n📥 הקלידו מספרים להוספה, למשל: 1 3 5", parse_mode="Markdown")

    user_states[chat_id] = {
        "mode": "awaiting_suggest",
        "items": missing_items
    }


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "show_help":
        await query.edit_message_text(
            text="ℹ️ Here is how you use the bot:\n\n"
                 "- /add ➡️ Add new items\n"
                 "- /list ➡️ View your list\n"
                 "- /delete ➡️ Remove items\n"
                 "- /suggest ➡️ See basic items\n"
                 "- /edit ➡️ Change quantities",
            parse_mode="Markdown"
        )

    elif data == "edit_info":
        await query.edit_message_text(
            text="✏️ **Editing Items:**\n\n"
                 "- By names: `Milk 2, Eggs 6`\n"
                 "- By numbers: `1 2, 3 4`\n\n"
                 "_Each item must be followed by a quantity!_",
            parse_mode="Markdown"
        )

    else:
        await query.edit_message_text(
            text="⚠️ Unknown action. Try again."
        )


async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = " ".join(context.args).strip()
    items = list_items()

    if not items:
        await update.message.reply_text(lang(chat_id)["empty_list"])
        return

    numbered_list = "\n".join(f"{i+1}. {item[0]}" for i, item in enumerate(items))

    # שליחת רשימת המוצרים + כפתור ℹ️
    await update.message.reply_text(
        f"📝 **Current Items:**\n{numbered_list}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("ℹ️ How to edit", callback_data="edit_info")]]
        )
    )

    user_states[chat_id] = {
        "mode": "awaiting_edit",
        "items": [item[0] for item in items]
    }

    if text:
        await handle_edit_input(chat_id, text, update)


async def handle_edit_input(chat_id, text, update):
    try:
        items = user_states.get(chat_id, {}).get("items", [])
        
        # קודם לבדוק אם המשתמש הקליד מספרים
        if all(re.fullmatch(r"\d+", token.strip()) for token in text.split()):
            selected_indexes = [int(t.strip()) - 1 for t in text.split()]
            selected_items = []

            for idx in selected_indexes:
                if 0 <= idx < len(items):
                    selected_items.append(items[idx])

            if not selected_items:
                await update.message.reply_text("⚠️ לא נמצאו פריטים תואמים למספרים שסיפקת.")
                return

            user_states[chat_id] = {
                "mode": "awaiting_edit_quantity",
                "selected_items": selected_items
            }

            items_text = "\n".join(f"- {item}" for item in selected_items)
            await update.message.reply_text(f"📥 בחרת לערוך את:\n{items_text}\n\n📥 כתבי כמויות בפורמט כמו: 2 3 1 4 (לפי הסדר שבחרת)")

            return

        # אחרת — המשתמש הזין שמות וכמויות (מופרדים בפסיקים)
        text = text.replace(",", " ")  # תומך גם בפסיקים
        pattern = r"([^0-9]+)\s*([0-9]+)"
        matches = re.findall(pattern, text)

        if not matches:
            await update.message.reply_text("❗ לא זוהו פריטים וכמויות תקינות. נסי שוב.")
            return

        updated_items = []
        failed_items = []

        for item_name, qty_str in matches:
            item_name = item_name.strip()
            qty = int(qty_str)

            updated = update_quantity(item_name, qty)
            if updated:
                updated_items.append(updated)
            else:
                failed_items.append(item_name)

        response = ""
        if updated_items:
            response += "✅ עודכנו:\n" + "\n".join(f"- {itm}" for itm in updated_items) + "\n"
        if failed_items:
            response += "⚠️ פריטים שלא נמצאו ברשימה:\n" + "\n".join(f"- {itm}" for itm in failed_items)

        await update.message.reply_text(response.strip())
        

    except Exception as e:
        logging.error(f"Error in handle_edit_input: {e}")
        await update.message.reply_text(f"שגיאה בעריכה: {e}")



async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if update.message.text is None:
        logging.warning("Received a message without text. Ignoring.")
        return

    state = user_states.get(chat_id)
    if not state:
        return

    if state["mode"] == "awaiting_add":
        items_text = update.message.text.strip()
        if not items_text:
            await update.message.reply_text("❗ נא להקליד מוצר תקין.")
            return

        items = [item.strip() for item in items_text.split(",") if item.strip()]
        if not items:
            await update.message.reply_text("❗ לא זוהו פריטים תקינים. נסי שוב.")
            return

        added_items = []
        skipped_items = []

        for item in items:
            if item_exists(item):
                skipped_items.append(item)
            else:
                add_item(item)
                added_items.append(item)

        response = ""
        if added_items:
            response += "✅ נוספו לרשימה:\n" + "\n".join(f"- {itm}" for itm in added_items) + "\n"
        if skipped_items:
            response += "⚠️ פריטים שכבר קיימים:\n" + "\n".join(f"- {itm}" for itm in skipped_items)

        await update.message.reply_text(response.strip())
        del user_states[chat_id]
        return

    elif state["mode"] == "awaiting_delete":
        try:
            items = state["items"]
            selections = re.findall(r"\d+", update.message.text)

            if not selections:
                await update.message.reply_text("❗ לא זוהו מספרים חוקיים. נסי שוב.")
                return

            deleted_items = []
            for idx_str in selections:
                idx = int(idx_str) - 1
                if 0 <= idx < len(items):
                    delete_item(items[idx])
                    deleted_items.append(items[idx])

            response = ""
            if deleted_items:
                response += "🗑️ נמחקו:\n" + "\n".join(f"- {itm}" for itm in deleted_items)
            else:
                response += "⚠️ לא נמחק אף פריט."

            await update.message.reply_text(response.strip())
            del user_states[chat_id]

        except Exception as e:
            logging.error(f"Error in delete selection: {e}")
            await update.message.reply_text(f"שגיאה במחיקה: {e}")
        return

    elif state["mode"] == "awaiting_edit":
        try:
            items = state["items"]
            text = update.message.text.strip()

            text = text.replace(",", " ")
            numbers = re.findall(r"\d+", text)

            if len(numbers) % 2 != 0:
                await update.message.reply_text("⚠️ פורמט שגוי. כל מוצר חייב להיות עם כמות. דוגמה: 1 2, 3 4")
                return

            updated_items = []
            failed_items = []

            for i in range(0, len(numbers), 2):
                idx = int(numbers[i]) - 1
                qty = int(numbers[i + 1])

                if 0 <= idx < len(items):
                    item_name = items[idx]
                    updated = update_quantity(item_name, qty)
                    if updated:
                        updated_items.append(updated)
                    else:
                        failed_items.append(item_name)
                else:
                    failed_items.append(f"מספר {idx+1} לא קיים")

            response = ""
            if updated_items:
                response += "✅ עודכנו:\n" + "\n".join(f"- {itm}" for itm in updated_items) + "\n"
            if failed_items:
                response += "⚠️ שגיאות בעריכה:\n" + "\n".join(f"- {itm}" for itm in failed_items)

            await update.message.reply_text(response.strip())
            del user_states[chat_id]

        except Exception as e:
            logging.error(f"Error in edit selection: {e}")
            await update.message.reply_text(f"שגיאה בעריכה: {e}")
        return
    elif state["mode"] == "awaiting_suggest":
        try:
            items = state["items"]
            text = update.message.text.strip()
            entries = [entry.strip() for entry in text.split(",") if entry.strip()]

            if not entries:
                await update.message.reply_text("❗ לא זוהו פריטים תקינים. נסי שוב.")
                return

            added_items = []
            skipped_items = []

            for entry in entries:
                if "-" in entry:
                    idx_str, qty_str = entry.split("-")
                else:
                    idx_str, qty_str = entry, "1"

                try:
                    idx = int(idx_str.strip()) - 1
                    qty = int(qty_str.strip())
                except ValueError:
                    await update.message.reply_text(f"⚠️ מספרים לא חוקיים בקטע: {entry}. ודאי שאת מקלידה רק מספרים.")
                    return

                if 0 <= idx < len(items):
                    base_item = items[idx]
                    item_name_to_add = f"{qty} × {base_item}" if qty > 1 else base_item

                    if not item_exists(item_name_to_add):
                        add_item(item_name_to_add)
                        added_items.append(item_name_to_add)
                    else:
                        skipped_items.append(item_name_to_add)
                else:
                    skipped_items.append(f"מספר {idx+1} לא קיים ברשימה")

            response = ""
            if added_items:
                response += "✅ נוספו לרשימה:\n" + "\n".join(f"- {itm}" for itm in added_items) + "\n"
            if skipped_items:
                response += "⚠️ פריטים שלא נוספו (כבר קיימים או לא נמצאו):\n" + "\n".join(f"- {itm}" for itm in skipped_items)

            await update.message.reply_text(response.strip())
            del user_states[chat_id]

        except Exception as e:
            logging.error(f"Error in suggest selection: {e}")
            await update.message.reply_text(f"שגיאה בהוספה מהצעות: {e}")
        return





async def reminder_task(app):
    for chat_id in get_all_users():
        try:
            await app.bot.send_message(chat_id=chat_id, text="תזכורת לעדכן את רשימת הקניות המשותפת 🛒 /list")
        except Exception as e:
            logging.error(f"Reminder error for chat {chat_id}: {e}")

async def main():
    nest_asyncio.apply()
    app = ApplicationBuilder().token(TOKEN).build()
    
    await app.bot.set_my_commands([
        BotCommand("start", "🚀 Start using the bot"),
        BotCommand("add", "➕ Add an item to the shared list"),
        BotCommand("list", "📋 Show the shopping list"),
        BotCommand("delete", "🗑️ Delete an item by number"),
        BotCommand("clear", "🧹 Clear all shopping list"),
        BotCommand("suggest", "💡 Suggest basic items"),
        BotCommand("edit", "✏️ Edit item quantities"),
    ])
    
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_command))
    app.add_handler(CommandHandler("delete", delete))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler(["suggest"], suggest))
    app.add_handler(CommandHandler("edit", edit))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_selection))
    
    scheduler = AsyncIOScheduler(timezone="Asia/Jerusalem")
    scheduler.add_job(reminder_task, 'cron', args=[app], day_of_week="sun,wed", hour=10, minute=0)
    scheduler.start()
    print("הבוט פועל...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())