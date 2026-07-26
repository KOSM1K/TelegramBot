import asyncio
import logging
from app.appcontext import AppContext

# Import your top-level routers
from app.handlers import router as handlers_router

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    # 1. Create the context
    context = AppContext()

    try:
        # 2. Wire up routers to the dispatcher
        context.dp.include_router(handlers_router)

        # 3. Start the bot
        logging.info("Starting bot...")
        await context.bot.delete_webhook(drop_pending_updates=True)
        await context.dp.start_polling(context.bot)

    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped by user.")
    except Exception as e:
        logging.error(f"Bot crashed with error: {e}")
    finally:
        # 4. ALWAYS clean up database connections, no matter how it exits
        logging.info("Cleaning up database connections...")
        await context.shutdown()
        logging.info("Shutdown complete.")

if __name__ == "__main__":
    asyncio.run(main())
