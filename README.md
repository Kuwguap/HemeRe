# 📝 TaskMaster Telegram Bot

A streamlined, cross-platform task manager built for Telegram. Manage your to-do list with descriptions, reminders, and quick-action **inline buttons**.

**Before you push or deploy:** see [TELEGRAM.md](TELEGRAM.md) for BotFather description & commands, and [DEPLOY.md](DEPLOY.md) for the Git + Render checklist.

## ✨ Features

* **Cross-Device Sync:** Access your tasks anywhere you have Telegram.
* **Task Management:** Add tasks with detailed descriptions.
* **Interactive UI:** Use inline buttons to manage tasks without typing commands:
  - ✅ Mark Done
  - 🗑 Delete
  - ⏰ Add Reminder (15min, 1h, 3h, 1d)
* **Reminders:** APScheduler cron checks every minute — you never miss a deadline.
* **Persistent Storage:** SQLite database (with Render Disk for cloud hosting).

## 🛠 Tech Stack

* **Language:** Python 3.10+
* **Library:** [aiogram 3.x](https://docs.aiogram.dev/) (Async Telegram Bot API)
* **Database:** SQLite
* **Scheduling:** APScheduler (interval trigger every 1 min)

## 🚀 Local Setup

1. **Get a Bot Token:** Message [@BotFather](https://t.me/botfather) on Telegram.
2. **Clone & Install:**
   ```bash
   cd gidbot
   pip install -r requirements.txt
   ```
3. **Configure:** Copy `.env.example` to `.env` and add your `BOT_TOKEN`.
4. **Run:**
   ```bash
   python bot.py
   ```

## ☁️ Deploy on Render

1. Push this repo to GitHub.
2. In [Render Dashboard](https://dashboard.render.com/), create a **Background Worker**.
3. Connect your repo — Render will detect `render.yaml`.
4. Set `BOT_TOKEN` in Environment (Settings → Environment).
5. Deploy. The worker runs 24/7 with persistent disk for SQLite.

The `render.yaml` defines a worker with:
- Persistent disk (`/opt/render/project/src/data`) for task storage
- APScheduler running reminder checks every minute

## 📋 Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome & main menu (inline buttons) |
| `/add <title>` | Add task (use `\|` for description) |
| `/list` | View tasks with inline buttons |
| `/achievements` | View badges and stats |
| `/help` | How to use the bot |
| `/cancel` | Cancel current action (e.g. add task) |

## Example

```
/add Buy groceries | Milk, eggs, bread
/add Call Mom
```

Then use inline buttons: **Mark Done**, **Delete**, **Add Reminder**.
