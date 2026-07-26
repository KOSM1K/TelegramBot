# app/handlers/balance.py
from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select

from app.appcontext import AppContext
from app.database.models.user import User

router = Router()


@router.message(Command("balance"))
async def cmd_balance(message: types.Message, context: AppContext):
    # Use the session factory directly from the context
    async with context.db_session_factory() as session:

        stmt = select(User).where(User.telegram_id == message.from_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                balance=1
            )
            session.add(user)
            await session.commit()
            await message.answer(f"🎉 Account created! Your starting balance is: {user.balance}")
        else:
            user.balance += 1
            await session.commit()
            await message.answer(f" Balance increased! Your new balance is: {user.balance}")