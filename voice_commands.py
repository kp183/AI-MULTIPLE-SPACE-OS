# core/voice_commands.py
import streamlit as st
import speech_recognition as sr

def listen_for_command():
    """
    Listens for a voice command from the user's microphone and returns the text.
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.toast("Listening...", icon="🎤")
        # Adjust for ambient noise to improve accuracy
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=4)
            st.toast("Processing...", icon="⚙️")
            # Use Google's speech recognition to convert audio to text
            command = r.recognize_google(audio).lower()
            st.toast(f"Heard: '{command}'", icon="🗣️")
            return command
        except sr.WaitTimeoutError:
            st.warning("Listening timed out. Please try again.")
            return None
        except sr.UnknownValueError:
            st.warning("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError as e:
            st.error(f"Could not request results from speech recognition service; {e}")
            return None