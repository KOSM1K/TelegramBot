from aiogram import Router

from app.handlers import ping

router = Router()

router.include_router(ping.router)
