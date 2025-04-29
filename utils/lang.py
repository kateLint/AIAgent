# utils/lang.py
import sqlite3
import logging
DEFAULT_LANG = "en"

TEXTS = {
    "en": {
        "choose_language": "🌐 Select language:",
        "language_selected": "✅ Language updated!",
        "start_message": "👋 Welcome to your shopping assistant!",
        "list_title": "Shopping List:",
        "nothing_deleted": "Nothing deleted.",
        "cleared": "✅ List cleared!",
        "current_reminder": "Current reminder: every {} days.",
        "send_new_reminder": "📅 Enter days for reminder update:",
        "reminder_updated": "✅ Reminder set: every {} days!",
        "invalid_reminder": "❗ Please enter a number between 1-30.",
        "empty_list": "🛒 Your list is empty.",
        "ask_what_to_add": "📥 What to add?",
        "already_exists": "⚠️ Item already exists.",
        "added_successfully": "added!",
        "invalid_items": "❗ Invalid input. Please enter item names.",
        "choose_item_to_delete": "🗑 Select item to delete:",
        "choose_suggested_items": "🛒 Add suggested items:",
        "add_selected_items": "➕ Add selected",
        "added_to_list": "✅ Added:",
        "confirm_update": "✅ Update",
        "bulk_edit_title": "🛒 Edit list items:",
        "updated_successfully": "✅ Updated!",
        "choose_items_to_delete": "🛒 Select items to delete:",
        "item_deleted_successfully": "✅ {} deleted!",
        "invalid_number": "❗ Invalid number.",
        "item_not_found": "❗ Item not found.",
        "all_items_deleted": "✅ All items deleted!",
        "confirm_multi_delete": "🗑️ Delete selected",
        "multi_items_deleted": "✅ Selected items deleted!",
        "clear_all_list": "🗑️ Clear List",
        "add_selected_item": "➕ Add selected",
        "select_tems_to_add": "🛒 Select items:",
        "added_to_favorites": "✅ {} added to favorites",
        "item_updated": "✏️ Item updated!",
        "update_shopping_list": "⏰ Reminder: Update your list! /list",
        "edit_item_text": "🛒 Editing:\n\nQty: {quantity}\nUnit: {unit}",
        "command_start": "🚀 Start",
        "command_add": "➕ Add item",
        "command_list": "📋 Show list",
        "command_delete": "🗑️ Delete",
        "command_suggest": "💡 Suggestions",
        "command_edit": "✏️ Edit items",
        "command_reminder": "⏰ Reminders",
        "decrease_button": "➖",
        "increase_button": "➕",
        "change_unit_button": "{unit}",
        "back_button": "⬅️ Back",
        "confirm_update": "✅ Confirm",
        "bulk_edit_title": "🛒 Edit list:",
        "add_new_name": "➕ New name",
        "add_new_item_name": "✏️ Enter new name:",
        "edit_item": "📝 Edit",
        "response_added": "✅ Added:\n{items}",
        "response_skipped": "⚠️ Already exists:\n{items}",
    },
    "he": {
        "choose_language": "🌐 בחר שפה:",
        "language_selected": "✅ השפה עודכנה!",
        "start_message": "👋 ברוך הבא לעוזר הקניות!",
        "list_title": "רשימת קניות:",
        "nothing_deleted": "לא נמחק דבר.",
        "cleared": "✅ הרשימה נוקתה!",
        "current_reminder": "תזכורת נוכחית: כל {} ימים.",
        "send_new_reminder": "📅 הזן מספר ימים לתזכורת:",
        "reminder_updated": "✅ תזכורת נקבעה: כל {} ימים!",
        "invalid_reminder": "❗ נא להזין מספר בין 1-30.",
        "empty_list": "🛒 הרשימה ריקה.",
        "ask_what_to_add": "📥 מה להוסיף?",
        "already_exists": "⚠️ פריט כבר קיים.",
        "added_successfully": "נוסף!",
        "invalid_items": "❗ קלט שגוי. נא להזין שמות פריטים.",
        "choose_item_to_delete": "🗑 בחר פריט למחיקה:",
        "choose_suggested_items": "🛒 הוסף פריטים מוצעים:",
        "add_selected_items": "➕ הוסף נבחרים",
        "added_to_list": "✅ נוסף:",
        "confirm_update": "✅ עדכן",
        "bulk_edit_title": "🛒 ערוך פריטים:",
        "updated_successfully": "✅ עודכן!",
        "choose_items_to_delete": "🛒 בחר פריטים למחיקה:",
        "item_deleted_successfully": "✅ {} נמחק!",
        "invalid_number": "❗ מספר שגוי.",
        "item_not_found": "❗ פריט לא נמצא.",
        "all_items_deleted": "✅ כל הפריטים נמחקו!",
        "confirm_multi_delete": "🗑️ מחק נבחרים",
        "multi_items_deleted": "✅ הפריטים הנבחרים נמחקו!",
        "clear_all_list": "🗑️ נקה הכל",
        "add_selected_item": "➕ הוסף נבחר",
        "select_tems_to_add": "🛒 בחר פריטים:",
        "added_to_favorites": "✅ {} נוסף למועדפים",
        "item_updated": "✏️ פריט עודכן!",
        "update_shopping_list": "⏰ תזכורת: עדכן את הרשימה! /list",
        "edit_item_text": "🛒 עריכה:\n\nכמות: {quantity}\nיחידה: {unit}",
        "command_start": "🚀 התחל",
        "command_add": "➕ הוסף פריט",
        "command_list": "📋 הצג רשימה",
        "command_delete": "🗑️ מחק",
        "command_suggest": "💡 הצעות",
        "command_edit": "✏️ ערוך",
        "command_reminder": "⏰ תזכורות",
        "decrease_button": "➖",
        "increase_button": "➕",
        "change_unit_button": "{unit}",
        "back_button": "🔙 חזרה",
        "add_new_name": "➕ שם חדש",
        "add_new_item_name": "✏️ הזן שם חדש:",
        "edit_item": "📝 ערוך",
        "response_added": "✅ נוסף:\n{items}",
        "response_skipped": "⚠️ כבר קיים:\n{items}"
    },
    "ru": {
        "choose_language": "🌐 Выберите язык:",
        "language_selected": "✅ Язык обновлен!",
        "start_message": "👋 Добро пожаловать в помощник покупок!",
        "list_title": "Список покупок:",
        "nothing_deleted": "Ничего не удалено.",
        "cleared": "✅ Список очищен!",
        "current_reminder": "Текущее напоминание: каждые {} дней.",
        "send_new_reminder": "📅 Введите дни для напоминания:",
        "reminder_updated": "✅ Напоминание: каждые {} дней!",
        "invalid_reminder": "❗ Введите число от 1 до 30.",
        "empty_list": "🛒 Список пуст.",
        "ask_what_to_add": "📥 Что добавить?",
        "already_exists": "⚠️ Товар уже в списке.",
        "added_successfully": "добавлен!",
        "invalid_items": "❗ Неверный ввод. Введите названия товаров.",
        "choose_item_to_delete": "🗑 Выберите товар для удаления:",
        "choose_suggested_items": "🛒 Добавить предложенные товары:",
        "add_selected_items": "➕ Добавить выбранные",
        "added_to_list": "✅ Добавлено:",
        "confirm_update": "✅ Обновить",
        "bulk_edit_title": "🛒 Редактировать товары:",
        "updated_successfully": "✅ Обновлено!",
        "choose_items_to_delete": "🛒 Выберите товары для удаления:",
        "item_deleted_successfully": "✅ {} удален!",
        "invalid_number": "❗ Неверный номер.",
        "item_not_found": "❗ Товар не найден.",
        "all_items_deleted": "✅ Все товары удалены!",
        "confirm_multi_delete": "🗑️ Удалить выбранные",
        "multi_items_deleted": "✅ Выбранные товары удалены!",
        "clear_all_list": "🗑️ Очистить список",
        "add_selected_item": "➕ Добавить выбранное",
        "select_tems_to_add": "🛒 Выберите товары:",
        "added_to_favorites": "✅ {} добавлен в избранное",
        "item_updated": "✏️ Товар обновлен!",
        "update_shopping_list": "⏰ Напоминание: обновите список! /list",
        "edit_item_text": "🛒 Редактирование:\n\nКол-во: {quantity}\nЕд.: {unit}",
        "command_start": "🚀 Старт",
        "command_add": "➕ Добавить",
        "command_list": "📋 Показать список",
        "command_delete": "🗑️ Удалить",
        "command_suggest": "💡 Предложения",
        "command_edit": "✏️ Редактировать",
        "command_reminder": "⏰ Напоминания",
        "decrease_button": "➖",
        "increase_button": "➕",
        "change_unit_button": "{unit}",
        "back_button": "🔙 Назад",
        "add_new_name": "➕ Новое имя",
        "add_new_item_name": "✏️ Введите новое имя:",
        "edit_item": "📝 Редактировать",
        "response_added": "✅ Добавлено:\n{items}",
        "response_skipped": "⚠️ Уже существует:\n{items}"
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
    lang_texts = TEXTS.get(lang, TEXTS[DEFAULT_LANG])
    if key not in lang_texts:
        logging.warning(f"Missing key '{key}' in language '{lang}'")
    return lang_texts.get(key, TEXTS[DEFAULT_LANG].get(key, f"[{key}]"))


def available_languages():
    """Return the available languages for user selection"""
    return {
        "🇺🇸 English": "en",
        "🇮🇱 עברית": "he",
        "🇷🇺 Русский": "ru",
    }