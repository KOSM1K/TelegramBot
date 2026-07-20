import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import time

class AppContext:
    def __init__(self):
        load_dotenv()
        token = os.getenv("BOT_TOKEN")
        if not token:
            raise ValueError("Error: BOT_TOKEN not found in .env!")

        self.bot = Bot(token=token)
        self.dp = Dispatcher()

        self.dp["context"] = self

        self.startup_timestamp = time.time()
