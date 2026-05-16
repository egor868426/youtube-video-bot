# 🎬 YouTube Video Finder Bot

A Telegram bot that searches YouTube and uses AI to rank the most useful results for your query.

**[@infoFindd_bot](https://t.me/infoFindd_bot)** — try it now

---

## What it does

1. You type `найди [query]` (or `search [query]`)
2. The bot fetches 10 YouTube videos
3. AI (Llama 3.3 70B via Groq) picks the 3–5 most relevant ones
4. You get a ranked list with a short explanation for each video

No ads. No sponsored results. Just the most useful videos for what you're actually looking for.

---

## Demo

| Command | Result |
|--------|--------|
| `найди как работает нейронная сеть` | Top 3–5 videos about neural networks, ranked by relevance |
| `search python async await` | Best tutorials ranked by AI |

> Screenshot coming soon — try it yourself at [@infoFindd_bot](https://t.me/infoFindd_bot)

---

## Features

- **AI ranking** — not just search results, but curated picks with explanations
- **Any topic** — programming, science, cooking, music — anything on YouTube
- **Natural chat** — talk to the bot freely, it responds in context
- **Fast** — results in ~5 seconds
- **Free** — no limits, no sign-up

---

## Tech stack

- **Python** + python-telegram-bot
- **yt-dlp** — YouTube search
- **Groq API** — Llama 3.3 70B for ranking, Llama 3.1 8B for chat
- **Railway** — 24/7 deployment

---

## Run locally

```bash
git clone https://github.com/egor868426/youtube-video-bot
cd youtube-video-bot
pip install -r requirements.txt

export BOT_TOKEN=your_telegram_bot_token
export GROQ_API_KEY=your_groq_api_key

python bot.py
```

---

## Deploy to Railway

1. Fork this repo
2. Create a new Railway project → Deploy from GitHub
3. Add environment variables: `BOT_TOKEN`, `GROQ_API_KEY`
4. Railway auto-deploys on every push

---

## Author

Built by [@egor868426](https://github.com/egor868426) as part of a 30-day AI project challenge.
