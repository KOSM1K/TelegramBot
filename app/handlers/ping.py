from aiogram import Router, types
from aiogram.filters import Command

import logging

from app.appcontext import AppContext

router = Router()

@router.message(Command("ping"))
async def ping(message: types.Message, context: AppContext):
    await message.answer(text='pong')
