# 🚀 Deploy checklist (Git + Render Blueprint)

Use this before your first push and when going live.

---

## Before pushing to Git

- [ ] **Never commit secrets**
  - `.env` is in `.gitignore` — confirm it's not tracked:  
    `git status` (you should not see `.env`).
  - If `.env` was ever committed, remove it from history and rotate `BOT_TOKEN`.

- [ ] **Create `.env` from example (locally only)**
  ```bash
  cp .env.example .env
  # Edit .env and set BOT_TOKEN=your_real_token
  ```

- [ ] **Test locally**
  ```bash
  pip install -r requirements.txt
  python bot.py
  ```
  - Send `/start`, add a task, use inline buttons, set a reminder. Confirm no errors.

- [ ] **Optional: set BotFather copy**
  - Use [TELEGRAM.md](TELEGRAM.md) to set short description, description, about, and commands in BotFather.

---

## Push to GitHub

```bash
git init
git add .
git status   # Ensure .env and data/ are not listed
git commit -m "Initial commit: TaskMaster bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/gidbot.git
git push -u origin main
```

Replace `YOUR_USERNAME` and repo name if different.

---

## Deploy on Render with Blueprint

This repo includes a **Render Blueprint** (`render.yaml`). One Blueprint creates the worker and its persistent disk.

### 1. Connect the repo

1. Go to [dashboard.render.com](https://dashboard.render.com/).
2. Click **New +** → **Blueprint**.
3. Connect your GitHub account if needed, then select the **gidbot** repository.
4. Render will detect `render.yaml` and show the services it will create (e.g. **taskmaster-bot** worker).

### 2. Apply the Blueprint

1. Click **Apply**.
2. Render creates the **Background Worker** and attaches a **1 GB persistent disk** for SQLite.

### 3. Set BOT_TOKEN

1. Open the new **taskmaster-bot** service.
2. Go to **Environment** (left sidebar).
3. Find **BOT_TOKEN** — it will say "Sync: Not set" or ask for a value.
4. Click **Add Value** or edit, and paste your Telegram bot token (same as in `.env` locally).
5. Save. Render will redeploy the service.

### 4. Deploy and verify

1. Wait for the deploy to finish (Build → Start). Check **Logs** for:
   - `Scheduler started for reminders`
   - `Starting polling...`
   - No Python tracebacks.
2. Open your bot in Telegram and send `/start`. Add a task, complete one, set a reminder.

### What the Blueprint sets

| Setting        | Value                                      |
|----------------|--------------------------------------------|
| Type           | Background Worker                         |
| Runtime        | Python                                    |
| Build          | `pip install -r requirements.txt`         |
| Start          | `python bot.py`                           |
| Disk           | 1 GB at `/opt/render/project/src/data` (required—tasks persist here) |
| DATABASE_PATH  | Set to disk path (tasks persist)           |
| BOT_TOKEN      | You must set this in Environment          |
| PYTHON_VERSION | 3.11.9 (required: full major.minor.patch) |

---

## After going live

- **BotFather:** Set description and commands (see [TELEGRAM.md](TELEGRAM.md)) so the bot looks official in search and profile.
- **README:** Update the deploy section with your bot’s username or link if you want to share it.
- **Monitoring:** Check Render logs and Telegram for errors; set up Render alerts if needed.
