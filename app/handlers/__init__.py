from aiogram import Router

from . import ping

router = Router()

router.include_router(ping.router)
