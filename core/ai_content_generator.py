# core/ai_content_generator.py
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
load_dotenv()

import vertexai
from vertexai.generative_models import GenerativeModel, Part

# --- AI Initialization ---
# This automatically uses the credentials from your service_account_key.json
try:
    vertexai.init(project="ai-os-469408", location="us-central1")
    print("Vertex AI initialized successfully!")
except Exception as e:
    print(f"Vertex AI initialization failed: {e}")

# Load the Gemini Pro model
model = GenerativeModel("gemini-1.0-pro")

def generate_personalized_content(profile):
    """
    Generates a personalized briefing for the user using the Gemini API.
    """
    if not profile or "age" not in profile:
        return "Could not generate content. User profile is incomplete."

    username = profile.get("username", "User")
    age = profile.get("age", 18)
    
    # --- Prompt Engineering ---
    # We create a different prompt based on the user's age.
    prompt = ""
    if age < 13: # For Children
        prompt = f"""
        You are a fun and friendly AI assistant for a kid's operating system.
        Your user's name is {username}.
        
        Generate a short, exciting daily briefing for them. Include the following sections using markdown:
        - A "Fun Fact of the Day" about animals or space.
        - A "Creative Challenge" with a simple, fun drawing idea (e.g., "a robot playing soccer").
        
        Make it cheerful and use emojis!
        """
    elif 13 <= age < 18: # For Teenagers
        prompt = f"""
        You are a cool and helpful AI assistant for a teenager's operating system.
        Your user's name is {username}.
        
        Generate a short, interesting daily briefing for them. Include the following sections using markdown:
        - A "Study Tip" for a common subject like Math or History.
        - A "Did You Know?" section about a fascinating historical event or scientific discovery.
        
        Keep the tone encouraging and modern.
        """
    else: # For Adults
        prompt = f"""
        You are a professional and efficient AI assistant for an adult's operating system.
        Your user's name is {username}.
        
        Generate a concise, professional daily briefing. Include the following sections using markdown headings:
        - A "Productivity Hack" to help them with their work or daily tasks.
        - A brief, one-sentence "Market Snapshot" about a major (but generic) global economic trend.
        
        Keep the tone sharp and informative.
        """

    try:
        # Send the prompt to the Gemini model
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Detailed Gemini Error: {e}")
        return "Sorry, I'm having trouble connecting to the AI at the moment. Please try again later."
# ----------------------------
# SMART SUGGESTIONS
# ----------------------------
def smart_suggestion(
    usage_counts: Dict[str, int],
    age: int,
    available_apps: List[str],
    streak: Dict[str, int | str] | None = None,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (app_name, reason) or (None, None).
    """
    if not available_apps:
        return None, None

    # 1) Time of day preference
    hour = datetime.now().hour
    tod_pref = []
    if 6 <= hour < 12:
        tod_pref = ["Calendar", "News", "Study", "Notes"]
        tod_label = "morning"
    elif 12 <= hour < 18:
        tod_pref = ["Games", "YouTube", "Camera", "Music"]
        tod_label = "afternoon"
    else:
        tod_pref = ["Relaxation", "Sleep", "Books", "Music", "Notes"]
        tod_label = "evening"

    # 2) Most-used app
    most_used = None
    if usage_counts:
        filtered = {k: v for k, v in usage_counts.items() if k in available_apps}
        if filtered:
            most_used = max(filtered, key=filtered.get)

    # 3) Streak boost
    streak_app, streak_len = None, 0
    if streak:
        streak_app = streak.get("app")
        streak_len = int(streak.get("len", 0))

    # Build priority
    priority = []
    priority += [a for a in tod_pref if a in available_apps]
    if streak_app and streak_len >= 2 and streak_app in available_apps:
        priority.insert(0, streak_app)
    if most_used and most_used not in priority:
        priority.append(most_used)
    for a in available_apps:
        if a not in priority:
            priority.append(a)

    if not priority:
        return None, None

    chosen = priority[0]
    if chosen == streak_app and streak_len >= 2:
        reason = f"keep your streak going ({streak_len}×)!"
    elif chosen in tod_pref:
        reason = f"great for the {tod_label}"
    elif chosen == most_used:
        reason = "you use this most"
    else:
        reason = "recommended for you"

    return chosen, reason