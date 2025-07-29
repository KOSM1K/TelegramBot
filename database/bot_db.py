import sqlite3
import threading

# Default name for database used by bot
DB_NAME = "bot_data.db"


# Class responsible for working with database used in the bot
class BotDatabase:
    def __init__(self):
        self.connection = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.cursor = self.connection.cursor()

        self.lock = threading.Lock()

        print(f"Database with name {DB_NAME} created")

        self._init_members_table()

    def close(self):
        self.connection.close()

    def _init_members_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER,
            chat_id INTEGER,
            UNIQUE(tg_id, chat_id)
        )
        ''')

    def add_member(self, tg_id: int, chat_id: int):
        with self.lock:
            self.cursor.execute(
                'INSERT OR IGNORE INTO members (tg_id, chat_id) VALUES (?, ?)',
                (tg_id, chat_id)
            )

            self.connection.commit()

    def remove_member(self, tg_id: int, chat_id: int):
        with self.lock:
            self.cursor.execute(
                'DELETE FROM members WHERE tg_id = ? AND chat_id = ?',
                (tg_id, chat_id)
            )

            self.connection.commit()

    # Returns list of tg id's of all members from chat_id
    def all_members_of_chat(self, chat_id: int) -> [int]:
        with self.lock:
            self.cursor.execute(
                'SELECT tg_id FROM members WHERE chat_id = ?',
                (chat_id,)
            )

            rows = self.cursor.fetchall()

        return [row[0] for row in rows]
