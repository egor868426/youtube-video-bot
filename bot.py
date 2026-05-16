import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from youtube_search import search_videos
from ranker import rank_videos
from groq import Groq

TOKEN = os.environ["BOT_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

CHAT_SYSTEM = """Ты дружелюбный ассистент. Отвечай коротко и по делу на русском языке.
Если пользователь хочет найти видео — напомни что нужно написать «найди [запрос]»."""


async def do_search(update: Update, query: str):
    await update.message.reply_text(f"🔍 Ищу видео по запросу «{query}»...")
    videos = search_videos(query, limit=10)
    if not videos:
        await update.message.reply_text("Ничего не нашёл, попробуй другой запрос.")
        return
    ranked = rank_videos(query, videos)
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
    for trigger in ["найди", "найти", "поищи", "search"]:
        if lower.startswith(trigger):
            query = text[len(trigger):].strip()
            if query:
                await do_search(update, query)
                return
            else:
                await update.message.reply_text("Что искать? Напиши: найди [запрос]")
                return

    # Обычный чат
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": CHAT_SYSTEM},
            {"role": "user", "content": text},
        ],
        temperature=0.7,
        max_tokens=300,
    )
    await update.message.reply_text(response.choices[0].message.content.strip())


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я помогу найти нужные видео на YouTube.\n\n"
        "Напиши <b>найди [запрос]</b> — и я подберу лучшие видео с объяснением.\n"
        "Или просто общайся со мной 🙂",
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
