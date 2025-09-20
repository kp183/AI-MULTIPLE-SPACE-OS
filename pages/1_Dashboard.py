# pages/1_Dashboard.py
import streamlit as st
from datetime import datetime
import pandas as pd
import speech_recognition as sr
import pyttsx3
import io
from pydub import AudioSegment
from streamlit_mic_recorder import mic_recorder

from core.ai_feed import generate_feed_cards
from core.profile_manager import (
    ensure_profile_defaults,
    record_app_open,
    update_user_profile,
    get_all_profiles,
    get_user_profile,    
    list_reminders,
)
from core.assistant import parse_intent, handle_intent

# --- Page Config ---
st.set_page_config(page_title="Dashboard", page_icon="📱", layout="centered")

# --- Auth Check ---
if "user_profile" not in st.session_state:
    st.error("🔒 You must log in first.")
    if st.button("Go to Login Page"):
        st.switch_page("app.py")
    st.stop()

# --- Profile State ---
profile = ensure_profile_defaults(st.session_state["user_profile"])
username = profile.get("username", "User")
age = int(profile.get("age", 18))

if not profile.get("guest_mode"):
    update_user_profile(username, profile)

if f"{username}_state" not in st.session_state:
    st.session_state[f"{username}_state"] = {"active_app": None, "notes_content": "Type your notes here..."}

if f"{username}_assistant" not in st.session_state:
    st.session_state[f"{username}_assistant"] = []

if "tts_engine" not in st.session_state:
    try:
        st.session_state.tts_engine = pyttsx3.init()
        st.session_state.tts_engine.setProperty("rate", 160)
    except Exception as e:
        st.session_state.tts_engine = None
        print(f"Failed to initialize TTS engine: {e}")

# --- Safe TTS ---
def speak_text(engine, text):
    if engine is None:
        st.warning("🔇 Text-to-speech engine not available.")
        return None
    try:
        engine.stop()
        engine.say(text)
        engine.runAndWait()
        return engine
    except Exception:
        st.warning("🔇 Voice busy. Reply shown as text only.")
        return engine

# --- App Renderers ---
def render_text_based_app(title, placeholder):
    st.subheader(title)
    st.session_state[f"{username}_state"]["notes_content"] = st.text_area(
        placeholder,
        value=st.session_state[f"{username}_state"]["notes_content"],
        height=300,
        label_visibility="collapsed",
    )

def render_gallery_based_app(title):
    st.subheader(title)
    cols = st.columns(2)
    cols[0].image("https://images.unsplash.com/photo-1516238840988-66a87c12de08?w=300", use_container_width=True, caption="Summer Vacation")
    cols[1].image("https://images.unsplash.com/photo-1549463519-5a1affd66c24?w=300", use_container_width=True, caption="Friends")

# --- Navigation Logic ---
def open_app(app_name: str):
    if not profile.get("guest_mode"):
        updated_profile = record_app_open(username, app_name)
        st.session_state["user_profile"] = updated_profile
    
    st.session_state[f"{username}_state"]["active_app"] = app_name
    st.rerun()

def close_app():
    if not profile.get("guest_mode"):
        update_user_profile(username, profile)
    st.session_state[f"{username}_state"]["active_app"] = None
    st.rerun()

# --- Age-based Apps ---
def get_available_apps(age: int):
    if age < 13:
        return [("Creative Canvas", "🎨"), ("Learning Zone", "🧠"), ("Story Time", "🎬"), ("Photo Album", "🖼️"), ("My Notes", "📝")]
    elif age < 18:
        return [("Social Hub", "💬"), ("Study Planner", "📚"), ("Music Stream", "🎧"), ("Photo Booth", "📸"), ("Web Browser", "🌐")]
    else:
        # CORRECTED NAME to match the check below
        return [("Workspace", "💼"), ("Mail", "📧"), ("Calendar", "📅"), ("Finance Tracker", "🏦"), ("Wellbeing", "📊")]

apps_to_display = get_available_apps(age)

