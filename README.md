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

## ☁️ Deploy on Render (Blueprint)

1. Push this repo to GitHub.
2. In [Render Dashboard](https://dashboard.render.com/): **New +** → **Blueprint** → select this repo.
3. Click **Apply** so Render creates the worker and its persistent disk from `render.yaml`.
4. Open the **taskmaster-bot** service → **Environment** → set **BOT_TOKEN** (paste your Telegram bot token).
5. Save; Render redeploys. Check **Logs** for `Starting polling...`.

The Blueprint (`render.yaml`) defines:
- **Background Worker** (Python 3.11), build: `pip install -r requirements.txt`, start: `python bot.py`
- **1 GB persistent disk** at `data/` so SQLite tasks survive deploys
- **BOT_TOKEN** must be set by you in the service Environment

Full steps: [DEPLOY.md](DEPLOY.md#deploy-on-render-with-blueprint).

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
