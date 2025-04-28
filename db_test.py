# utils/db.py

import sqlite3
import logging
from pathlib import Path
import sqlite3
import logging
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent.parent / "shopping_list.db"

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS shopping (
                item TEXT,
                category TEXT DEFAULT ''
            )
            """)
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                reminder_days INTEGER DEFAULT 3
            )
            """)
            self.conn.commit()
            logging.info("✅ Tables are ready.")
        except Exception as e:
            logging.error(f"❗ Error creating tables: {e}")

    # --- Items ---
    def add_item(self, item, category=""):
        try:
            self.cursor.execute("INSERT INTO shopping (item, category) VALUES (?, ?)", (item, category))
            self.conn.commit()
        except Exception as e:
            logging.error(f"❗ Error adding item: {e}")

    def list_items(self):
        self.cursor.execute("SELECT item FROM shopping")
        return [row[0] for row in self.cursor.fetchall()]

    def delete_item(self, item):
        self.cursor.execute("DELETE FROM shopping WHERE item = ?", (item,))
        self.conn.commit()

    def item_exists(self, item):
        self.cursor.execute("SELECT 1 FROM shopping WHERE item = ?", (item,))
        return self.cursor.fetchone() is not None

    def update_item_quantity(self, base_item, qty):
        self.cursor.execute("SELECT item FROM shopping")
        for (item_name,) in self.cursor.fetchall():
            clean_name = item_name
            if "×" in item_name or "x" in item_name:
                clean_name = re.sub(r"^\d+\s*[×x]\s*", "", item_name).strip()
            if base_item.strip() == clean_name:
                new_name = f"{qty} × {clean_name}" if qty > 1 else clean_name
                self.cursor.execute("UPDATE shopping SET item = ? WHERE item = ?", (new_name, item_name))
                self.conn.commit()
                return new_name
        return None

    # --- Users ---
    def add_user(self, chat_id):
        try:
            self.cursor.execute("INSERT OR IGNORE INTO users (chat_id) VALUES (?)", (chat_id,))
            self.conn.commit()
        except Exception as e:
            logging.error(f"❗ Error adding user: {e}")

    def get_all_users(self):
        self.cursor.execute("SELECT chat_id FROM users")
        return [row[0] for row in self.cursor.fetchall()]

    def set_reminder_days(self, chat_id, days):
        try:
            self.cursor.execute("UPDATE users SET reminder_days = ? WHERE chat_id = ?", (days, chat_id))
            self.conn.commit()
        except Exception as e:
            logging.error(f"❗ Error setting reminder_days: {e}")

    def get_reminder_days(self, chat_id):
        self.cursor.execute("SELECT reminder_days FROM users WHERE chat_id = ?", (chat_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 3  # Default 3 days
    

        
db = Database()  # Singleton
