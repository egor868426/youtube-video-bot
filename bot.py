import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from youtube_search import search_videos
from ranker import rank_videos
from groq import Groq

TOKEN = os.environ["BOT_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

CHAT_SYSTEM_RU = """Ты дружелюбный ассистент. Отвечай коротко и по делу на русском языке.
Если пользователь хочет найти видео — напомни что нужно написать «найди [запрос]»."""

CHAT_SYSTEM_EN = """You are a friendly assistant. Reply briefly and to the point in English.
If the user wants to find videos — remind them to type 'search [query]'."""


async def do_search(update: Update, query: str, lang: str = "ru"):
    if lang == "en":
        await update.message.reply_text(f"🔍 Searching for «{query}»...")
    else:
        await update.message.reply_text(f"🔍 Ищу видео по запросу «{query}»...")
    videos = search_videos(query, limit=10)
    if not videos:
        msg = "Nothing found, try a different query." if lang == "en" else "Ничего не нашёл, попробуй другой запрос."
        await update.message.reply_text(msg)
        return
    ranked = rank_videos(query, videos, lang=lang)
    if lang == "en":
        lines = [f"🎬 <b>Top videos for «{query}»</b>\n"]
    else:
        lines = [f"🎬 <b>Топ видео по запросу «{query}»</b>\n"]
    for i, v in enumerate(ranked, 1):
        duration = f" · {v['duration']}" if v.get("duration") else ""
        lines.append(
            f"{i}. <a href=\"{v['url']}\">{v['title']}</a>\n"
            f"   <i>{v['channel']}{duration}</i>\n"
            f"   {v['reason']}\n"
        )
    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    lower = text.lower()

    # Триггер поиска
    en_triggers = ["search"]
    ru_triggers = ["найди", "найти", "поищи"]
    for trigger in en_triggers:
        if lower.startswith(trigger):
            query = text[len(trigger):].strip()
            if query:
                await do_search(update, query, lang="en")
            else:
                await update.message.reply_text("What to search? Type: search [query]")
            return
    for trigger in ru_triggers:
        if lower.startswith(trigger):
            query = text[len(trigger):].strip()
            if query:
                await do_search(update, query, lang="ru")
            else:
                await update.message.reply_text("Что искать? Напиши: найди [запрос]")
            return

    # Обычный чат — язык по тексту пользователя
    lang = "en" if lower.isascii() else "ru"
    chat_system = CHAT_SYSTEM_EN if lang == "en" else CHAT_SYSTEM_RU
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": chat_system},
            {"role": "user", "content": text},
        ],
        temperature=0.7,
        max_tokens=300,
    )
    await update.message.reply_text(response.choices[0].message.content.strip())


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! / Hi there!\n\n"
        "🇷🇺 Я помогу найти нужные видео на YouTube.\n"
        "Напиши <b>найди [запрос]</b> — подберу лучшие видео с объяснением.\n\n"
        "🇬🇧 I'll help you find the best YouTube videos.\n"
        "Type <b>search [query]</b> — I'll pick the most relevant ones with explanations.\n\n"
        "Или просто общайся / or just chat 🙂",
        parse_mode="HTML",
    )


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен. Триггер поиска: «найди [запрос]»")
    app.run_polling()


if __name__ == "__main__":
    main()
