# core/assistant.py
import re
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# --- Firebase Profile Manager ---
from .profile_manager import (
    get_user_profile,
    update_user_profile,
    ensure_profile_defaults,
    add_reminder,
)

# --- Greeting state (to reduce repetition) ---
_last_greeting: Optional[str] = None
_greet_count: int = 0


# -------- Intent Parsing --------
def parse_intent(text: str, available_apps: List[str]) -> Dict:
    """
    Parse a user command into an intent dictionary.
    Returns: {"action": <str>, ...}
    Supported actions:
        open_app, most_used, streak, add_reminder, list_reminders,
        get_time, get_date, joke, about, help, greet, unknown
    """
    if not text:
        return {"action": "unknown"}

    t = text.strip().lower()

    # greetings
    greetings = [
        "hello", "hi", "hey", "yo", "sup", "what's up", "whats up",
        "good morning", "good evening", "good afternoon",
        "how are you", "how r u", "how ru", "how r you"
    ]
    if any(g in t for g in greetings):
        return {"action": "greet"}

    # open app
    if any(w in t for w in ["open ", "launch ", "start "]):
        for app in available_apps:
            if app.lower() in t:
                return {"action": "open_app", "app": app}

    # most used
    if "most used" in t or "what did i do most" in t or "usage" in t:
        return {"action": "most_used"}

    # streak
    if "streak" in t:
        return {"action": "streak"}

    # list reminders
    if "show reminders" in t or "my reminders" in t or "list reminders" in t:
        return {"action": "list_reminders"}

    # add reminder
    if "remind me" in t or t.startswith("remind "):
        task = None
        m = re.search(r"remind (?:me )?(?:to )?(.*)", t)
        if m:
            task = m.group(1)
        due = parse_due_datetime(t)
        return {"action": "add_reminder", "task": task or "something", "due": due}

    # time check
    if "time" in t and ("what" in t or "current" in t):
        return {"action": "get_time"}

    # date check
    if "date" in t or "day is it" in t:
        return {"action": "get_date"}

    # joke
    if "joke" in t:
        return {"action": "joke"}

    # about
    if "who created you" in t or "what are you" in t or "who are you" in t:
        return {"action": "about"}

    # help
    if "help" in t or "what can you do" in t:
        return {"action": "help"}

    return {"action": "unknown"}


def parse_due_datetime(text: str) -> datetime:
    """Extract a due datetime from natural language text."""
    now = datetime.now()

    if "tomorrow" in text:
        base = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
        return parse_time_of_day(text, default=base)

    if "today" in text:
        base = now.replace(second=0, microsecond=0)
        return parse_time_of_day(text, default=base + timedelta(hours=1))

    m = re.search(r"in\s+(\d+)\s+(minute|minutes|hour|hours)", text)
    if m:
        qty = int(m.group(1))
        unit = m.group(2)
        delta = timedelta(minutes=qty) if "minute" in unit else timedelta(hours=qty)
        return (now + delta).replace(second=0, microsecond=0)

    # fallback to "at X am/pm"
    t = parse_time_of_day(text, default=None)
    if t:
        return t

    # final fallback: +1 hour
    return (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)


