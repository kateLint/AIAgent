# utils/lang.py
import sqlite3
import logging
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
"add_selected_item": "➕ Add selected item",
"select_tems_to_add": "🛒 Select items to add:",
"added_to_favorites": "✅ {item_name} added to favorites",
"item_updated":"✏️ Item updated successfully!",
"update_shopping_list":"⏰ Reminder: Update your shopping list! /list",
"edit_item_text": "🛒 Editing item:\n\nQuantity: {quantity}\nUnit: {unit}",
"command_start": "🚀 Start the bot",
"command_add": "➕ Add an item",
"command_list": "📋 Show shopping list",
"command_delete": "🗑️ Delete an item",
"command_suggest": "💡 Suggest basics",
"command_edit": "✏️ Edit quantities",
"command_reminder": "⏰ Manage reminders",
# אנגלית
"decrease_button": "➖",
"increase_button": "➕",
"change_unit_button": "{unit}",
"back_button": "⬅️ Back",
"confirm_update": "✅ Confirm Update",
"bulk_edit_title": "🛒 Edit your shopping list:",
"updated_successfully": "✅ Items updated successfully!",
"edit_item_text": "🛒 Editing item:\n\nQuantity: {quantity}\nUnit: {unit}",
"add_new_name": "➕ Add a new name",
"add_new_item_name":"✏️ Enter the new name for the item:",
"edit_item":"📝 Edit",
"response_added":"✅ Added:\n{items}",
"response_skipped":"⚠️ Already exists:\n{items}",
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
"add_selected_item": "➕ הוסף מוצר חדש",
"select_tems_to_add": "🛒בחר מוצרים להוספה :",
"added_to_favorites": "✅ {item_name} הוספת פריט למועדפים",
"item_updated":"✏️ הפריט עודכן בהצלחה!",
"update_shopping_list":"⏰ תזכורת: עדכן את רשימת הקניות שלך! /list",
"edit_item_text": "🛒 עריכה של פריט:\n\nכמות: {quantity}\nיחידה: {unit}",
"decrease_button": "➖",
"increase_button": "➕",
"change_unit_button": "{unit}",
"back_button": "🔙 חזור",
"command_start": "🚀 התחל את הבוט",
"command_add": "➕ הוסף פריט",
"command_list": "📋 הצג רשימת קניות",
"command_delete": "🗑️ מחק פריט",
"command_suggest": "💡 הצע מוצרים בסיסיים",
"command_edit": "✏️ ערוך כמויות",
"command_reminder": "⏰ נהל תזכורות",
"add_new_name": "➕ הוסף שם חדש",
"add_new_item_name":"✏️ כתוב את השם החדש לפריט:",
"edit_item":"📝 עריכה",
"response_added":"✅ נוספו:\n{items}",
"response_skipped":"⚠️ כבר קיימים:\n{items}"}, 
    "ru":{
        "choose_language": "🌐 Пожалуйста, выберите язык:",
        "language_selected": "✅ Язык успешно выбран!",
        "start_message": "👋 Добро пожаловать! Я ваш помощник по покупкам.",
        "list_title": "Общий список покупок:",
        "nothing_deleted": "Нет удаленных элементов.",
        "cleared": "✅ Список покупок очищен!",
        "current_reminder": "Текущая напоминалка: каждые {} дней.",
        "send_new_reminder": "📅 Отправьте новое количество дней для обновления напоминания.",
        "reminder_updated": "✅ Напоминание обновлено на каждые {} дней!",
                "empty_list": "🛒 Ваш список покупок сейчас пуст.",
                "ask_what_to_add": "📥 Что вы хотите добавить?",
        "already_exists": "⚠️ Этот элемент уже существует в вашем списке.",
        "added_successfully": "успешно добавлено!",
        "invalid_items": "❗ Неверный ввод. Пожалуйста, отправьте названия элементов.",
        "invalid_reminder": "❗ Пожалуйста, отправьте число от 1 до 30.",
        "choose_item_to_delete": "🗑 Выберите элемент для удаления:",
                "choose_suggested_items": "🛒 Выберите предложенные элементы для добавления:",
        "add_selected_items": "➕ Добавить выбранные элементы",
        "added_to_list": "✅ Добавлено в список:",
        "confirm_update": "✅ Обновить",
        "bulk_edit_title": "🛒 Редактирование списка покупок:\nВыберите элемент и обновите количество и единицу измерения",
        "updated_successfully": "✅ Успешно обновлено!",
        "choose_items_to_delete": "🛒 Выберите элементы для удаления:",
"item_deleted_successfully": "✅ {item_name} успешно удален!",
"invalid_number": "❗ Неверный номер. Пожалуйста, попробуйте снова.",
"item_not_found": "❗ Элемент не найден. Пожалуйста, попробуйте снова.",
"all_items_deleted": "✅ Все элементы удалены!",
"confirm_multi_delete": "🗑️ Удалить выбранные элементы",    
"multi_items_deleted": "✅ Выбранные элементы успешно удалены!",
"clear_all_list": "🗑️ Очистить весь список",
"add_selected_item": "➕ Добавить выбранный элемент",
"select_tems_to_add": "🛒 Выберите элементы для добавления:",
"added_to_favorites": "✅ {item_name} добавлен в избранное",
"item_updated":"✏️ Элемент успешно обновлен!",
"update_shopping_list":"⏰ Напоминание: обновите свой список покупок! /list",
"edit_item_text": "🛒 Редактирование элемента:\n\nКоличество: {quantity}\nЕдиница: {unit}" ,    
"command_start": "🚀 Начать бота",  
"command_add": "➕ Добавить элемент",
"command_list": "📋 Показать список покупок",
"command_delete": "🗑️ Удалить элемент",
"command_suggest": "💡 Предложить основы",
"command_edit": "✏️ Изменить количество",
"command_reminder": "⏰ Управление напоминаниями",
"decrease_button": "➖",
"increase_button": "➕",
"change_unit_button": "{unit}",     
"back_button": "🔙 Назад",
"confirm_update": "✅ Подтвердить обновление",
"bulk_edit_title": "🛒 Редактировать ваш список покупок:",
"updated_successfully": "✅ Элементы успешно обновлены!",
"edit_item_text": "🛒 Редактирование элемента:\n\nКоличество: {quantity}\nЕдиница: {unit}",
"add_new_name": "➕ Добавить новое имя",
"add_new_item_name":"✏️ Введите новое имя для элемента:",   
"edit_item":"📝 Редактировать",
"response_added":"✅ Добавлено:\n{items}",
"response_skipped":"⚠️ Уже существует:\n{items}"



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