# --- CSS Styling ---
st.markdown(
    """
    <style>
    body { font-family: 'Segoe UI', sans-serif; }
    .stApp { background-color: #F0F2F6; }
    .main .block-container { max-width: 440px; padding: 1rem; }
    .card { background-color: white; border-radius: 12px; padding: 18px; box-shadow: 0 4px 8px rgba(0,0,0,0.06); margin-bottom: 1rem; }
    .app-icon button { background-color: #E8F0FE; color: #1967D2; border-radius: 14px; height: 90px; width: 100%; font-size: 14px; font-weight: 500; border: none; transition: all 0.2s ease-in-out; }
    .app-icon button:hover { background-color: #D2E3FC; transform: scale(1.05); }
    .assistant-bubble { padding:10px 14px; border-radius:10px; background:#f7f9ff; border:1px solid #e1e7ff; margin:6px 0; }
    .badge { display:inline-block; padding:4px 10px; border-radius:8px; background:#e8f0fe; color:#1967D2; font-size:13px; font-weight:500; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar ---
st.sidebar.header(f"👋 Hi, {username}")
st.sidebar.write(f"Age: {age}")
if profile.get("guest_mode"):
    st.sidebar.warning("Guest Mode 🟡 – data won't be saved.")

st.session_state["enable_tts"] = st.sidebar.checkbox("🔊 Voice Replies", value=True)

if st.sidebar.button("🚪 Logout"):
    if not profile.get("guest_mode"):
        update_user_profile(username, profile)
    st.session_state.clear()
    st.switch_page("app.py")

# --- Main ---
active_app = st.session_state[f"{username}_state"]["active_app"]

if active_app:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if st.button("‹ Back"):
        close_app()
    
    # App Routing
    if active_app in ["Workspace", "Study Planner", "My Notes"]:
        render_text_based_app(f"{'💼' if active_app=='Workspace' else '📚' if active_app=='Study Planner' else '📝'} {active_app}", "Jot down your thoughts...")
    elif active_app in ["Photo Album", "Photo Booth"]:
        render_gallery_based_app(f"{'🖼️'} {active_app}")
    else:
        st.info(f"You opened the '{active_app}' app. Its unique interface would be built here.")

    st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- Home Screen ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    hour = datetime.now().hour
    greet = "morning" if 5 <= hour < 12 else "afternoon" if hour < 18 else "evening"
    st.subheader(f"Good {greet}, {username}!")
    st.caption(datetime.now().strftime("%A, %B %d"))
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Smart Launcher ---
    st.markdown("<h5>📲 Smart Launcher</h5>", unsafe_allow_html=True)
    usage_counts = profile.get("usage_counts", {})
    streaks = profile.get("streak", {})

    def app_priority(app_name):
        score = usage_counts.get(app_name, 0)
        if streaks.get("app") == app_name and streaks.get("len", 0) > 1:
            score += streaks["len"] * 2
        
        # Check against new app names
        if 6 <= hour < 12 and app_name in ["Workspace", "Study Planner", "My Notes"]:
            score += 5
        elif 18 <= hour < 23 and app_name in ["Creative Canvas", "Learning Zone", "Games"]:
            score += 5
        return score

    sorted_apps = sorted(apps_to_display, key=lambda x: app_priority(x[0]), reverse=True)
    if sorted_apps:
        top_app = sorted_apps[0][0]
        st.markdown(f"<span class='badge'>✨ Suggested: {top_app}</span>", unsafe_allow_html=True)

    cols = st.columns(len(sorted_apps) if len(sorted_apps) <= 3 else 3)
    for i, (app_name, app_icon) in enumerate(sorted_apps):
        with cols[i % 3]:
            st.markdown('<div class="app-icon">', unsafe_allow_html=True)
            if st.button(f"{app_icon}\n{app_name}", key=f"smart_{app_name}"):
                open_app(app_name)
            st.markdown("</div>", unsafe_allow_html=True)

    # --- All Apps ---
    st.markdown("<h5>All Apps</h5>", unsafe_allow_html=True)
    cols = st.columns(len(apps_to_display) if len(apps_to_display) <= 3 else 3)
    for i, (app_name, app_icon) in enumerate(apps_to_display):
        with cols[i % 3]:
            st.markdown('<div class="app-icon">', unsafe_allow_html=True)
            if st.button(f"{app_icon}\n{app_name}", key=f"static_{app_name}"):
                open_app(app_name)
            st.markdown("</div>", unsafe_allow_html=True)

    # --- Reminders ---
    if not profile.get("guest_mode") and any(app[0] == "Reminders" for app in apps_to_display):
        user_reminders = list_reminders(username)
        if user_reminders:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("⏰ Reminders")
            df_r = pd.DataFrame(user_reminders).fillna("soon")
            st.table(df_r.head(5))
            st.markdown("</div>", unsafe_allow_html=True)

    # --- AI Feed ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🧠 AI Feed")
    feed_cards = generate_feed_cards(profile)
    if not feed_cards:
        st.info("No insights yet. Open some apps!")
    else:
        for card in feed_cards:
            st.markdown(f"""
                <div style="border-radius:12px;padding:12px;margin:10px 0;
                background:white;border:1px solid rgba(0,0,0,.05);
                box-shadow: 0 2px 6px rgba(0,0,0,.04);">
                {card.get('icon','📌')} <b>{card.get('title','')}</b><br>
                <span style="opacity:.9">{card.get('body','')}</span>
                </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Digital Wellbeing ---
    if age >= 18 and not profile.get("guest_mode") and any(app[0] == "Wellbeing" for app in apps_to_display):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 Digital Wellbeing")
        child_profiles = [p for p in get_all_profiles() if p.get("age", 18) < 18]

        if not child_profiles:
            st.info("No child profiles linked.")
        else:
            for child in child_profiles:
                child_data = get_user_profile(child["username"]) or child
                with st.expander(f"{child_data['username']}'s Usage"):
                    usage_data = child_data.get("usage_counts", {})
                    if not usage_data:
                        st.write("No usage data.")
                    else:
                        df = pd.DataFrame(list(usage_data.items()), columns=["App", "Clicks"])
                        st.bar_chart(df.set_index("App"))
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Assistant ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Assistant 🎙️")
    
    for msg in st.session_state[f"{username}_assistant"]:
        role = "You" if msg["role"] == "user" else "Assistant"
        st.markdown(f'<div class="assistant-bubble"><b>{role}:</b> {msg["text"]}</div>', unsafe_allow_html=True)
    
    voice_cmd = None
    audio = mic_recorder(start_prompt="Speak", stop_prompt="⏹ Stop", key="voice_input")
    if audio and "bytes" in audio:
        try:
            sound = AudioSegment.from_file(io.BytesIO(audio["bytes"]))
            wav_io = io.BytesIO(); sound.export(wav_io, format="wav"); wav_io.seek(0)
            r = sr.Recognizer();
            with sr.AudioFile(wav_io) as source: audio_data = r.record(source)
            voice_cmd = r.recognize_google(audio_data)
        except Exception as e:
            st.error(f"🎤 Error: {e}")
    
    user_input = None
    if voice_cmd: user_input = voice_cmd

    with st.form("assistant_form", clear_on_submit=True):
        text_cmd = st.text_input("Type a command...", "")
        submitted = st.form_submit_button("Send")
        if submitted and text_cmd.strip(): user_input = text_cmd

    if user_input:
        st.session_state[f"{username}_assistant"].append({"role": "user", "text": user_input})
        intent = parse_intent(user_input, [name for name, _ in apps_to_display])
        reply, app_to_open = handle_intent(username, [name for name, _ in apps_to_display], intent, user_input)
        
        st.session_state[f"{username}_assistant"].append({"role": "assistant", "text": reply})
        if st.session_state.get("enable_tts", True):
            st.session_state.tts_engine = speak_text(st.session_state.tts_engine, reply)
        
        if app_to_open: open_app(app_to_open)
        else: st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)