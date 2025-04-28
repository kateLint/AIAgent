from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import db
from utils.lang import get_text
from utils.db import clear_items


async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_delete_buttons(update, context)

async def handle_delete(update: Update, context: ContextTypes.DEFAULT_TYPE, forced_text: str = None):
    chat_id = update.effective_chat.id
    text = forced_text or update.message.text.strip()

    if context.user_data.get("mode") != "awaiting_delete":
        return

    rows = db.list_items(chat_id)  # [(id, item_name, quantity, unit)]

    if not rows:
        await update.message.reply_text(get_text(chat_id, "empty_list"))
        context.user_data.pop("mode", None)
        return

    try:
        index = int(text) - 1
        if 0 <= index < len(rows):
            item_id, item_name, quantity, unit = rows[index]
            db.delete_item(chat_id, item_id)
            await update.message.reply_text(get_text(chat_id, "item_deleted_successfully").format(item_name=item_name))
        else:
            await update.message.reply_text(get_text(chat_id, "invalid_number"))
    except ValueError:
        found = False
        clean_text = text.strip().lower()
        for item_id, item_name, quantity, unit in rows:
            if item_name.lower() == clean_text:
                db.delete_item(chat_id, item_id)
                await update.message.reply_text(get_text(chat_id, "item_deleted_successfully").format(item_name=item_name))
                found = True
                break
        if not found:
            await update.message.reply_text(get_text(chat_id, "item_not_found"))

    context.user_data.pop("mode", None)

async def send_delete_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    rows = db.list_items(chat_id)

    # ⬇️ ADD this part: Clear all list button at the bottom
    keyboard.append([
        InlineKeyboardButton(get_text(chat_id, "clear_all_list"), callback_data="clear_all_items")
    ])
    
    if not rows:
        await update.message.reply_text(get_text(chat_id, "empty_list"))
        return

    keyboard = []
    temp_row = []
    for item_id, item_name, quantity, unit in rows:
        display_text = f"{item_name} {quantity} {unit}"
        button = InlineKeyboardButton(f"🗑 {display_text}", callback_data=f"delete_item:{item_id}")
        temp_row.append(button)
        if len(temp_row) == 2:
            keyboard.append(temp_row)
            temp_row = []

    if temp_row:
        keyboard.append(temp_row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(get_text(chat_id, "choose_item_to_delete"), reply_markup=reply_markup)


async def handle_delete_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    data = query.data

    if data.startswith("delete_item:"):
        item_id = int(data.split(":")[1])
        db.delete_item(chat_id, item_id)

        # Reload updated list
        rows = db.list_items(chat_id)
        if not rows:
            await query.edit_message_text(get_text(chat_id, "all_items_deleted"))
        else:
            keyboard = []
            temp_row = []
            for item_id, item_name, quantity, unit in rows:
                display_text = f"{item_name} {quantity} {unit}"
                button = InlineKeyboardButton(f"🗑 {display_text}", callback_data=f"delete_item:{item_id}")
                temp_row.append(button)
                if len(temp_row) == 2:
                    keyboard.append(temp_row)
                    temp_row = []
            if temp_row:
                keyboard.append(temp_row)
            
            # ➡️ ADD "Clear All List" button at the end
            keyboard.append([
                InlineKeyboardButton(get_text(chat_id, "clear_all_list"), callback_data="clear_all_items")
            ])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(get_text(chat_id, "choose_item_to_delete"), reply_markup=reply_markup)

    elif data == "clear_all_items":
        db.clear_items(chat_id)
        await query.edit_message_text(get_text(chat_id, "cleared"))


async def send_multi_select_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    rows = db.list_items(chat_id)

    if not rows:
        await update.message.reply_text(get_text(chat_id, "empty_list"))
        return

    selected = context.user_data.get("selected_items_for_delete", [])

    keyboard = []
    temp_row = []

    for item_id, item_name, quantity, unit in rows:
        prefix = "✅" if item_id in selected else "⬜"
        display_text = f"{item_name} {quantity} {unit}"
        button = InlineKeyboardButton(f"{prefix} {display_text}", callback_data=f"select_item:{item_id}")
        temp_row.append(button)
        if len(temp_row) == 2:
            keyboard.append(temp_row)
            temp_row = []

    if temp_row:
        keyboard.append(temp_row)


    # ✅ אם יש פריטים נבחרים נוסיף גם כפתור "אשר מחיקה מרובה"
    if selected:
        keyboard.append([
            InlineKeyboardButton(get_text(chat_id, "confirm_multi_delete"), callback_data="confirm_delete")
        ])
        
    # ✅ תמיד נוסיף את כפתור "נקה את כל הרשימה"
    keyboard.append([
        InlineKeyboardButton(get_text(chat_id, "clear_all_list"), callback_data="clear_all_items")
    ])



    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(get_text(chat_id, "choose_items_to_delete"), reply_markup=reply_markup)



async def handle_multi_select_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    data = query.data

    # שליפת הרשימה הנוכחית של פריטים
    rows = db.list_items(chat_id)

    # שליפת מצב הפריטים שנבחרו
    selected = context.user_data.get("selected_items_for_delete", [])

    # לחיצה על פריט כדי לבחור/לבטל בחירה
    if data.startswith("select_item:"):
        item_id = int(data.split(":")[1])
        if item_id in selected:
            selected.remove(item_id)
        else:
            selected.append(item_id)

        context.user_data["selected_items_for_delete"] = selected

        # בנייה מחודשת של המקלדת עם הפריטים המעודכנים
        reply_markup = build_delete_keyboard(chat_id, selected)
        await query.edit_message_text(get_text(chat_id, "choose_items_to_delete"), reply_markup=reply_markup)

    # אישור מחיקה מרובה
    elif data == "confirm_delete":
        if selected:
            for item_id in selected:
                db.delete_item(chat_id, item_id)

            context.user_data["selected_items_for_delete"] = []
            await query.edit_message_text(get_text(chat_id, "multi_items_deleted"))
        else:
            await query.edit_message_text(get_text(chat_id, "no_items_selected"))

    # מחיקה של כל הרשימה
    elif data == "clear_all_items":
        db.clear_items(chat_id)
        await query.edit_message_text(get_text(chat_id, "cleared"))

    else:
        await query.edit_message_text(get_text(chat_id, "unknown_action"))



def build_delete_keyboard(chat_id, selected):
    rows = db.list_items(chat_id)

    keyboard = []
    temp_row = []

    for item_id, item_name, quantity, unit in rows:
        prefix = "✅" if item_id in selected else "⬜"
        display_text = f"{item_name} {quantity} {unit}"
        button = InlineKeyboardButton(f"{prefix} {display_text}", callback_data=f"select_item:{item_id}")
        temp_row.append(button)
        if len(temp_row) == 2:
            keyboard.append(temp_row)
            temp_row = []

    if temp_row:
        keyboard.append(temp_row)

    # ✅ אם יש פריטים נבחרים — נוסיף גם כפתור "אשר מחיקה מרובה"
    if selected:
        keyboard.append([
            InlineKeyboardButton(get_text(chat_id, "confirm_multi_delete"), callback_data="confirm_delete")
        ])
        
    # ✅ תמיד נכניס כפתור "נקה את כל הרשימה"
    keyboard.append([
        InlineKeyboardButton(get_text(chat_id, "clear_all_list"), callback_data="clear_all_items")
    ])


    return InlineKeyboardMarkup(keyboard)
