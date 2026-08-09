from aiogram import Router

from app.handlers.admin import auth

router = Router()

router.include_router(auth.router)
