import os
import time
from collections import defaultdict

from agno.agent import Agent
from dotenv import load_dotenv

from database import SessionLocal, engine
from models import Article, Base
from tools import search_images, search_papers, search_videos, search_web

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

import requests

class GroqModel:
    def __init__(self, api_key, model="llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt):
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        data = response.json()

        if "choices" not in data:
            print("Groq FULL ERROR:", data)  # 👈 debug log

        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return f"Groq API Error: {data.get('error', data)}"
    
class GroqAgentWrapper:
    def __init__(self, model):
        self.model = model

    def run(self, prompt):
        output = self.model.generate(prompt)

        class Response:
            def __init__(self, content):
                self.content = content

        return Response(output)

# Create tables
Base.metadata.create_all(bind=engine)


groq_model = GroqModel(api_key=api_key)

summary_agent = GroqAgentWrapper(groq_model)


def normalize_text(value: str) -> str:
    """Create a stable key for comparing results across repeated searches."""
    return " ".join((value or "").lower().strip().split())


def result_key(item: dict) -> str:
    """
    Prefer link for uniqueness. Fall back to title when the link is missing.
    """
    link = normalize_text(item.get("link", "") or item.get("url", ""))
    title = normalize_text(item.get("title", ""))
    return link or title


# 🔹 Ranking Function
def rank_results(results, topic):
    for item in results:
        text = (item.get("title", "") + item.get("snippet", "")).lower()
        item["score"] = text.count(topic.lower())
    return sorted(results, key=lambda x: x.get("score", 0), reverse=True)[:5]


def fetch_previous_web_results(topic: str):
    """Pull previously stored search results for the same topic."""
    db = SessionLocal()
    try:
        rows = (
            db.query(Article)
            .filter(Article.topic == topic)
            .order_by(Article.created_at.desc())
            .all()
        )
        previous = []
        for row in rows:
            previous.append(
                {
                    "title": row.title,
                    "link": row.url,
                    "snippet": row.snippet,
                    "score": row.score or 0,
                    "published": row.created_at.isoformat() if row.created_at else "N/A",
                    "_source": "history",
                }
            )
        return previous
    finally:
        db.close()


def compare_runs(current_results, previous_results):
    """
    Combine the latest search with the saved history and return:
    - best_result: the strongest single result across all runs
    - compared_results: de-duplicated ranking across all runs
    """
    grouped = defaultdict(lambda: {
        "title": "",
        "link": "",
        "snippet": "",
        "published": "N/A",
        "score": 0,
        "history_hits": 0,
        "latest_hits": 0,
        "_source": "history",
    })

    def absorb(item, is_current: bool):
        if item.get("error"):
            return

        key = result_key(item)
        if not key:
            return

        bucket = grouped[key]
        bucket["title"] = bucket["title"] or item.get("title", "")
        bucket["link"] = bucket["link"] or item.get("link", "")
        bucket["snippet"] = bucket["snippet"] or item.get("snippet", "")
        bucket["published"] = bucket["published"] if bucket["published"] != "N/A" else item.get("published", "N/A")
        bucket["score"] = max(bucket["score"], int(item.get("score", 0) or 0))
        if is_current:
            bucket["latest_hits"] += 1
            bucket["_source"] = "latest"
        else:
            bucket["history_hits"] += 1

    for item in previous_results:
        absorb(item, is_current=False)

    for item in current_results:
        absorb(item, is_current=True)

    compared_results = []
    for item in grouped.values():
        # Boost items that appeared both before and now.
        item["combined_score"] = item["score"] + (item["history_hits"] * 2) + item["latest_hits"]
        compared_results.append(item)

    compared_results.sort(
        key=lambda x: (
            x.get("combined_score", 0),
            x.get("latest_hits", 0),
            x.get("history_hits", 0),
        ),
        reverse=True,
    )

    best_result = compared_results[0] if compared_results else {}

    return best_result, compared_results


# 🔹 Summary
def build_summary(topic, web_results, papers, videos=None):
    text = ""
    for w in web_results:
        text += w.get("snippet", "") + "\n"

    if videos:
        for v in videos:
            text += v.get("snippet", "") + "\n"

    prompt = f"""
You are a helpful assistant.

Instructions:
- Summarize the topic in simple English
- Use only the given data
- Keep it short

Topic: {topic}

Data:
{text}
"""

    try:
        response = summary_agent.run(prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        return f"Summary failed: {str(e)}"


# 🔹 Main Function
def run_research(topic):
    start = time.time()

    previous_results = fetch_previous_web_results(topic)

    web = search_web(topic)
    web = rank_results(web, topic)

    best_result, compared_results = compare_runs(web, previous_results)

    images = search_images(topic)
    videos = search_videos(topic)
    papers = search_papers(topic)
    summary = build_summary(topic, web, papers, videos)

    # Save latest run to DB
    db = SessionLocal()
    try:
        for item in web:
            if not item.get("error"):
                article = Article(
                    topic=topic,
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    score=item.get("score", 0),
                )
                db.add(article)
        db.commit()
    finally:
        db.close()

    runtime = round(time.time() - start, 2)

    return {
        "topic": topic,
        "summary": summary,
        "web_results": web,
        "best_result": best_result,
        "compared_results": compared_results,
        "previous_runs_count": len(previous_results),
        "images": images,
        "videos": videos,
        "papers": papers,
        "runtime": runtime
    }
