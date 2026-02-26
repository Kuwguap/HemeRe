"""Configuration for TaskMaster Bot."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "./data/tasks.db"))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN must be set in environment or .env file")


def ensure_data_dir() -> None:
    """Ensure data directory exists (for local dev and Render disk mount)."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
