import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import time

from app.database.engine import engine as db_engine
from app.database.engine import async_session_factory as db_session_factory
from app.database.engine import Base as db_base_model

class AppContext:
    def __init__(self):
        load_dotenv()
        token = os.getenv("BOT_TOKEN")
        if not token:
            raise ValueError("Error: BOT_TOKEN not found in .env!")

        self.bot = Bot(token=token)
        self.dp = Dispatcher()

        self.dp["context"] = self

        self.db_engine = db_engine
        self.db_session_factory = db_session_factory

        self.startup_timestamp = time.time()

    async def shutdown(self):
        """Cleanly close database connections when the bot stops."""
        await self.engine.dispose()
