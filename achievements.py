"""Achievement unlock logic and notifications."""
from datetime import datetime

import database as db


def check_achievements(user_id: int, event: str, **kwargs) -> list[dict]:
    """
    Check and unlock achievements. event: 'task_created' | 'task_done' | 'reminder_set'.
    Returns list of newly unlocked {id, emoji, name, description}.
    """
    unlocked = []
    stats = db.get_user_stats(user_id)
    have = db.get_user_achievement_ids(user_id)

    # First task created
    if stats["total_created"] >= 1 and "first_task" not in have:
        if db.unlock_achievement(user_id, "first_task"):
            a = _get_ach("first_task")
            if a:
                unlocked.append(a)

    # Completed counts
    done = stats["total_done"]
    for aid, threshold in [("tasks_5", 5), ("tasks_10", 10), ("tasks_25", 25), ("tasks_50", 50), ("tasks_100", 100)]:
        if done >= threshold and aid not in have:
            if db.unlock_achievement(user_id, aid):
                a = _get_ach(aid)
                if a:
                    unlocked.append(a)

    # Reminders
    rem = stats["total_reminders"]
    if rem >= 1 and "first_reminder" not in have:
        if db.unlock_achievement(user_id, "first_reminder"):
            a = _get_ach("first_reminder")
            if a:
                unlocked.append(a)
    if rem >= 5 and "reminders_5" not in have:
        if db.unlock_achievement(user_id, "reminders_5"):
            a = _get_ach("reminders_5")
            if a:
                unlocked.append(a)

    # Streaks
    streak = stats["streak"]
    if streak >= 3 and "streak_3" not in have:
        if db.unlock_achievement(user_id, "streak_3"):
            a = _get_ach("streak_3")
            if a:
                unlocked.append(a)
    if streak >= 7 and "streak_7" not in have:
        if db.unlock_achievement(user_id, "streak_7"):
            a = _get_ach("streak_7")
            if a:
                unlocked.append(a)
    if streak >= 30 and "streak_30" not in have:
        if db.unlock_achievement(user_id, "streak_30"):
            a = _get_ach("streak_30")
            if a:
                unlocked.append(a)

    # List master: 10+ tasks (created, any state)
    if stats["total_created"] >= 10 and "list_master" not in have:
        if db.unlock_achievement(user_id, "list_master"):
            a = _get_ach("list_master")
            if a:
                unlocked.append(a)

    # No reminder left behind
    if stats["tasks_with_reminder_done"] >= 10 and "no_reminder_left_behind" not in have:
        if db.unlock_achievement(user_id, "no_reminder_left_behind"):
            a = _get_ach("no_reminder_left_behind")
            if a:
                unlocked.append(a)

    # Event-specific: early_bird, night_owl (on task_done), speed_demon (on task_done)
    if event == "task_done" and kwargs.get("completed_at"):
        try:
            dt = datetime.fromisoformat(kwargs["completed_at"].replace("Z", "+00:00"))
            hour = dt.hour
            if hour < 9 and "early_bird" not in have:
                if db.unlock_achievement(user_id, "early_bird"):
                    a = _get_ach("early_bird")
                    if a:
                        unlocked.append(a)
            if hour >= 22 and "night_owl" not in have:
                if db.unlock_achievement(user_id, "night_owl"):
                    a = _get_ach("night_owl")
                    if a:
                        unlocked.append(a)
        except Exception:
            pass

    if event == "task_done" and kwargs.get("created_at") and kwargs.get("completed_at"):
        try:
            created = datetime.fromisoformat(kwargs["created_at"].replace("Z", "+00:00"))
            completed = datetime.fromisoformat(kwargs["completed_at"].replace("Z", "+00:00"))
            if (completed - created).total_seconds() <= 300 and "speed_demon" not in have:  # 5 min
                if db.unlock_achievement(user_id, "speed_demon"):
                    a = _get_ach("speed_demon")
                    if a:
                        unlocked.append(a)
        except Exception:
            pass

    # Clean slate: all active tasks done (on task_done we could check if remaining active == 0)
    if event == "task_done":
        stats2 = db.get_user_stats(user_id)
        # Active = total_created - total_done; if we just completed one and active is 0
        active = stats2["total_created"] - stats2["total_done"]
        if active == 0 and stats2["total_done"] >= 1 and "clean_slate" not in have:
            if db.unlock_achievement(user_id, "clean_slate"):
                a = _get_ach("clean_slate")
                if a:
                    unlocked.append(a)

    return unlocked


def _get_ach(aid: str) -> dict | None:
    all_a = db.get_all_achievements()
    for a in all_a:
        if a["id"] == aid:
            return a
    return None


def format_achievement_notification(ach: dict) -> str:
    """Single achievement unlock message."""
    return f"🏆 <b>Achievement Unlocked!</b>\n\n{ach['emoji']} <b>{ach['name']}</b>\n<i>{ach['description']}</i>"


def format_achievements_list(user_id: int) -> str:
    """Full achievements list with locked/unlocked."""
    all_a = db.get_all_achievements()
    unlocked_ids = db.get_user_achievement_ids(user_id)
    stats = db.get_user_stats(user_id)
    lines = [
        "🏆 <b>Achievements</b>\n",
        f"📊 <b>Your stats:</b> {stats['total_done']} completed · {stats['streak']} day streak · {stats['total_reminders']} reminders\n",
    ]
    for a in all_a:
        uid = a["id"]
        if uid in unlocked_ids:
            lines.append(f"{a['emoji']} <b>{a['name']}</b> — {a['description']}")
        else:
            lines.append(f"🔒 <i>{a['name']}</i> — {a['description']}")
    return "\n".join(lines)
