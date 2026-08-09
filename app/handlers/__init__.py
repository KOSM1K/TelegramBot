from aiogram import Router

from app.handlers import ping
from app.handlers import server_stats
from app.handlers import balance
from app.handlers import admin
from app.handlers import user_info

router = Router()

router.include_router(ping.router)
router.include_router(server_stats.router)
router.include_router(balance.router)
router.include_router(admin.router)
router.include_router(user_info.router)
