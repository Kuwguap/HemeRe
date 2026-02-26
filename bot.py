"""TaskMaster Telegram Bot - Main entry point."""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import BOT_TOKEN, ensure_data_dir
from database import init_db
from handlers import router
from scheduler import init_scheduler

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Start the bot."""
    ensure_data_dir()
    init_db()
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(router)

    # Register bot commands (show in Telegram menu)
    await bot.set_my_commands([
        BotCommand(command="start", description="Open bot & menu"),
        BotCommand(command="add", description="Add a new task"),
        BotCommand(command="list", description="View all tasks"),
        BotCommand(command="achievements", description="View badges & stats"),
        BotCommand(command="help", description="How to use"),
        BotCommand(command="cancel", description="Cancel current action"),
    ])

    # Start APScheduler for reminders
    scheduler = init_scheduler(bot)
    scheduler.start()
    logger.info("Scheduler started for reminders")

    try:
        logger.info("Starting polling...")
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
