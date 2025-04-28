# handlers/edit.py
import re
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from utils import db
from utils.lang import get_text
from utils.common import format_item_display, toggle_unit

# --- Memory for edit mode ---
user_edit_state = {}



from utils.lang import get_language

async def send_bulk_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    items = db.list_items_with_ids(chat_id)

    if not items:
        await update.message.reply_text(get_text(chat_id, "empty_list"))
        return

    # Initialize edit state
    context.user_data["edit_bulk"] = {}
    for item_row in items:
        item_id, item_name, quantity, unit = item_row
        context.user_data["edit_bulk"][item_id] = {
            "name": item_name,
            "quantity": quantity,
            "unit": unit
        }

    await render_bulk_edit(update, context)




# handlers/edit.py

async def render_bulk_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    edit_bulk = context.user_data.get("edit_bulk", {})

    if not edit_bulk:
        return

    keyboard = []

    for item_id, data in edit_bulk.items():
        row = [
            InlineKeyboardButton(f"{data['name']}", callback_data="noop"),  # Name is static
            InlineKeyboardButton("➖", callback_data=f"bulk_decrease:{item_id}"),  # Decrease
            InlineKeyboardButton(f"{data['quantity']}", callback_data="noop"),  # Quantity is static
            InlineKeyboardButton("➕", callback_data=f"bulk_increase:{item_id}"),  # Increase
            InlineKeyboardButton(f"{data['unit']}", callback_data=f"bulk_change_unit:{item_id}")  # Unit change
        ]
        keyboard.append(row)

    # Confirm Button
    keyboard.append([InlineKeyboardButton(get_text(chat_id, "confirm_update"), callback_data="bulk_confirm")])

    full_text = get_text(chat_id, "bulk_edit_title")

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=full_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            text=full_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# handlers/edit.py

async def handle_bulk_edit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    chat_id = update.effective_chat.id

    if data == "noop":
        await query.answer()
        return

    await query.answer()

    edit_bulk = context.user_data.get("edit_bulk", {})

    if data.startswith("bulk_decrease:"):
        item_id = int(data.split(":")[1])
        if edit_bulk[item_id]["quantity"] > 1:
            edit_bulk[item_id]["quantity"] -= 1

    elif data.startswith("bulk_increase:"):
        item_id = int(data.split(":")[1])
        edit_bulk[item_id]["quantity"] += 1

    elif data.startswith("bulk_change_unit:"):
        item_id = int(data.split(":")[1])
        current = edit_bulk[item_id]["unit"]
        edit_bulk[item_id]["unit"] = toggle_unit(chat_id, current)

    elif data == "bulk_confirm":
        for item_id, item_data in edit_bulk.items():
            db.update_item(chat_id, item_id, item_data["quantity"], item_data["unit"])

        await query.edit_message_text(get_text(chat_id, "updated_successfully"))

        items = db.list_items(chat_id)

        if items:
            message = get_text(chat_id, "list_title") + "\n\n"
            for idx, item_row in enumerate(items, start=1):
                formatted_item = format_item_display(item_row, chat_id)
                message += f"{idx}. {formatted_item}\n"
            await query.message.reply_text(message.strip())
        else:
            await query.message.reply_text(get_text(chat_id, "empty_list"))

        context.user_data.pop("edit_bulk", None)
        return

    context.user_data["edit_bulk"] = edit_bulk
    await render_bulk_edit(update, context)

  
async def send_single_select_edit(update, context):
    chat_id = update.effective_chat.id
    items = db.list_items_with_ids(chat_id)

    if not items:
        await update.message.reply_text("📭 אין פריטים ברשימה!")
        return

    context.user_data["edit_selected_item"] = None
    keyboard = []

    for item_id, item_name in items:
        button = InlineKeyboardButton(f"⬜ {item_name}", callback_data=f"select_edit_item:{item_id}")
        keyboard.append([button])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("🛒 בחרי פריט לעריכה:", reply_markup=reply_markup)

