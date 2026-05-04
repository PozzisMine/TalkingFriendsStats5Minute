import json
import os
import requests
from datetime import datetime, timezone

API_KEY = os.environ.get("YOUTUBE_API_KEY")

if not API_KEY:
    raise Exception("YOUTUBE_API_KEY не найден в GitHub Secrets")

with open("channels.txt", "r", encoding="utf-8") as f:
    channel_ids = [line.strip() for line in f if line.strip()]

channel_ids = channel_ids[:20]

if not channel_ids:
    raise Exception("channels.txt пустой")

url = "https://www.googleapis.com/youtube/v3/channels"

params = {
    "part": "snippet,statistics",
    "id": ",".join(channel_ids),
    "key": API_KEY
}

response = requests.get(url, params=params)
data = response.json()

if response.status_code != 200:
    raise Exception(data)

channels = []

for item in data.get("items", []):
    stats = item.get("statistics", {})
    snippet = item.get("snippet", {})
    thumbs = snippet.get("thumbnails", {})

    avatar = (
        thumbs.get("high", {}).get("url")
        or thumbs.get("medium", {}).get("url")
        or thumbs.get("default", {}).get("url")
        or ""
    )

    channel_id = item.get("id")

    channels.append({
        "id": channel_id,
        "title": snippet.get("title", "Без названия"),
        "avatar": avatar,
        "url": f"https://www.youtube.com/channel/{channel_id}",
        "subscribers": int(stats.get("subscriberCount", 0)),
        "views": int(stats.get("viewCount", 0)),
        "videos": int(stats.get("videoCount", 0))
    })

now = datetime.now(timezone.utc).isoformat()

current = {
    "updated_at": now,
    "total_channels": len(channels),
    "total_subscribers": sum(c["subscribers"] for c in channels),
    "total_views": sum(c["views"] for c in channels),
    "total_videos": sum(c["videos"] for c in channels),
    "channels": channels
}

with open("stats.json", "w", encoding="utf-8") as f:
    json.dump(current, f, ensure_ascii=False, indent=2)

try:
    with open("history.json", "r", encoding="utf-8") as f:
        history = json.load(f)
except FileNotFoundError:
    history = []

history.append(current)

# Храним последние 10000 обновлений
history = history[-10000:]

with open("history.json", "w", encoding="utf-8") as f:
    json.dump(history, f, ensure_ascii=False, indent=2)

print("stats.json и history.json обновлены")
