# 📱 Telegram bot setup (BotFather)

Use these with [@BotFather](https://t.me/botfather) to make your bot official.

---

## 1. Short description (≤120 chars)

**Used in:** Bot search results and profile header.

```
Your personal task manager. Add tasks, set reminders, and tick them off with inline buttons—all inside Telegram.
```

*(119 characters)*

---

## 2. Description (≤512 chars)

**Used in:** Bot profile — tap the bot name to see this.

```
TaskMaster helps you stay on top of your to‑do list without leaving Telegram.

✨ Add tasks with titles and optional descriptions
✅ Mark tasks done or delete them with one tap (inline buttons)
⏰ Set reminders in 15m, 1h, 3h, or 1 day
📋 View all tasks and filter by active or completed
🏆 Unlock achievements as you complete tasks and build streaks

Your list syncs across devices. No account signup—just start chatting. Perfect for quick capture and daily planning.
```

---

## 3. About (≤120 chars)

**Used in:** Short bio under the bot name in profile.

```
To‑do list + reminders + achievements. Manage tasks with inline buttons.
```

*(72 characters)*

---

## 4. Commands to set in BotFather

In BotFather, send **Set Commands** (or `/setcommands`), choose your bot, then paste:

```
start - Open the bot and show menu
add - Add a new task (e.g. /add Buy milk)
list - View all tasks with actions
achievements - View your badges and stats
help - How to use the bot
cancel - Cancel current action
```

---

## 5. Optional: Bot profile picture

- Use a simple icon (checklist, clipboard, or “TM” logo).
- Square, at least 256×256 px; Telegram will resize as needed.
- In BotFather: **Edit Bot** → **Edit botpic** and send the image.

---

## 6. Optional: Inline mode

If you want the bot to appear in other chats via `@YourBotName task title`:

- In BotFather: **Edit Bot** → **Bot Settings** → **Inline Mode** → Turn on.
- Your code does not handle inline queries yet; this is only if you add that feature later.

For now you can leave **Inline Mode** off.
