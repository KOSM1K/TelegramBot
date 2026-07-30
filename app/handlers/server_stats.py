from aiogram import Router, types
from aiogram.filters import Command

import logging
import psutil

from app.appcontext import AppContext

router = Router()

@router.message(Command("stats"))
async def stats(message: types.Message, context: AppContext):
    cpu_usage = psutil.cpu_percent(interval=1)

    mem = psutil.virtual_memory()

    mem_total = mem.total / (1024 ** 3)
    mem_used = mem.used / (1024 ** 3)

    stats_string = f"CPU: {cpu_usage}%\n" \
    f"RAM: {mem_used:.2f} / {mem_total:.2f} GB"


    await message.answer(text=stats_string)
