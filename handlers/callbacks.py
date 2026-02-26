"""Callback handlers for inline buttons."""
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
import achievements as ach
from keyboards import (
    MainMenu,
    TaskAction,
    ReminderTime,
    ListNav,
    task_buttons,
    reminder_time_buttons,
    main_menu_buttons,
)
from .commands import _get_show_done, _set_show_done, send_list
from .states import AddTaskStates

router = Router()


@router.callback_query(MainMenu.filter(F.action == "add_task"))
async def cb_menu_add_task(callback: CallbackQuery, callback_data: MainMenu, state: FSMContext) -> None:
    """Start add-task flow via inline button."""
    await callback.answer()
    await state.set_state(AddTaskStates.waiting_title)
    await callback.message.answer(
        "📝 <b>New task</b>\n\nSend me the task title (e.g. <i>Buy milk</i>).\n"
        "You can add a description with <code>|</code> e.g. <i>Call Mom | Tomorrow 5pm</i>.\n\n"
        "Type /cancel to cancel.",
    )


@router.callback_query(MainMenu.filter(F.action == "my_list"))
async def cb_menu_my_list(callback: CallbackQuery, callback_data: MainMenu) -> None:
    """Show task list via inline button."""
    await callback.answer()
    await send_list(callback.from_user.id, callback.message)


@router.callback_query(MainMenu.filter(F.action == "achievements"))
async def cb_menu_achievements(callback: CallbackQuery, callback_data: MainMenu) -> None:
    """Show achievements via inline button."""
    await callback.answer()
    text = ach.format_achievements_list(callback.from_user.id)
    await callback.message.answer(text, reply_markup=main_menu_buttons())


@router.callback_query(MainMenu.filter(F.action == "help"))
async def cb_menu_help(callback: CallbackQuery, callback_data: MainMenu) -> None:
    """Show help via inline button."""
    await callback.answer()
    await callback.message.answer(
        "📚 <b>TaskMaster Help</b>\n\n"
        "➕ <b>Add:</b> Use the button or /add <i>title</i>\n"
        "📋 <b>List:</b> View & manage with inline buttons\n"
        "✅ Done · 🗑️ Delete · ⏰ Remind (15m, 1h, 3h, 1d)\n\n"
        "🏆 Unlock achievements by completing tasks & streaks!",
        reply_markup=main_menu_buttons(),
    )


@router.callback_query(TaskAction.filter(F.action == "done"))
async def cb_task_done(callback: CallbackQuery, callback_data: TaskAction) -> None:
    """Mark task as done and check achievements."""
    await callback.answer()
    user_id = callback.from_user.id
    task_id = callback_data.task_id

    task_before = db.get_task(task_id, user_id)
    if not task_before:
        await callback.answer("Task not found.", show_alert=True)
        return

    if db.mark_task_done(task_id, user_id):
        task = db.get_task(task_id, user_id)
        from html import escape as html_escape
        await callback.message.edit_text(
            f"✅ <s>{html_escape(task.title)}</s>\n<i>Completed! 🎉</i>",
            reply_markup=None,
        )
        created_at = task_before.created_at
        completed_at = task.completed_at if task else None
        for u in ach.check_achievements(
            user_id, "task_done", completed_at=completed_at, created_at=created_at
        ):
            await callback.message.answer(ach.format_achievement_notification(u))
    else:
        await callback.answer("Task not found or already done.", show_alert=True)


@router.callback_query(TaskAction.filter(F.action == "delete"))
async def cb_task_delete(callback: CallbackQuery, callback_data: TaskAction) -> None:
    """Delete a task."""
    await callback.answer()
    user_id = callback.from_user.id
    task_id = callback_data.task_id

    if db.delete_task(task_id, user_id):
        await callback.message.edit_text("🗑 Task deleted.")
    else:
        await callback.answer("Task not found.", show_alert=True)


@router.callback_query(TaskAction.filter(F.action == "remind"))
async def cb_task_remind(callback: CallbackQuery, callback_data: TaskAction) -> None:
    """Show reminder time options."""
    await callback.answer()
    task_id = callback_data.task_id
    user_id = callback.from_user.id

    task = db.get_task(task_id, user_id)
    if not task:
        await callback.answer("Task not found.", show_alert=True)
        return
    if task.has_reminder:
        await callback.answer("This task already has a reminder.", show_alert=True)
        return

    await callback.message.edit_reply_markup(reply_markup=reminder_time_buttons(task_id))


@router.callback_query(TaskAction.filter(F.action == "cancel_remind"))
async def cb_cancel_remind(callback: CallbackQuery, callback_data: TaskAction) -> None:
    """Cancel reminder selection, restore task buttons."""
    from html import escape as html_escape
    await callback.answer()
    task_id = callback_data.task_id
    user_id = callback.from_user.id

    task = db.get_task(task_id, user_id)
    if not task:
        return

    prefix = "✅" if task.done else "⬜"
    text = f"{prefix} {html_escape(task.title)}"
    if task.description:
        text += f"\n<i>{html_escape(task.description)}</i>"
    await callback.message.edit_reply_markup(reply_markup=task_buttons(task_id, task.has_reminder))


@router.callback_query(ReminderTime.filter())
async def cb_reminder_time(callback: CallbackQuery, callback_data: ReminderTime) -> None:
    """Set reminder for task."""
    await callback.answer()
    task_id = callback_data.task_id
    user_id = callback.from_user.id
    minutes = callback_data.minutes

    task = db.get_task(task_id, user_id)
    if not task:
        await callback.answer("Task not found.", show_alert=True)
        return

    reminder_at = datetime.utcnow() + timedelta(minutes=minutes)
    db.add_reminder(task_id, user_id, reminder_at)

    from html import escape as html_escape
    label = {15: "15 min", 60: "1 hour", 180: "3 hours", 1440: "1 day"}.get(minutes, f"{minutes} min")
    await callback.message.edit_text(
        f"⬜ {html_escape(task.title)}\n⏰ Reminder in {label}",
        reply_markup=task_buttons(task_id, has_reminder=True),
    )
    for u in ach.check_achievements(callback.from_user.id, "reminder_set"):
        await callback.message.answer(ach.format_achievement_notification(u))


@router.callback_query(ListNav.filter(F.action == "toggle_done"))
async def cb_toggle_done(callback: CallbackQuery, callback_data: ListNav) -> None:
    """Toggle show/hide completed tasks and refresh list."""
    user_id = callback.from_user.id
    current = _get_show_done(user_id)
    _set_show_done(user_id, not current)
    await callback.answer("🔄 List updated!")
    await send_list(user_id, callback.message)
