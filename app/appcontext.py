import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import time

from app.database.engine import engine
from app.database.engine import async_session_factory
from app.database.engine import Base


class AppContext:
    def __init__(self):
        load_dotenv()
        token = os.getenv("BOT_TOKEN")
        if not token:
            raise ValueError("Error: BOT_TOKEN not found in .env!")

        self.bot = Bot(token=token)
        self.dp = Dispatcher()

        self.dp["context"] = self

        self.engine = engine
        self.db_session_factory = async_session_factory

        self.startup_timestamp = time.time()

    async def shutdown(self):
        """Cleanly close database connections when the bot stops."""
        await self.engine.dispose()
