from aiogram import Router, types
from aiogram.filters import Command

from appcontext import AppContext

router = Router()

@router.message(Command("ping"))
async def ping(message: types.Message, context: AppContext):
    await message.answer(text='pong')
