from aiogram import Router

from app.handlers import ping
from app.handlers import balance


router = Router()

router.include_router(ping.router)
router.include_router(balance.router)
