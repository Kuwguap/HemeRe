"""APScheduler for reminder cron jobs."""
import asyncio
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

import database as db

logger = logging.getLogger(__name__)

# Bot instance set by main - required to send reminder messages
_bot = None


def init_scheduler(bot) -> AsyncIOScheduler:
    """Initialize scheduler with reminder job. Needs bot instance to send messages."""
    global _bot
    _bot = bot

    scheduler = AsyncIOScheduler()
    # Check for due reminders every 60 seconds (cron-like)
    scheduler.add_job(
        send_pending_reminders,
        IntervalTrigger(minutes=1),
        id="reminders",
        replace_existing=True,
    )
    return scheduler


async def send_pending_reminders() -> None:
    """Send all due reminders and mark them as sent."""
    if _bot is None:
        return
    reminders = db.get_pending_reminders()
    for reminder_id, task_id, user_id, title in reminders:
        try:
            await _bot.send_message(
                chat_id=user_id,
                text=f"⏰ <b>Reminder!</b>\n\n{title}",
            )
            db.mark_reminder_sent(reminder_id)
        except Exception as e:
            logger.warning("Failed to send reminder %s: %s", reminder_id, e)
