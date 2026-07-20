import asyncio
import logging
from appcontext import AppContext

# Import your top-level routers
from handlers import router as handlers_router

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    # 1. Create the context (this automatically creates bot, dp, and db)
    context = AppContext()

    # 2. Wire up the routers to the dispatcher
    context.dp.include_router(handlers_router)

    # 3. Start the bot
    logging.info("Starting bot...")
    await context.bot.delete_webhook(drop_pending_updates=True)
    await context.dp.start_polling(context.bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
