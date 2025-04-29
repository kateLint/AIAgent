# utils/favorites.py

import sqlite3
from typing import List, Tuple

DB_PATH = "shopping_list.db"

DEFAULT_FAVORITES = [
    "Milk", "Bread", "Eggs", "Cheese", "Tomatoes",
    "Cucumbers", "Apples", "Bananas", "Rice", "Pasta"
]

def create_favorites_table():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                item_name TEXT NOT NULL
            )
        """)
        conn.commit()

def initialize_favorites(chat_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM favorites WHERE chat_id = ?", (chat_id,))
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.executemany(
                "INSERT INTO favorites (chat_id, item_name) VALUES (?, ?)",
                [(chat_id, item) for item in DEFAULT_FAVORITES]
            )
            conn.commit()

def list_favorites(chat_id: int) -> List[Tuple[int, str]]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, item_name FROM favorites WHERE chat_id = ? ORDER BY item_name ASC", (chat_id,))
        return cursor.fetchall()

def add_favorite(chat_id: int, item_name: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO favorites (chat_id, item_name) VALUES (?, ?)
        """, (chat_id, item_name))
        conn.commit()

def edit_favorite(chat_id: int, favorite_id: int, new_name: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE favorites SET item_name = ? WHERE id = ? AND chat_id = ?
        """, (new_name, favorite_id, chat_id))
        conn.commit()

def delete_favorite(chat_id: int, favorite_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM favorites WHERE id = ? AND chat_id = ?
        """, (favorite_id, chat_id))
        conn.commit()

# ensure table is created on import
create_favorites_table()