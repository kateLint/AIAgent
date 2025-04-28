# utils/lang.py
import sqlite3

DEFAULT_LANG = "en"

TEXTS = {
    "en": {
        "choose_language": "🌐 Please choose your language:",
        "language_selected": "✅ Language selected successfully!",
        "start_message": "👋 Welcome! I'm your shopping assistant.",
        "list_title": "Shared Shopping List:",
        "nothing_deleted": "No items were deleted.",
        "cleared": "✅ The shopping list was cleared!",
        "current_reminder": "Current reminder: every {} days.",
        "send_new_reminder": "📅 Send a new number of days to update the reminder.",
        "reminder_updated": "✅ Reminder updated to every {} days!",
        "invalid_reminder": "❗ Please send a number between 1 and 30.",
                "empty_list": "🛒 Your shopping list is currently empty.",
                 "ask_what_to_add": "📥 What would you like to add?",
        "already_exists": "⚠️ This item already exists in your list.",
        "added_successfully": "has been successfully added!",
        "invalid_items": "❗ Invalid input. Please send the item names.",
        "choose_item_to_delete": "🗑 Choose an item to delete:",
                "choose_suggested_items": "🛒 Choose suggested items to add:",
"add_selected_items": "➕ Add selected items",
        "added_to_list": "✅ Added to list:",
        "confirm_update": "✅ Update",
        "bulk_edit_title": "🛒 Shopping List Edit:\nSelect an item and update quantity and unit",
        "updated_successfully": "✅ Updated successfully!",
        "choose_items_to_delete": "🛒 Choose items to delete:",
"item_deleted_successfully": "✅ {item_name} deleted successfully!",
"invalid_number": "❗ Invalid number. Please try again.",
"item_not_found": "❗ Item not found. Please try again.",
"all_items_deleted": "✅ All items deleted!",
"confirm_multi_delete": "🗑️ Delete selected items",
"multi_items_deleted": "✅ Selected items deleted successfully!",
"clear_all_list": "🗑️ Clear Entire List",

    },
    "he": {
        "choose_language": "🌐 אנא בחר שפה:",
        "language_selected": "✅ השפה עודכנה בהצלחה!",
        "start_message": "👋 שלום! אני עוזר הקניות שלך.",
        "list_title": "רשימת הקניות המשותפת:",
        "nothing_deleted": "לא נמחקו פריטים.",
        "cleared": "✅ הרשימה נוקתה בהצלחה!",
        "current_reminder": "תזכורת נוכחית: כל {} ימים.",
        "send_new_reminder": "📅 שלח מספר ימים חדש לעדכון התזכורת.",
        "reminder_updated": "✅ התזכורת עודכנה ל־{} ימים!",
                "empty_list": "🛒 רשימת הקניות שלך ריקה כרגע.",
"ask_what_to_add": "📥 מה תרצה להוסיף?",
        "already_exists": "⚠️ פריט זה כבר קיים ברשימה שלך.",
        "added_successfully": "נוסף בהצלחה!",
        "invalid_items": "❗ קלט לא תקין. שלח שמות פריטים.",
        "invalid_reminder": "❗ נא לשלוח מספר בין 1 ל־30.",
        "choose_item_to_delete": "🗑 בחר פריט למחיקה:",
                "choose_suggested_items": "🛒 בחר פריטים מומלצים להוספה:",
    "add_selected_items": "➕ הוסף פריטים שנבחרו",
        "added_to_list": "✅ נוספו לרשימה:",
        "confirm_update": "✅ עדכן",
         "bulk_edit_title": "🛒 עריכת רשימת קניות:\nבחרי פריט ועדכני את הכמות והיחידה",
        "updated_successfully": "✅ עודכן בהצלחה!",
        "choose_items_to_delete": "🛒 בחר פריטים למחיקה:",
"item_deleted_successfully": "✅ {item_name} נמחק בהצלחה!",
"invalid_number": "❗ מספר לא חוקי. נסה שוב.",
"item_not_found": "❗ פריט לא נמצא. נסה שוב.",
"all_items_deleted": "✅ כל הפריטים נמחקו!",
"confirm_multi_delete": "🗑️ מחק פריטים שנבחרו",
"multi_items_deleted": "✅ כל הפריטים שנבחרו נמחקו בהצלחה!",
"clear_all_list": "🗑️ נקה את כל הרשימה",



    }
}

conn = sqlite3.connect("shopping_list.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS languages (
    chat_id INTEGER PRIMARY KEY,
    lang TEXT DEFAULT 'en'
)
""")
conn.commit()

def set_language(chat_id: int, lang: str):
    cursor.execute("""
    INSERT INTO languages (chat_id, lang) VALUES (?, ?)
    ON CONFLICT(chat_id) DO UPDATE SET lang=excluded.lang
    """, (chat_id, lang))
    conn.commit()

def get_language(chat_id: int) -> str:
    cursor.execute("SELECT lang FROM languages WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()
    return row[0] if row else DEFAULT_LANG

def get_text(chat_id: int, key: str) -> str:
    lang = get_language(chat_id)
    return TEXTS.get(lang, TEXTS[DEFAULT_LANG]).get(key, "")

def available_languages():
    """Return the available languages for user selection"""
    return {
        "🇺🇸 English": "en",
        "🇮🇱 עברית": "he",
    }
