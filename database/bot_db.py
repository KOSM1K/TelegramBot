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
        self._init_money_table()
        self._init_daily_table()

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

    def _init_money_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS money (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER,
            chat_id INTEGER,
            money INTEGER DEFAULT 1000,
            UNIQUE(tg_id, chat_id)
        )
        ''')

    def _init_daily_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily (
            chat_id INTEGER PRIMARY KEY,
            last_call INTEGER
        )
        ''')
        self.connection.commit()

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

    def add_money(self, tg_id: int, chat_id: int, amount: int):
        with self.lock:
            self.cursor.execute('''
                INSERT INTO money (tg_id, chat_id, money)
                VALUES (?, ?, ?)
                ON CONFLICT(tg_id, chat_id)
                DO UPDATE SET money = money + excluded.money
            ''', (tg_id, chat_id, amount))
            self.connection.commit()

    def get_money(self, tg_id: int, chat_id: int) -> int:
        with self.lock:
            self.cursor.execute('''
                SELECT money FROM money
                WHERE tg_id = ? AND chat_id = ?
            ''', (tg_id, chat_id))
            row = self.cursor.fetchone()
        return row[0] if row else 0

    def take_money(self, tg_id: int, chat_id: int, amount: int) -> bool:
        with self.lock:
            # Atomic deduction: only subtract if there’s enough
            self.cursor.execute('''
                UPDATE money
                SET money = money - ?
                WHERE tg_id = ? AND chat_id = ? AND money >= ?
            ''', (amount, tg_id, chat_id, amount))

            if self.cursor.rowcount == 0:
                return False  # Not enough funds

            self.connection.commit()
            return True

    def get_last_daily(self, chat_id):
        with self.lock:
            self.cursor.execute('SELECT last_call FROM daily WHERE chat_id = ?', (chat_id,))
            row = self.cursor.fetchone()
            return int(row[0]) if row else None

    def update_daily(self, chat_id):
        from datetime import datetime
        now = int(datetime.now().timestamp())
        with self.lock:
            self.cursor.execute('''
                INSERT INTO daily (chat_id, last_call)
                VALUES (?, ?)
                ON CONFLICT(chat_id)
                DO UPDATE SET last_call = excluded.last_call
            ''', (chat_id, now))
            self.connection.commit()
