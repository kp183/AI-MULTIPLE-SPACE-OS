# core/ai_feed.py
from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Optional

# Optional: natural-language polish via VertexAI (graceful fallback if unavailable)
_USE_VERTEX = True
_model = None

def _maybe_init_vertex() -> None:
    global _model
    if _model is not None:
        return
    if not _USE_VERTEX:
        return
    try:
        from dotenv import load_dotenv
        load_dotenv()
        import vertexai
        from vertexai.generative_models import GenerativeModel

        # vertexai.init(project="YOUR_PROJECT_ID", location="us-central1")  # optional
        _model = GenerativeModel("gemini-1.0-pro")
    except Exception:
        _model = None


def _nlp_polish(text: str) -> str:
    """Optionally send to Gemini for a crisper phrasing."""
    _maybe_init_vertex()
    if _model is None:
        return text
    try:
        resp = _model.generate_content(
            f"Rewrite the following as a friendly, concise feed card (keep emojis if present):\n\n{text}"
        )
        return (resp.text or "").strip() or text
    except Exception:
        return text


def _format_time(dt: datetime) -> str:
    return dt.strftime("%a, %b %d at %I:%M %p")


def _pick_top_app(usage_counts: Dict[str, int]) -> Optional[str]:
    if not usage_counts:
        return None
    return max(usage_counts, key=usage_counts.get)


def generate_feed_cards(profile: dict) -> List[Dict[str, str]]:
    """
    Returns a list of feed 'cards'.
    Each card is: { 'icon': '📌', 'title': '...', 'body': '...' }
    """
    cards: List[Dict[str, str]] = []

    username = profile.get("username", "User")
    age = int(profile.get("age", 18))
    usage_counts: Dict[str, int] = profile.get("usage_counts", {}) or {}
    streak = profile.get("streak", {}) or {}
    last_opened = profile.get("last_opened_app")
    reminders: List[dict] = profile.get("reminders", []) or []

    # --- 1) Time-of-day ---
    hour = datetime.now().hour
    if 6 <= hour < 12:
        cards.append({
            "icon": "🌅",
            "title": "Good morning!",
            "body": _nlp_polish("Start strong: jot a quick plan in Notes or review a reminder.")
        })
    elif 12 <= hour < 18:
        cards.append({
            "icon": "🌤️",
            "title": "Good afternoon!",
            "body": _nlp_polish("Take a short focus sprint. Capture ideas in Notes or enjoy a mindful break.")
        })
    else:
        cards.append({
            "icon": "🌙",
            "title": "Good evening!",
            "body": _nlp_polish("Wind down gently. Review your day in Notes or set a reminder for tomorrow.")
        })

    # --- 2) Usage spotlight ---
    top_app = _pick_top_app(usage_counts)
    if top_app:
        count = usage_counts.get(top_app, 0)
        cards.append({
            "icon": "📊",
            "title": "Your activity spotlight",
            "body": _nlp_polish(f"You’ve opened **{top_app}** {count} time(s). Keep momentum or try something new!")
        })
    else:
        cards.append({
            "icon": "✨",
            "title": "Try something",
            "body": _nlp_polish("No usage yet. Tap an app to get started — Notes, Gallery, or Games.")
        })

    # --- 3) Streak nudges ---
    s_app = streak.get("app")
    s_len = int(streak.get("len", 0) or 0)
    if s_app and s_len >= 2:
        cards.append({
            "icon": "🔥",
            "title": "Streak on!",
            "body": _nlp_polish(f"You’re on a **{s_len}×** streak with **{s_app}**. Want to keep it going?")
        })

    # --- 4) Upcoming reminders ---
    now = datetime.now()
    upcoming = []
    for r in reminders:
        try:
            when_iso = r.get("when_iso")
            if not when_iso:
                continue
            when = datetime.fromisoformat(when_iso)
            if when >= now:
                upcoming.append((when, r.get("text", "Reminder")))
        except Exception:
            continue

    upcoming.sort(key=lambda x: x[0])
    if upcoming:
        top = upcoming[:2]
        body_lines = [f"• **{txt}** — { _format_time(when) }" for when, txt in top]
        cards.append({
            "icon": "⏰",
            "title": "Upcoming reminders",
            "body": _nlp_polish("\n".join(body_lines))
        })

    # --- 5) Age-aware guidance ---
    if age < 13:
        cards.append({
            "icon": "🎨",
            "title": "Creative spark",
            "body": _nlp_polish("Draw something fun in Notes — maybe a **space robot** or **dancing tiger**!")
        })
        cards.append({
            "icon": "🛡️",
            "title": "Stay safe",
            "body": _nlp_polish("Always check with a parent before sharing info online.")
        })
    elif 13 <= age < 18:
        cards.append({
            "icon": "📚",
            "title": "Study reminder",
            "body": _nlp_polish("Review today’s lessons for at least 20 minutes to stay sharp.")
        })
        cards.append({
            "icon": "🎧",
            "title": "Take a break",
            "body": _nlp_polish("Music or a short walk can help you recharge your focus.")
        })
    else:
        cards.append({
            "icon": "💼",
            "title": "Productivity tip",
            "body": _nlp_polish("Try 25-minute focus sessions with 5-minute breaks for better productivity.")
        })
        cards.append({
            "icon": "🌿",
            "title": "Digital detox",
            "body": _nlp_polish("Step away from screens for a short walk to refresh your mind.")
        })

    # --- 6) Balance nudge ---
    if usage_counts:
        max_count = max(usage_counts.values())
        if max_count >= 5:
            mostly = _pick_top_app(usage_counts)
            if mostly:
                cards.append({
                    "icon": "🧘",
                    "title": "Balance nudge",
                    "body": _nlp_polish(f"You’ve spent a lot of time in **{mostly}**. A 2-minute pause can reset your focus.")
                })

    # --- 7) Last opened continuity ---
    if last_opened:
        cards.append({
            "icon": "🔁",
            "title": "Continue where you left off",
            "body": _nlp_polish(f"Last opened: **{last_opened}**. Want to jump back in?")
        })

    return cards
