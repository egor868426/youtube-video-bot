import os
import json
from groq import Groq

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """Ты помощник по подбору видео. Пользователь ищет видео по запросу.
Из списка видео выбери 3-5 самых полезных и релевантных.

Верни JSON-массив (только выбранные видео, в порядке от лучшего к худшему):
[
  {
    "url": "ссылка на видео",
    "reason": "1-2 предложения на русском — почему это видео полезно для данного запроса"
  }
]

Отвечай ТОЛЬКО валидным JSON, без пояснений."""


def rank_videos(query: str, videos: list[dict]) -> list[dict]:
    videos_text = "\n".join(
        f"{i+1}. {v['title']} | {v['channel']} | {v['duration']} | {v['views']}\n   {v['description']}\n   URL: {v['url']}"
        for i, v in enumerate(videos)
    )
    prompt = f"Запрос пользователя: «{query}»\n\nВидео:\n{videos_text}"

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=600,
        )
        text = response.choices[0].message.content.strip()
        ranked = json.loads(text)

        url_map = {v["url"]: v for v in videos}
        result = []
        for r in ranked:
            video = url_map.get(r["url"], {})
            result.append({
                "title": video.get("title", ""),
                "url": r["url"],
                "channel": video.get("channel", ""),
                "duration": video.get("duration", ""),
                "reason": r.get("reason", ""),
            })
        return result
    except Exception as e:
        return [{"title": v["title"], "url": v["url"], "channel": v["channel"],
                 "duration": v["duration"], "reason": "Релевантное видео по запросу"} for v in videos[:3]]
