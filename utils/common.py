# utils/common.py
from functools import wraps
from telegram import Update
from utils.lang import get_language
import re

def send_typing_action(func):
    @wraps(func)
    async def wrapper(update: Update, context):
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        return await func(update, context)
    return wrapper

 # utils/common.py

UNIT_TRANSLATIONS = {
    "he": {
        "יח׳": "יח׳",
        "ק״ג": "ק״ג",
    },
    "en": {
        "יח׳": "pcs",
        "ק״ג": "kg",
    }
}



def clean_item_name(name: str) -> str:
    """
    מנקה שם פריט:
    - מסיר כמות בהתחלה (כגון '2 ×')
    - מסיר יחידה בסוף (כגון 'יח׳' או 'ק״ג')
    """
    name = name.strip()
    name = re.sub(r"^\d+\s*[×x]\s*", "", name)  # הסרת כמות בהתחלה
    name = re.sub(r"\s*(יח׳|ק״ג)$", "", name)  # הסרת יחידה בסוף
    return name.strip()

def translate_unit(unit: str, chat_id: int) -> str:
    """
    מתרגם יחידה לפי השפה של הצ'אט.
    """
    lang = get_language(chat_id)
    return UNIT_TRANSLATIONS.get(lang, UNIT_TRANSLATIONS["en"]).get(unit, unit)



# utils/common.py

def format_item_display(item_row, chat_id: int) -> str:
    """
    Format a shopping list item for display.
    """
    id, item_name, quantity, unit = item_row
    translated_unit = translate_unit(unit, chat_id)

    if quantity > 1:
        return f"{item_name} {quantity} {translated_unit}"
    else:
        return f"{item_name} 1 {translated_unit}"
    


def toggle_unit(chat_id: int, current_unit: str) -> str:
    """
    מחליף יחידה בין יח׳/ק״ג או pcs/kg לפי שפת המשתמש.
    """
    lang = get_language(chat_id)
    if lang == "he":
        return "ק״ג" if current_unit == "יח׳" else "יח׳"
    else:
        return "kg" if current_unit == "pcs" else "pcs"
