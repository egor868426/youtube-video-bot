import yt_dlp


def search_videos(query: str, limit: int = 10) -> list[dict]:
    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
    }
    url = f"ytsearch{limit}:{query}"
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        entries = info.get("entries", []) if info else []

    videos = []
    for v in entries:
        if not v:
            continue
        duration_sec = int(v.get("duration") or 0)
        duration = f"{duration_sec // 60}:{duration_sec % 60:02d}" if duration_sec else ""
        views = v.get("view_count") or 0
        views_str = f"{views:,}".replace(",", " ") if views else ""
        videos.append({
            "title": v.get("title", ""),
            "url": f"https://youtube.com/watch?v={v.get('id', '')}",
            "channel": v.get("channel") or v.get("uploader", ""),
            "duration": duration,
            "views": views_str,
            "description": (v.get("description") or "")[:200],
        })
    return videos
