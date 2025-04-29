import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import db
from utils.lang import get_text
from utils.common import format_item_display, toggle_unit

# --- Edit Memory ---
user_edit_state = {}

async def send_bulk_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    items = db.list_items_with_ids(chat_id)

    if not items:
        await update.message.reply_text(get_text(chat_id, "empty_list"))
        return

    context.user_data["edit_bulk"] = {
        item_id: {"name": item_name, "quantity": quantity, "unit": unit}
        for item_id, item_name, quantity, unit in items
    }
    await render_bulk_edit(update, context)

async def render_bulk_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    edit_bulk = context.user_data.get("edit_bulk", {})

    if not edit_bulk:
        return

    keyboard = [
        [
            InlineKeyboardButton(data['name'], callback_data="noop"),
            InlineKeyboardButton(get_text(chat_id, "decrease_button"), callback_data=f"bulk_decrease:{item_id}"),
            InlineKeyboardButton(str(data['quantity']), callback_data="noop"),
            InlineKeyboardButton(get_text(chat_id, "increase_button"), callback_data=f"bulk_increase:{item_id}"),
            InlineKeyboardButton(get_text(chat_id, "change_unit_button").format(unit=data['unit']),callback_data=f"bulk_change_unit:{item_id}")
        ]
        for item_id, data in edit_bulk.items()
    ]

    keyboard.append([
        InlineKeyboardButton(get_text(chat_id, "confirm_update"), callback_data="bulk_confirm")
    ])

    text = get_text(chat_id, "bulk_edit_title")

    if update.callback_query:
        await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_bulk_edit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = update.effective_chat.id

    edit_bulk = context.user_data.get("edit_bulk", {})

    if data == "noop":
        return

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
                formatted = format_item_display(item_row, chat_id)
                message += f"{idx}. {formatted}\n"
            await query.message.reply_text(message.strip())
        else:
            await query.message.reply_text(get_text(chat_id, "empty_list"))

        context.user_data.pop("edit_bulk", None)
        return

    context.user_data["edit_bulk"] = edit_bulk
    await render_bulk_edit(update, context)

async def handle_edit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id

    edit_items = context.user_data.get("edit_items", {})

    if data.startswith("edit_select:"):
        item_id = int(data.split(":")[1])
        quantity = edit_items[item_id]["quantity"]
        unit = edit_items[item_id]["unit"]

        keyboard = [
            [
                InlineKeyboardButton(get_text(chat_id, "decrease_button"), callback_data=f"edit_decrease:{item_id}"),
                InlineKeyboardButton(get_text(chat_id, "increase_button"), callback_data=f"edit_increase:{item_id}"),
                InlineKeyboardButton(get_text(chat_id, "change_unit_button"), callback_data=f"edit_change_unit:{item_id}")
            ],
            [InlineKeyboardButton(get_text(chat_id, "back_button"), callback_data="edit_back")]
        ]

        await query.edit_message_text(
            text=get_text(chat_id, "edit_item_text").format(quantity=quantity, unit=unit),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("edit_decrease:") or data.startswith("edit_increase:") or data.startswith("edit_change_unit:"):
        item_id = int(data.split(":")[1])
        item = edit_items.get(item_id, {"quantity": 1, "unit": "יח׳"})

        if data.startswith("edit_decrease:") and item["quantity"] > 1:
            item["quantity"] -= 1
        elif data.startswith("edit_increase:"):
            item["quantity"] += 1
        elif data.startswith("edit_change_unit:"):
            item["unit"] = toggle_unit(chat_id, item["unit"])

        edit_items[item_id] = item
        context.user_data["edit_items"] = edit_items

        await handle_edit_callback(update, context)

    elif data == "edit_back":
        await send_bulk_edit(update, context)

    elif data == "edit_confirm":
        for item_id, values in edit_items.items():
            db.update_item_quantity_and_unit(chat_id, item_id, values["quantity"], values["unit"])

        await query.edit_message_text(get_text(chat_id, "updated_successfully"))
