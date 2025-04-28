# utils/db.py
import sqlite3
import logging
import re
from datetime import datetime

DB_PATH = "shopping_list.db"

# utils/db.py

def create_tables():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Chats table (already exists)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id INTEGER PRIMARY KEY,
                chat_type TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reminder_days INTEGER DEFAULT 3
            )
        """)

        # New shopping table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shopping (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                unit TEXT DEFAULT 'pcs',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(chat_id) REFERENCES chats(chat_id)
            )
        """)
        conn.commit()


def add_chat(chat_id: int, chat_type: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO chats (chat_id, chat_type) VALUES (?, ?)
        """, (chat_id, chat_type))
        conn.commit()

def update_language(chat_id: int, lang: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE chats SET language = ? WHERE chat_id = ?
        """, (lang, chat_id))
        conn.commit()

def update_last_update(chat_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE chats SET last_update = CURRENT_TIMESTAMP WHERE chat_id = ?
        """, (chat_id,))
        conn.commit()

def set_reminder_days(chat_id: int, days: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE chats SET reminder_days = ? WHERE chat_id = ?
        """, (days, chat_id))
        conn.commit()

def get_chat_settings(chat_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row  # Make rows behave like dicts
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chats WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        else:
            return {}

    
def update_item_quantity_and_unit(chat_id: int, item_id: int, quantity: int, unit: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT item FROM shopping WHERE chat_id = ? AND id = ?", (chat_id, item_id))
        row = cursor.fetchone()

        if row:
            base_name = row["item"]
            new_item = f"{quantity} × {base_name} ({unit})"
            cursor.execute("UPDATE shopping SET item = ? WHERE id = ?", (new_item, item_id))
            conn.commit()


def update_item_quantity_and_unit(chat_id: int, item_id: int, quantity: int, unit: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT item FROM shopping WHERE chat_id = ? AND id = ?
        """, (chat_id, item_id))
        row = cursor.fetchone()

        if row:
            base_name = row["item"]
            new_item = f"{quantity} × {base_name} ({unit})"
            cursor.execute("""
                UPDATE shopping SET item = ? WHERE id = ?
            """, (new_item, item_id))
            conn.commit()
            
def list_items_with_ids(chat_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, item_name, quantity, unit FROM shopping WHERE chat_id = ?
        """, (chat_id,))
        return cursor.fetchall()


def delete_item_by_id(item_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM shopping WHERE id = ?", (item_id,))
        conn.commit()


def update_item_quantity(chat_id: int, item_name: str, quantity: int):
    base_name = re.sub(r"^\d+\s*[×x]\s*", "", item_name).strip()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, item FROM shopping WHERE chat_id = ?", (chat_id,))
        for row in cursor.fetchall():
            clean_item = re.sub(r"^\d+\s*[×x]\s*", "", row['item']).strip()
            if clean_item == base_name:
                new_name = f"{quantity} × {clean_item}" if quantity > 1 else clean_item
                cursor.execute("UPDATE shopping SET item = ? WHERE id = ?", (new_name, row['id']))
                conn.commit()
                return new_name
        return None

def get_chats_for_reminder():
    now = datetime.now()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chats")
        reminder_list = []
        for row in cursor.fetchall():
            last_update = datetime.strptime(row['last_update'], "%Y-%m-%d %H:%M:%S")
            if (now - last_update).days >= row['reminder_days']:
                reminder_list.append(row['chat_id'])
        return reminder_list

def clear_items(chat_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM shopping WHERE chat_id = ?", (chat_id,))
        conn.commit()


create_tables()



from utils.common import clean_item_name, translate_unit

def update_item_quantity_and_unit(chat_id: int, item_id: int, quantity: int, unit: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # שליפת שם הפריט הקיים
        cursor.execute("SELECT item FROM shopping WHERE id = ? AND chat_id = ?", (item_id, chat_id))
        row = cursor.fetchone()

        if row:
            original_name = row[0]

            # ניקוי שם המוצר
            base_name = clean_item_name(original_name)

            # בניית שם חדש עם יחידה בעברית בלבד!
            if quantity > 1:
                new_name = f"{base_name} {quantity} × {unit}"
            else:
                new_name = f"{base_name} 1 {unit}"

            # עדכון במסד הנתונים
            cursor.execute(
                "UPDATE shopping SET item = ? WHERE id = ? AND chat_id = ?",
                (new_name, item_id, chat_id)
            )
            conn.commit()


# לוודא שהטבלאות קיימות במסד
create_tables()



def clean_item_name(name: str) -> str:
    """Clean item name by removing existing quantities and units."""
    name = name.strip()
    # Remove quantity like "2 ×"
    name = re.sub(r"^\d+\s*[×x]\s*", "", name)
    # Remove trailing units like "יח׳" or "ק״ג" (or others)
    name = re.sub(r"\s*(יח׳|ק״ג)$", "", name)
    name = name.strip()
    return name


#---------------------
def add_item(chat_id: int, item_name: str, quantity: int = 1, unit: str = 'pcs'):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO shopping (chat_id, item_name, quantity, unit) VALUES (?, ?, ?, ?)
        """, (chat_id, item_name, quantity, unit))
        conn.commit()
        
        
def list_items(chat_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, item_name, quantity, unit FROM shopping WHERE chat_id = ?
        """, (chat_id,))
        return cursor.fetchall()  
    
def update_item(chat_id: int, item_id: int, quantity: int = 1, unit: str = 'pcs'):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE shopping SET quantity = ?, unit = ? WHERE id = ? AND chat_id = ?
        """, (quantity, unit, item_id, chat_id))
        conn.commit()          
        
def delete_item(chat_id: int, item_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM shopping WHERE id = ? AND chat_id = ?
        """, (item_id, chat_id))
        conn.commit()

def item_exists(chat_id: int, item_name: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM shopping WHERE chat_id = ? AND item_name = ?
        """, (chat_id, item_name))
        return cursor.fetchone() is not None        