async def handle_single_edit_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id

    if data.startswith("select_edit_item:"):
        item_id = int(data.split(":")[1])
        context.user_data["edit_selected_item"] = {"id": item_id, "quantity": 1, "unit": "יח׳"}

        keyboard = [
            [
                InlineKeyboardButton("➖", callback_data="edit_decrease"),
                InlineKeyboardButton("➕", callback_data="edit_increase"),
                InlineKeyboardButton("🔁 שנה יחידה", callback_data="edit_change_unit"),
            ],
            [InlineKeyboardButton("✅ סיום", callback_data="edit_confirm")]
        ]

        await query.edit_message_text(
            text=f"🛒 עריכה:\nכמות: 1\nיחידה: יח׳",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data in ["edit_decrease", "edit_increase", "edit_change_unit"]:
        selected = context.user_data.get("edit_selected_item")
        if not selected:
            await query.answer("בחר קודם פריט!")
            return

        if data == "edit_decrease" and selected["quantity"] > 1:
            selected["quantity"] -= 1
        elif data == "edit_increase":
            selected["quantity"] += 1
        elif data == "edit_change_unit":
            selected["unit"] = "ק״ג" if selected["unit"] == "יח׳" else "יח׳"

        context.user_data["edit_selected_item"] = selected

        keyboard = [
            [
                InlineKeyboardButton("➖", callback_data="edit_decrease"),
                InlineKeyboardButton("➕", callback_data="edit_increase"),
                InlineKeyboardButton("🔁 שנה יחידה", callback_data="edit_change_unit"),
            ],
            [InlineKeyboardButton("✅ סיום", callback_data="edit_confirm")]
        ]

        await query.edit_message_text(
            text=f"🛒 עריכה:\nכמות: {selected['quantity']}\nיחידה: {selected['unit']}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "edit_confirm":
        selected = context.user_data.get("edit_selected_item")
        if not selected:
            await query.answer("לא נבחר פריט!")
            return

        db.update_item_quantity_and_unit(chat_id, selected["id"], selected["quantity"], selected["unit"])
        await query.edit_message_text("✅ הפריט עודכן בהצלחה!")

        context.user_data["edit_selected_item"] = None

async def send_edit_list(update, context):
    chat_id = update.effective_chat.id
    rows = db.list_items_with_ids(chat_id)  # נחזיר [(id, item_name)]

    if not rows:
        await update.message.reply_text(get_text(chat_id, "empty_list"))
        return

    context.user_data["edit_items"] = {}

    keyboard = []
    temp_row = []

    for item_id, item_name in rows:
        context.user_data["edit_items"][item_id] = {"quantity": 1, "unit": "יח׳"}
        button = InlineKeyboardButton(
            f"📝 {item_name} | 1 יח׳", callback_data=f"edit_select:{item_id}"
        )
        temp_row.append(button)
        if len(temp_row) == 1:
            keyboard.append(temp_row)
            temp_row = []

    if temp_row:
        keyboard.append(temp_row)

    keyboard.append([InlineKeyboardButton("✅ סיים עדכון", callback_data="edit_confirm")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(get_text(chat_id, "edit_list_title"), reply_markup=reply_markup)

async def handle_edit_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id

    edit_items = context.user_data.get("edit_items", {})

    if data.startswith("edit_select:"):
        item_id = int(data.split(":")[1])

        keyboard = [
            [
                InlineKeyboardButton("➖", callback_data=f"edit_decrease:{item_id}"),
                InlineKeyboardButton("➕", callback_data=f"edit_increase:{item_id}"),
                InlineKeyboardButton("🔁 שנה יחידה", callback_data=f"edit_change_unit:{item_id}"),
            ],
            [InlineKeyboardButton("🔙 חזור", callback_data="edit_back")]
        ]

        quantity = edit_items[item_id]["quantity"]
        unit = edit_items[item_id]["unit"]

        await query.edit_message_text(
            text=f"🛒 עריכה של פריט:\n\nכמות: {quantity}\nיחידה: {unit}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("edit_decrease:") or data.startswith("edit_increase:") or data.startswith("edit_change_unit:"):
        item_id = int(data.split(":")[1])
        item = edit_items.get(item_id, {"quantity": 1, "unit": "יח׳"})

        if data.startswith("edit_decrease:"):
            if item["quantity"] > 1:
                item["quantity"] -= 1
        elif data.startswith("edit_increase:"):
            item["quantity"] += 1
        elif data.startswith("edit_change_unit:"):
            item["unit"] = "ק״ג" if item["unit"] == "יח׳" else "יח׳"

        edit_items[item_id] = item
        context.user_data["edit_items"] = edit_items

        keyboard = [
            [
                InlineKeyboardButton("➖", callback_data=f"edit_decrease:{item_id}"),
                InlineKeyboardButton("➕", callback_data=f"edit_increase:{item_id}"),
                InlineKeyboardButton("🔁 שנה יחידה", callback_data=f"edit_change_unit:{item_id}"),
            ],
            [InlineKeyboardButton("🔙 חזור", callback_data="edit_back")]
        ]

        await query.edit_message_text(
            text=f"🛒 עריכה של פריט:\n\nכמות: {item['quantity']}\nיחידה: {item['unit']}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "edit_back":
        await send_edit_list(update, context)

    elif data == "edit_confirm":
        for item_id, values in edit_items.items():
            db.update_item_quantity_and_unit(chat_id, item_id, values["quantity"], values["unit"])

        await query.edit_message_text("✅ כל הפריטים עודכנו בהצלחה!")


async def edit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    items = list_items(chat_id)

    if not items:
        await update.message.reply_text(get_text(chat_id, "empty_list"))
        return

    # שליחת רשימה עם כפתור ℹ️ עזרה
    numbered_list = "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
    await update.message.reply_text(
        f"📝 {get_text(chat_id, 'list_title')}\n\n{numbered_list}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("ℹ️ How to edit", callback_data="edit_info")]
        ])
    )

    user_edit_state[chat_id] = {
        "items": items,
        "mode": "awaiting_edit_input"
    }

async def handle_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id not in user_edit_state:
        await update.message.reply_text("❗ No edit session found. Please use /edit first.")
        return

    state = user_edit_state[chat_id]
    items = state["items"]

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    text = update.message.text.strip()
    if not text:
        await update.message.reply_text(get_text(chat_id, "invalid_items"))
        return

    # זיהוי פורמט
    text = text.replace(",", " ")
    tokens = text.split()

    if len(tokens) % 2 != 0:
        await update.message.reply_text("⚠️ Invalid format. Every item must have a quantity.")
        return

    updated_items = []
    failed_items = []

    for i in range(0, len(tokens), 2):
        first = tokens[i]
        second = tokens[i+1]

        if first.isdigit():
            # לפי מספר
            idx = int(first) - 1
            if 0 <= idx < len(items):
                item_name = items[idx]
                qty = int(second)
                new_name = update_item_quantity(chat_id, item_name, qty)
                if new_name:
                    updated_items.append(new_name)
                else:
                    failed_items.append(item_name)
            else:
                failed_items.append(first)
        else:
            # לפי שם
            item_name = first
            qty = int(second)
            new_name = update_item_quantity(chat_id, item_name, qty)
            if new_name:
                updated_items.append(new_name)
            else:
                failed_items.append(item_name)

    response = ""
    if updated_items:
        response += "✅ Updated:\n" + "\n".join(f"- {itm}" for itm in updated_items) + "\n"
    if failed_items:
        response += "⚠️ Failed to update:\n" + "\n".join(f"- {itm}" for itm in failed_items)

    await update.message.reply_text(response.strip())

    # סיום מצב עריכה
    del user_edit_state[chat_id]
