"""Configuration for TaskMaster Bot."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Use persistent disk path on Render (env may not be set if Blueprint wasn't applied)
_raw_db = os.getenv("DATABASE_PATH")
if not _raw_db and os.getenv("RENDER"):
    _raw_db = "/opt/render/project/src/data/tasks.db"
if not _raw_db:
    _raw_db = "./data/tasks.db"
DATABASE_PATH = Path(_raw_db).resolve()

if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN is not set. "
        "Locally: add it to a .env file. "
        "On Render: set BOT_TOKEN in the service Environment (Dashboard → your service → Environment)."
    )


def ensure_data_dir() -> None:
    """Ensure data directory exists (for local dev and Render disk mount)."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
