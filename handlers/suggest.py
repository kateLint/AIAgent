# handlers/suggest.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from utils.favorites import list_favorites, delete_favorite, initialize_favorites
from utils.db import  add_item, item_exists
from utils.lang import get_text
from utils.favorites import add_favorite, edit_favorite

DEFAULT_UNIT = 'pcs'


async def handle_suggest_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id

    selected = context.user_data.get("selected_suggested_items", [])
    context.user_data.setdefault("suggest_edit_mode", False)

    # ✏️ בחירת מוצר
    if data.startswith("select_suggest:"):
        item = data.split(":")[1]
        if item in selected:
            selected.remove(item)
        else:
            selected.append(item)
        context.user_data["selected_suggested_items"] = selected
        await send_suggest_buttons(update, context)

    # ➕ אישור הוספה
    elif data == "confirm_suggest":
        added = []
        for item_name in selected:
            if not item_exists(chat_id, item_name):
                add_item(chat_id, item_name, quantity=1, unit=DEFAULT_UNIT)
                added.append(item_name)

        context.user_data["selected_suggested_items"] = []
        if added:
            await query.edit_message_text(get_text(chat_id, "updated_successfully") + "\n" + "\n".join(f"- {name}" for name in added))
        else:
            await query.edit_message_text(get_text(chat_id, "no_items_added"))

    # 🖋 עריכת מוצר
    elif data.startswith("edit_fav:"):
        fav_id = int(data.split(":")[1])
        context.user_data["mode"] = "awaiting_edit_fav"
        context.user_data["edit_fav_id"] = fav_id
        await query.edit_message_text(f"add_new_item_name")

    # 🗑 מחיקת מוצר
    elif data.startswith("delete_fav:"):
        fav_id = int(data.split(":")[1])
        delete_favorite(chat_id, fav_id)
        await send_suggest_buttons(update, context)

    # ➕ הוספת מוצר חדש
    elif data == "add_fav":
        context.user_data["mode"] = "awaiting_add_fav"
        await query.edit_message_text(f"add_new_name")

    # 📝 החלפת מצב עריכה
    elif data == "edit_suggest_toggle":
        context.user_data["suggest_edit_mode"] = not context.user_data.get("suggest_edit_mode", False)
        await send_suggest_buttons(update, context)

    else:
        await query.edit_message_text(get_text(chat_id, "unknown_command"))
           
            
async def send_suggest_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, edit_mode: bool = False):
    chat_id = update.effective_chat.id
    initialize_favorites(chat_id)

    # אם לא קיים במשתמש, נקבע False
    context.user_data.setdefault("suggest_edit_mode", False)

    favorites = list_favorites(chat_id)
    selected = context.user_data.get("selected_suggested_items", [])

    keyboard = []
    for fav_id, name in favorites:
        row = [
            InlineKeyboardButton(
                f"✅ {name}" if name in selected else f"⬜ {name}",
                callback_data=f"select_suggest:{name}"
            )
        ]
        # אם אנחנו במצב עריכה, נוסיף גם עיפרון ומחיקה
        if context.user_data["suggest_edit_mode"]:
            row.append(InlineKeyboardButton("🖋", callback_data=f"edit_fav:{fav_id}"))
            row.append(InlineKeyboardButton("🗑", callback_data=f"delete_fav:{fav_id}"))
        keyboard.append(row)

    if selected:
        keyboard.append([
            InlineKeyboardButton(get_text(chat_id, "add_selected_items"), callback_data="confirm_suggest")
        ])

    # אם במצב עריכה נוסיף כפתור "➕ הוסף מוצר חדש"
    if context.user_data["suggest_edit_mode"]:
        keyboard.append([
            InlineKeyboardButton("command_add", callback_data="add_fav")
        ])

    # תמיד נוסיף כפתור "עריכה ✏️" שמחליף מצב
    keyboard.append([
        InlineKeyboardButton("edit_item" if not context.user_data["suggest_edit_mode"] else "updated_successfully", callback_data="edit_suggest_toggle")
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text(get_text(chat_id, "choose_suggested_items"), reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(get_text(chat_id, "choose_suggested_items"), reply_markup=reply_markup)

            
async def handle_edit_mode_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["suggest_edit_mode"] = not context.user_data.get("suggest_edit_mode", False)
    await send_suggest_buttons(update, context)

            