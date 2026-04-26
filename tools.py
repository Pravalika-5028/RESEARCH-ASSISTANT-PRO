import os
from urllib.parse import parse_qs, urlparse

import feedparser
import requests
from dotenv import load_dotenv

load_dotenv()


import requests
from urllib.parse import urlparse, parse_qs

def _youtube_thumbnail_from_url(url: str) -> str:
    """Return best available YouTube thumbnail with fallback."""
    if not url:
        return ""

    try:
        parsed = urlparse(url)
        host = (parsed.netloc or "").lower()

        video_id = ""
        if "youtu.be" in host:
            video_id = parsed.path.strip("/")
        elif "youtube.com" in host:
            if parsed.path.startswith("/watch"):
                video_id = parse_qs(parsed.query).get("v", [""])[0]
            elif parsed.path.startswith("/shorts/"):
                video_id = parsed.path.split("/shorts/", 1)[1].split("/", 1)[0]
            elif parsed.path.startswith("/embed/"):
                video_id = parsed.path.split("/embed/", 1)[1].split("/", 1)[0]

        if video_id:
            base = f"https://img.youtube.com/vi/{video_id}"

            # Try highest → fallback
            for quality in ["maxresdefault.jpg", "sddefault.jpg", "hqdefault.jpg"]:
                thumb_url = f"{base}/{quality}"
                try:
                    r = requests.head(thumb_url)
                    if r.status_code == 200:
                        return thumb_url
                except:
                    continue

    except Exception:
        pass

    return ""

def search_web(query: str, num_results: int = 5):
    api_key = os.getenv("SERPER_API_KEY")

    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    payload = {"q": query, "num": num_results}

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        results = []
        for item in data.get("organic", []):
            results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet"),
                "published": item.get("date", "N/A")   # publish time
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]


def search_images(query: str):
    api_key = os.getenv("SERPER_API_KEY")

    url = "https://google.serper.dev/images"
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    payload = {"q": query}

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        return [{
            "title": img.get("title"),
            "image_url": img.get("imageUrl"),
            "source_url": img.get("sourceUrl")
        } for img in data.get("images", [])]
    except Exception as e:
        return [{"error": str(e)}]


def search_videos(query: str, num_results: int = 5):
    """Fetch YouTube video results for the topic via Serper's videos endpoint."""
    api_key = os.getenv("SERPER_API_KEY")

    url = "https://google.serper.dev/videos"
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    payload = {"q": query, "num": num_results}

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        results = []
        for item in data.get("videos", []):
            link = item.get("link", "") or ""
            source = (item.get("source") or item.get("channel") or "").lower()

            # Keep the section focused on YouTube results.
            if link and ("youtube.com" not in link.lower() and "youtu.be" not in link.lower() and source != "youtube"):
                continue

            thumbnail_url = _youtube_thumbnail_from_url(link)
            print("THUMBNAIL:", thumbnail_url)

            results.append({
                "title": item.get("title"),
                "link": link,
                "snippet": item.get("snippet"),
                "published": item.get("date", "N/A"),
                "thumbnail_url": thumbnail_url,
                "channel": item.get("channel") or item.get("source"),
                "duration": item.get("duration"),
            })

        return results[:num_results]
    except Exception as e:
        return [{"error": str(e)}]


def search_papers(query: str):
    url = "http://export.arxiv.org/api/query"
    params = {"search_query": f"all:{query}", "max_results": 5}

    try:
        response = requests.get(url, params=params)
        feed = feedparser.parse(response.text)

        papers = []
        for entry in feed.entries:
            papers.append({
                "title": entry.title,
                "summary": entry.summary,
                "link": entry.link,
                "published": entry.published
            })
        return papers
    except Exception as e:
        return [{"error": str(e)}]
