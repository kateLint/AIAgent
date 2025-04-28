📋 Shopping List Bot - Shared Shopping List Telegram Bot
Welcome to Shopping List Bot!
This simple and friendly Telegram bot lets you manage a shared shopping list among multiple users.
Every change (adding, deleting, editing items) is immediately saved to the database, and users always see the latest list when they run /list.

🚀 Key Features
Add items to the shared shopping list (/add)

View the current shared list (/list)

Delete items from the list (/delete)

Clear the entire list (/clear)

Suggest missing basic items (/suggest)

Edit item quantities (/edit)

📦 Installation and Running
Install required libraries
Run:

bash
Copy
Edit
pip install python-telegram-bot apscheduler nest_asyncio
Set your Telegram bot token
In main.py, insert your bot token from BotFather:

python
Copy
Edit
TOKEN = "your-telegram-bot-token-here"
Run the bot

bash
Copy
Edit
python main.py
Database setup
The SQLite database (shopping_list.db) will be automatically created during the first run.

🛠️ Requirements
Python 3.8 or higher

sqlite3 module

Active internet connection (for Telegram communication)

🗂️ Project Structure
bash
Copy
Edit
main.py             # Main bot script
shopping_list.db    # SQLite database for items and users
README.md           # This project guide
🧠 Notes
The bot uses a passive update model:
Changes are instantly stored, and users manually retrieve the latest list using /list.

Multilingual support:
Messages are available in both Hebrew and English depending on user preference.

Automated reminders:
Shopping list reminders are sent twice a week (Sunday and Wednesday at 10:00 AM).

📧 Contact
Developer: ktlint@gmail.com

