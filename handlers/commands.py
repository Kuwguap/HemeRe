"""Command handlers for TaskMaster Bot."""
from html import escape as html_escape
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import html

import database as db
import achievements as ach
from keyboards import task_buttons, list_filter_buttons, main_menu_buttons
from .states import AddTaskStates

router = Router()

# In-memory state for list filter (persists per user in real session)
_show_done: dict[int, bool] = {}


def _get_show_done(user_id: int) -> bool:
    return _show_done.get(user_id, True)


def _set_show_done(user_id: int, value: bool) -> None:
    _show_done[user_id] = value


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Welcome message with quick-action inline buttons."""
    name = message.from_user.full_name or "there"
    await message.answer(
        f"👋 Hey {html.bold(name)}!\n\n"
        f"🎯 I'm <b>TaskMaster</b> — your personal task sidekick.\n\n"
        f"✨ Use the buttons below or type /add & /list — then smash those tasks! 💪",
        reply_markup=main_menu_buttons(),
    )


@router.message(Command("achievements"))
async def cmd_achievements(message: Message) -> None:
    """Show achievements list."""
    text = ach.format_achievements_list(message.from_user.id)
    await message.answer(text, reply_markup=main_menu_buttons())


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    """Cancel any active flow (e.g. add task)."""
    await state.clear()
    await message.answer("❌ Cancelled.", reply_markup=main_menu_buttons())


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Help message with main menu."""
    await message.answer(
        "📚 <b>TaskMaster Help</b>\n\n"
        "➕ <b>Add:</b> Use the button below or /add <i>title</i>\n"
        "📋 <b>List:</b> View & manage tasks with inline buttons\n"
        "✅ Mark Done · 🗑 Delete · ⏰ Add Reminder (15m, 1h, 3h, 1d)\n\n"
        "🏆 <b>Achievements:</b> Unlock badges by completing tasks & streaks!",
        reply_markup=main_menu_buttons(),
    )


@router.message(AddTaskStates.waiting_title, F.text)
async def add_task_via_state(message: Message, state: FSMContext) -> None:
    """Handle task title when user clicked 'Add Task' button."""
    user_id = message.from_user.id
    text = (message.text or "").strip()
    if not text:
        await message.answer("📝 Send me the task title (or /cancel to cancel).")
        return
    if text.lower() == "/cancel":
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=main_menu_buttons())
        return
    parts = text.split("|", 1)
    title = parts[0].strip()
    description = parts[1].strip() if len(parts) > 1 else ""
    task_id = db.add_task(user_id, title, description)
    task = db.get_task(task_id, user_id)
    await state.clear()
    if not task:
        await message.answer("😅 Failed to create task.")
        return
    status = "✨ Task added!"
    if description:
        status += f"\n\n📝 <i>{html_escape(description)}</i>"
    await message.answer(status, reply_markup=task_buttons(task_id, task.has_reminder))
    for u in ach.check_achievements(user_id, "task_created"):
        await message.answer(ach.format_achievement_notification(u))


@router.message(Command("add"), F.text)
async def cmd_add(message: Message) -> None:
    """Add a task. Format: /add Title | Optional description or reminder hint."""
    user_id = message.from_user.id
    text = message.text or ""
    args = text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "Usage: /add <i>task title</i>\nExample: /add Buy milk",
        )
        return

    rest = args[1].strip()
    # Support "Title | description" or "Title"
    parts = rest.split("|", 1)
    title = parts[0].strip()
    description = parts[1].strip() if len(parts) > 1 else ""

    if not title:
        await message.answer("Task title cannot be empty.")
        return

    task_id = db.add_task(user_id, title, description)
    task = db.get_task(task_id, user_id)
    if not task:
        await message.answer("Failed to create task.")
        return

    status = "✨ Task added!"
    if description:
        status += f"\n\n📝 <i>{html_escape(description)}</i>"

    await message.answer(
        status,
        reply_markup=task_buttons(task_id, task.has_reminder),
    )
    for u in ach.check_achievements(user_id, "task_created"):
        await message.answer(ach.format_achievement_notification(u))


@router.message(Command("add"))
async def cmd_add_empty(message: Message) -> None:
    """Add command without text."""
    await message.answer("Usage: /add <i>task title</i>\nExample: /add Buy milk")


async def send_list(user_id: int, message: Message) -> None:
    """Send task list (used by /list and by My List callback)."""
    show_done = _get_show_done(user_id)
    tasks = db.get_user_tasks(user_id, include_done=show_done)

    if not tasks:
        await message.answer(
            "📭 No tasks yet!\n\n👇 Add one with the button or /add <i>task title</i>",
            reply_markup=main_menu_buttons(),
        )
        return

    lines = []
    for t in tasks:
        prefix = "✅" if t.done else "⬜"
        title_esc = html_escape(t.title)
        if t.done:
            lines.append(f"{prefix} <s>{title_esc}</s>")
        else:
            lines.append(f"{prefix} {title_esc}")
        if t.description:
            desc_esc = html_escape(t.description)
            lines.append(f"   <i>{desc_esc}</i>")
        lines.append("")
    header = "📋 Your tasks:" if show_done else "🔥 Active tasks:"
    body = "\n".join(lines[:-1])
    await message.answer(
        f"{header}\n\n{body}",
        reply_markup=list_filter_buttons(show_done),
    )
    for t in tasks:
        prefix = "✅" if t.done else "⬜"
        text = f"{prefix} {html_escape(t.title)}"
        if t.description:
            text += f"\n<i>{html_escape(t.description)}</i>"
        if t.reminder_at:
            text += "\n⏰ Reminder set"
        await message.answer(text, reply_markup=task_buttons(t.id, t.has_reminder))


@router.message(Command("list"))
async def cmd_list(message: Message) -> None:
    """List all tasks with inline buttons."""
    await send_list(message.from_user.id, message)
