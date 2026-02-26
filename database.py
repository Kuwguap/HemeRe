"""SQLite database and task models."""
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator

from config import DATABASE_PATH


@dataclass
class Task:
    """Represents a user task."""
    id: int
    user_id: int
    title: str
    description: str
    done: bool
    reminder_at: datetime | None
    created_at: datetime
    completed_at: datetime | None = None

    @property
    def has_reminder(self) -> bool:
        return self.reminder_at is not None


def get_connection() -> sqlite3.Connection:
    """Create database connection and ensure directory exists."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_session() -> Iterator[sqlite3.Connection]:
    """Context manager for database sessions."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Initialize database schema."""
    with db_session() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                done INTEGER DEFAULT 0,
                reminder_at TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
        """)
        # Migration: add completed_at if missing
        try:
            conn.execute("ALTER TABLE tasks ADD COLUMN completed_at TEXT")
        except sqlite3.OperationalError:
            pass
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                reminder_at TEXT NOT NULL,
                sent INTEGER DEFAULT 0,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_user ON tasks(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_done ON tasks(done)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_reminders_pending ON reminders(sent, reminder_at)")
        # Achievements
        conn.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id TEXT PRIMARY KEY,
                emoji TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                sort_order INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                user_id INTEGER NOT NULL,
                achievement_id TEXT NOT NULL,
                unlocked_at TEXT NOT NULL,
                PRIMARY KEY (user_id, achievement_id),
                FOREIGN KEY (achievement_id) REFERENCES achievements(id)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_user_achievements_user ON user_achievements(user_id)")
        # Seed default achievements
        _seed_achievements(conn)


def add_task(user_id: int, title: str, description: str = "", reminder_at: datetime | None = None) -> int:
    """Add a new task. Returns task ID."""
    created_at = datetime.utcnow().isoformat()
    reminder_str = reminder_at.isoformat() if reminder_at else None
    with db_session() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (user_id, title, description, done, reminder_at, created_at) VALUES (?, ?, ?, 0, ?, ?)",
            (user_id, title, description, reminder_str, created_at)
        )
        task_id = cur.lastrowid
        if reminder_at:
            conn.execute(
                "INSERT INTO reminders (task_id, user_id, reminder_at) VALUES (?, ?, ?)",
                (task_id, user_id, reminder_str)
            )
        return task_id or 0


def get_task(task_id: int, user_id: int) -> Task | None:
    """Get a task by ID for a specific user."""
    with db_session() as conn:
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id)
        ).fetchone()
        return _row_to_task(row) if row else None


def get_user_tasks(user_id: int, include_done: bool = True) -> list[Task]:
    """Get all tasks for a user."""
    with db_session() as conn:
        if include_done:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE user_id = ? ORDER BY done ASC, created_at DESC",
                (user_id,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE user_id = ? AND done = 0 ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()
        return [_row_to_task(r) for r in rows]


def mark_task_done(task_id: int, user_id: int) -> bool:
    """Mark a task as done. Returns True if updated."""
    completed_at = datetime.utcnow().isoformat()
    with db_session() as conn:
        cur = conn.execute(
            "UPDATE tasks SET done = 1, completed_at = ? WHERE id = ? AND user_id = ?",
            (completed_at, task_id, user_id)
        )
        if cur.rowcount:
            conn.execute("UPDATE reminders SET sent = 1 WHERE task_id = ?", (task_id,))
        return cur.rowcount > 0


def delete_task(task_id: int, user_id: int) -> bool:
    """Delete a task. Returns True if deleted."""
    with db_session() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
        if cur.rowcount:
            conn.execute("DELETE FROM reminders WHERE task_id = ?", (task_id,))
        return cur.rowcount > 0


def get_pending_reminders() -> list[tuple[int, int, int, str]]:
    """Get reminders that are due. Returns (reminder_id, task_id, user_id, title)."""
    now = datetime.utcnow().isoformat()
    with db_session() as conn:
        rows = conn.execute("""
            SELECT r.id, r.task_id, r.user_id, t.title
            FROM reminders r
            JOIN tasks t ON r.task_id = t.id
            WHERE r.sent = 0 AND r.reminder_at <= ?
        """, (now,)).fetchall()
        return [(r["id"], r["task_id"], r["user_id"], r["title"]) for r in rows]


def mark_reminder_sent(reminder_id: int) -> None:
    """Mark a reminder as sent."""
    with db_session() as conn:
        conn.execute("UPDATE reminders SET sent = 1 WHERE id = ?", (reminder_id,))


def add_reminder(task_id: int, user_id: int, reminder_at: datetime) -> bool:
    """Add a reminder for an existing task. Replaces any existing reminder. Returns True if successful."""
    reminder_str = reminder_at.isoformat()
    with db_session() as conn:
        conn.execute(
            "UPDATE tasks SET reminder_at = ? WHERE id = ? AND user_id = ?",
            (reminder_str, task_id, user_id)
        )
        # Mark old reminders as sent (avoid duplicates), then add new one
        conn.execute("UPDATE reminders SET sent = 1 WHERE task_id = ?", (task_id,))
        conn.execute(
            "INSERT INTO reminders (task_id, user_id, reminder_at) VALUES (?, ?, ?)",
            (task_id, user_id, reminder_str)
        )
        return True


def _seed_achievements(conn: sqlite3.Connection) -> None:
    """Insert default achievement definitions if not present."""
    defaults = [
        ("first_task", "🌱", "First Step", "Create your first task", 1),
        ("tasks_5", "⭐", "Getting Started", "Complete 5 tasks", 2),
        ("tasks_10", "🌟", "On a Roll", "Complete 10 tasks", 3),
        ("tasks_25", "🔥", "Productivity Beast", "Complete 25 tasks", 4),
        ("tasks_50", "💎", "Half Century", "Complete 50 tasks", 5),
        ("tasks_100", "👑", "Century Legend", "Complete 100 tasks", 6),
        ("first_reminder", "⏰", "Time Keeper", "Set your first reminder", 7),
        ("reminders_5", "🔔", "Reminder Pro", "Set 5 reminders", 8),
        ("streak_3", "📅", "Three Day Streak", "Complete a task 3 days in a row", 9),
        ("streak_7", "🎯", "Week Warrior", "Complete a task 7 days in a row", 10),
        ("streak_30", "🏆", "Monthly Master", "30-day completion streak", 11),
        ("early_bird", "🌅", "Early Bird", "Complete a task before 9 AM", 12),
        ("night_owl", "🦉", "Night Owl", "Complete a task after 10 PM", 13),
        ("speed_demon", "⚡", "Speed Demon", "Complete a task within 5 min of creating", 14),
        ("list_master", "📋", "List Master", "Have 10+ tasks in your list at once", 15),
        ("clean_slate", "🧹", "Clean Slate", "Complete all active tasks", 16),
        ("no_reminder_left_behind", "✅", "No Reminder Left Behind", "Complete 10 tasks that had reminders", 17),
    ]
    for aid, emoji, name, desc, order in defaults:
        conn.execute(
            "INSERT OR IGNORE INTO achievements (id, emoji, name, description, sort_order) VALUES (?, ?, ?, ?, ?)",
            (aid, emoji, name, desc, order)
        )


def get_user_stats(user_id: int) -> dict:
    """Return total_created, total_done, total_reminders, last_done_date, streak, tasks_with_reminder_done."""
    with db_session() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as total, SUM(done) as done FROM tasks WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        total = row["total"] or 0
        done = row["done"] or 0
        rem = conn.execute(
            "SELECT COUNT(*) as c FROM reminders WHERE user_id = ?",
            (user_id,)
        ).fetchone()["c"] or 0
        last_done = conn.execute(
            "SELECT completed_at FROM tasks WHERE user_id = ? AND done = 1 AND completed_at IS NOT NULL ORDER BY completed_at DESC LIMIT 1",
            (user_id,)
        ).fetchone()
        last_done_date = last_done["completed_at"][:10] if last_done and last_done["completed_at"] else None
        # Tasks that had a reminder and were completed
        reminder_done = conn.execute(
            "SELECT COUNT(*) as c FROM tasks WHERE user_id = ? AND done = 1 AND reminder_at IS NOT NULL",
            (user_id,)
        ).fetchone()["c"] or 0
        streak = _compute_streak(conn, user_id)
        return {
            "total_created": total,
            "total_done": done,
            "total_reminders": rem,
            "last_done_date": last_done_date,
            "streak": streak,
            "tasks_with_reminder_done": reminder_done,
        }


def _compute_streak(conn: sqlite3.Connection, user_id: int) -> int:
    """Consecutive days (including today) with at least one completed task."""
    from datetime import timedelta
    rows = conn.execute(
        "SELECT DISTINCT date(completed_at) as d FROM tasks WHERE user_id = ? AND done = 1 AND completed_at IS NOT NULL ORDER BY d DESC LIMIT 100",
        (user_id,)
    ).fetchall()
    if not rows:
        return 0
    dates = [r["d"] for r in rows]
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if today not in dates:
        # Streak broken (no completion today yet)
        return 0
    streak = 0
    d = datetime.utcnow().date()
    for _ in range(400):
        day_str = d.strftime("%Y-%m-%d")
        if day_str in dates:
            streak += 1
            d -= timedelta(days=1)
        else:
            break
    return streak


def get_all_achievements() -> list[dict]:
    """List all achievement definitions ordered by sort_order."""
    with db_session() as conn:
        rows = conn.execute(
            "SELECT id, emoji, name, description, sort_order FROM achievements ORDER BY sort_order"
        ).fetchall()
        return [dict(r) for r in rows]


def get_user_achievement_ids(user_id: int) -> set[str]:
    """Set of achievement IDs unlocked by user."""
    with db_session() as conn:
        rows = conn.execute(
            "SELECT achievement_id FROM user_achievements WHERE user_id = ?",
            (user_id,)
        ).fetchall()
        return {r["achievement_id"] for r in rows}


def unlock_achievement(user_id: int, achievement_id: str) -> bool:
    """Unlock achievement for user. Returns True if newly unlocked."""
    now = datetime.utcnow().isoformat()
    with db_session() as conn:
        try:
            conn.execute(
                "INSERT INTO user_achievements (user_id, achievement_id, unlocked_at) VALUES (?, ?, ?)",
                (user_id, achievement_id, now)
            )
            return True
        except sqlite3.IntegrityError:
            return False  # already unlocked


def _row_to_task(row: sqlite3.Row) -> Task:
    """Convert a DB row to Task."""
    reminder_at = row["reminder_at"]
    if reminder_at:
        try:
            reminder_at = datetime.fromisoformat(reminder_at)
        except ValueError:
            reminder_at = None
    try:
        completed_at = row["completed_at"]
    except (IndexError, KeyError):
        completed_at = None
    if completed_at:
        try:
            completed_at = datetime.fromisoformat(completed_at)
        except (ValueError, TypeError):
            completed_at = None
    return Task(
        id=row["id"],
        user_id=row["user_id"],
        title=row["title"],
        description=row["description"] or "",
        done=bool(row["done"]),
        reminder_at=reminder_at,
        created_at=datetime.fromisoformat(row["created_at"]),
        completed_at=completed_at,
    )
