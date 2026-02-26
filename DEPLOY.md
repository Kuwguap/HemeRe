# 🚀 Deploy checklist (Git + Render)

Use this before your first push and when going live.

---

## Before pushing to Git

- [ ] **Never commit secrets**
  - `.env` is in `.gitignore` — confirm it’s not tracked:  
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

Replace `YOUR_USERNAME` with your GitHub username (or org) and repo name if different.

---

## Deploy on Render

1. **Log in** at [dashboard.render.com](https://dashboard.render.com/).

2. **New → Background Worker**
   - Connect your GitHub account and select the `gidbot` repo.
   - Render can auto-detect `render.yaml`; if so, use that blueprint.

3. **Environment**
   - Add **BOT_TOKEN**: paste your bot token (same as in `.env`).
   - Do not commit this value; set it only in Render’s Environment tab.

4. **Deploy**
   - Trigger a deploy. Build: `pip install -r requirements.txt`. Start: `python bot.py`.
   - Check the **Logs** tab for “Starting polling…” and no Python tracebacks.

5. **Persistent disk**
   - If you use the `render.yaml` from this repo, a 1 GB disk is attached for SQLite. Tasks persist across deploys.

6. **Test the live bot**
   - Open your bot in Telegram, send `/start`, add a task, complete one, set a reminder. Confirm reminders fire (scheduler runs every minute).

---

## After going live

- **BotFather:** Set description and commands (see [TELEGRAM.md](TELEGRAM.md)) so the bot looks official in search and profile.
- **README:** Update the “Deploy on Render” section with your bot’s username or link if you want to share it.
- **Monitoring:** Check Render logs and Telegram for errors; set up Render alerts if needed.