def parse_time_of_day(text: str, default: Optional[datetime]) -> Optional[datetime]:
    """Parse explicit time from text (e.g., 'at 5pm')."""
    now = datetime.now()
    m = re.search(r"at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text)
    if not m:
        return default

    hour = int(m.group(1))
    minute = int(m.group(2) or 0)
    ampm = m.group(3)

    if ampm:
        ampm = ampm.lower()
        if ampm == "pm" and hour < 12:
            hour += 12
        if ampm == "am" and hour == 12:
            hour = 0

    return now.replace(hour=hour, minute=minute, second=0, microsecond=0)


# -------- Intent Handling --------
def handle_intent(username: str, available_apps: List[str], intent: Dict, original_text: str) -> Tuple[str, Optional[str]]:
    """
    Handle the parsed intent and return:
        (assistant_reply, app_to_open or None)
    """
    profile = ensure_profile_defaults(get_user_profile(username) or {})
    usage = profile.get("usage_counts", {})
    streak = profile.get("streak", {"app": None, "len": 0})

    action = intent.get("action")

    if action == "open_app":
        app = intent.get("app")
        if app in available_apps:
            return f"Opening {app} ✅", app
        return f"App '{app}' not found.", None

    if action == "most_used":
        if not usage:
            return "No usage data yet.", None
        most_used = max(usage, key=usage.get)
        count = usage[most_used]
        return f"Most used: {most_used} ({count} times).", None

    if action == "streak":
        s_app = streak.get("app")
        s_len = int(streak.get("len", 0) or 0)
        if s_app and s_len > 1:
            return f"🔥 {s_len}× streak with {s_app}!", None
        return "No active streak yet.", None

    if action == "list_reminders":
        reminders = profile.get("reminders", [])
        if not reminders:
            return "No reminders set.", None
        sorted_rem = sorted(reminders, key=lambda r: r.get("due", ""))
        lines = [f"- {r['text']} ({format_human_time(r.get('due'))})" for r in sorted_rem[:5]]
        return "Reminders:\n" + "\n".join(lines), None

    if action == "add_reminder":
        task = (intent.get("task") or "something").strip()
        due_dt = intent.get("due")
        due_iso = due_dt.isoformat() if isinstance(due_dt, datetime) else None
        add_reminder(username, task, due_iso)
        return f"Reminder added ✅ {task} ({format_human_time(due_iso)})", None

    if action == "get_time":
        return f"⏰ {datetime.now().strftime('%I:%M %p')}", None

    if action == "get_date":
        return f"📅 {datetime.now().strftime('%A, %B %d, %Y')}", None

    if action == "joke":
        jokes = [
            "Why don’t skeletons fight? They don’t have the guts.",
            "Why did the computer go to the doctor? It caught a virus.",
            "I told my phone I needed a break… now it sends me Kit-Kats.",
            "Why don’t programmers like nature? Too many bugs.",
            "Why did the developer go broke? He used up all his cache.",
        ]
        return random.choice(jokes), None

    if action == "about":
        return "I’m your AI launcher assistant 🤖", None

    if action == "help":
        return (
            "Try:\n"
            "- Open Notes / Launch Gallery\n"
            "- What's my most used app?\n"
            "- Show my streak\n"
            "- Remind me to study tomorrow 7pm\n"
            "- Show reminders\n"
            "- What time is it? / What's today’s date?\n"
            "- Tell me a joke"
        ), None

    if action == "greet":
        global _last_greeting, _greet_count
        text_lower = original_text.lower()
        _greet_count += 1

        # If user asks "how are you"
        if "how are" in text_lower or "how r" in text_lower:
            responses = [
                "Doing great! How about you?",
                "All good 🚀 Ready to help!",
                "I’m awesome — how are you?",
            ]
            reply = random.choice(responses)
            _last_greeting = reply
            return reply, None

        # Too many greetings in a row
        if _greet_count > 3:
            special_responses = [
                "Haha, lots of hellos 😄",
                "Still here 👋 Want me to do something?",
                "Hello again! Ready when you are.",
            ]
            reply = random.choice(special_responses)
            _last_greeting = reply
            return reply, None

        # Normal greetings (avoid repeating last one)
        responses = [
            "Hello 👋",
            "Hey! How’s it going?",
            "Hi there!",
            "Good to see you!",
            "Yo 👊",
        ]
        choices = [r for r in responses if r != _last_greeting] or responses
        reply = random.choice(choices)

        _last_greeting = reply
        return reply, None

    # --- Fallback ---
    return "Sorry, didn’t get that. Try **help**.", None


def format_human_time(iso: Optional[str]) -> str:
    """Format ISO timestamp into a human-friendly string."""
    if not iso:
        return "soon"
    try:
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%a, %b %d at %I:%M %p")
    except Exception:
        return iso
