"""Inline keyboard builders for TaskMaster Bot."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class MainMenu(CallbackData, prefix="menu"):
    """Callback data for main menu."""
    action: str  # add_task, my_list, achievements, help


class TaskAction(CallbackData, prefix="task"):
    """Callback data for task actions."""
    action: str  # done, delete, remind
    task_id: int


class ReminderTime(CallbackData, prefix="remind"):
    """Callback data for reminder time selection."""
    task_id: int
    minutes: int


class ListNav(CallbackData, prefix="list"):
    """Callback data for list navigation."""
    action: str  # show_done, hide_done, page
    page: int = 0


def task_buttons(task_id: int, has_reminder: bool = False) -> InlineKeyboardMarkup:
    """Inline buttons for a single task: Mark Done, Delete, Add Reminder."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Done",
            callback_data=TaskAction(action="done", task_id=task_id).pack()
        ),
        InlineKeyboardButton(
            text="🗑️ Delete",
            callback_data=TaskAction(action="delete", task_id=task_id).pack()
        ),
    )
    if not has_reminder:
        builder.row(
            InlineKeyboardButton(
                text="⏰ Remind",
                callback_data=TaskAction(action="remind", task_id=task_id).pack()
            ),
        )
    return builder.as_markup()


def reminder_time_buttons(task_id: int) -> InlineKeyboardMarkup:
    """Quick reminder time options: 15m, 1h, 3h, 1d."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="⏱️ 15m",
            callback_data=ReminderTime(task_id=task_id, minutes=15).pack()
        ),
        InlineKeyboardButton(
            text="🕐 1h",
            callback_data=ReminderTime(task_id=task_id, minutes=60).pack()
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🕒 3h",
            callback_data=ReminderTime(task_id=task_id, minutes=180).pack()
        ),
        InlineKeyboardButton(
            text="📅 1d",
            callback_data=ReminderTime(task_id=task_id, minutes=1440).pack()
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="❌ Cancel",
            callback_data=TaskAction(action="cancel_remind", task_id=task_id).pack()
        ),
    )
    return builder.as_markup()


def main_menu_buttons() -> InlineKeyboardMarkup:
    """Main menu: Add Task, My List, Achievements, Help."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="➕ Add Task",
            callback_data=MainMenu(action="add_task").pack()
        ),
        InlineKeyboardButton(
            text="📋 My List",
            callback_data=MainMenu(action="my_list").pack()
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🏆 Achievements",
            callback_data=MainMenu(action="achievements").pack()
        ),
        InlineKeyboardButton(
            text="❓ Help",
            callback_data=MainMenu(action="help").pack()
        ),
    )
    return builder.as_markup()


def list_filter_buttons(show_done: bool) -> InlineKeyboardMarkup:
    """Toggle showing/hiding completed tasks."""
    builder = InlineKeyboardBuilder()
    text = "🙈 Hide Completed" if show_done else "👁️ Show All"
    builder.row(
        InlineKeyboardButton(
            text=text,
            callback_data=ListNav(action="toggle_done", page=0).pack()
        ),
    )
    return builder.as_markup()
