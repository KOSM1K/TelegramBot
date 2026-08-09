from aiogram import Router, types
from aiogram.filters import Command

from app.appcontext import AppContext

router = Router()


@router.message(Command("whoami"))
async def cmd_whoami(message: types.Message, context: AppContext):
    user_id = message.from_user.id
    await message.answer(f"👤 Your Telegram ID is: `{user_id}`", parse_mode="Markdown")
