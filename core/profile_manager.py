# core/profile_manager.py

import json
import os
import hashlib
from datetime import datetime

ASSETS_DIR = "assets"
PROFILES_DIR = os.path.join(ASSETS_DIR, "user_profiles")
os.makedirs(PROFILES_DIR, exist_ok=True)

def _hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def ensure_profile_defaults(profile: dict) -> dict:
    """Ensure a profile has all the necessary default fields."""
    profile.setdefault("usage_counts", {})
    profile.setdefault("last_opened_app", None)
    profile.setdefault("streak", {"app": None, "len": 0})
    profile.setdefault("wallpaper", None)
    profile.setdefault("reminders", [])
    return profile

def create_user_profile(username, age, pin):
    profile_path = os.path.join(PROFILES_DIR, f"{username}.json")
    if os.path.exists(profile_path):
        return False, "Username already exists."
    
    # Use the consistent key "usage_counts" from the start
    user_data = {
        "username": username,
        "age": age,
        "pin_hash": _hash_pin(pin)
    }
    user_data = ensure_profile_defaults(user_data) # Add all default fields
    
    with open(profile_path, 'w') as f:
        json.dump(user_data, f, indent=4)
    return True, "User created successfully."

def get_user_profile(username):
    profile_path = os.path.join(PROFILES_DIR, f"{username}.json")
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as f:
            # Ensure any loaded profile is also checked for default fields
            return ensure_profile_defaults(json.load(f))
    return None

def verify_user_pin(username, pin):
    profile = get_user_profile(username)
    if profile and 'pin_hash' in profile:
        return _hash_pin(pin) == profile['pin_hash']
    return False

def update_user_profile(username, profile_data):
    if profile_data.get("guest_mode"):
        return
    profile_path = os.path.join(PROFILES_DIR, f"{username}.json")
    with open(profile_path, 'w') as f:
        json.dump(profile_data, f, indent=4)

def get_all_profiles():
    profiles = []
    for filename in os.listdir(PROFILES_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(PROFILES_DIR, filename), 'r') as f:
                profiles.append(json.load(f))
    return profiles

def record_app_open(username: str, app_name: str) -> dict:
    profile = get_user_profile(username)
    if not profile:
        return {}
    
    usage = profile.get("usage_counts", {})
    usage[app_name] = usage.get(app_name, 0) + 1
    profile["usage_counts"] = usage

    prev = profile.get("last_opened_app")
    if prev == app_name:
        profile["streak"]["app"] = app_name
        profile["streak"]["len"] = int(profile["streak"].get("len", 0)) + 1
    else:
        profile["streak"]["app"] = app_name
        profile["streak"]["len"] = 1

    profile["last_opened_app"] = app_name

    update_user_profile(username, profile)
    return profile

def add_reminder(username: str, text: str, due_iso: str | None):
    profile = get_user_profile(username) or {"username": username}
    profile = ensure_profile_defaults(profile)
    reminders = profile.get("reminders", [])
    reminders.append({"text": text, "due": due_iso, "created_at": datetime.now().isoformat()})
    profile["reminders"] = reminders
    update_user_profile(username, profile)
    return profile

def list_reminders(username: str):
    profile = get_user_profile(username) or {"username": username}
    profile = ensure_profile_defaults(profile)
    return profile.get("reminders", [])