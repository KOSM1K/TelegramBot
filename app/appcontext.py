import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import time

class AppContext:
    def __init__(self):
        # 1. Load config/token
        load_dotenv()
        token = os.getenv("BOT_TOKEN")
        if not token:
            raise ValueError("Error: BOT_TOKEN not found in .env!")

        # 2. Create Bot and Dispatcher
        self.bot = Bot(token=token)
        self.dp = Dispatcher()

        # 3. THE MAGIC TRICK: Inject the context into the dispatcher
        # This allows handlers to ask for "context" and get this exact instance
        self.dp["context"] = self

        # 4. Initialize other services (like your DB adapter)
        # self.db = MyDatabaseAdapter()

        self.startup_timestamp = time.time()
