# app.py
import streamlit as st
import os
import io
from PIL import Image
from core import profile_manager
from core.biometric_auth import get_image_hash, compare_hashes

# -------------------------
# Streamlit Page Settings
# -------------------------
st.set_page_config(page_title="AI OS", page_icon="📱", layout="centered")

ASSETS_DIR = "assets"
USER_IMAGES_DIR = os.path.join(ASSETS_DIR, "user_images")
REGISTERED_IMAGE_NAME = "registered_face.png"
SIMILARITY_THRESHOLD = 10  # Lower = stricter matching

# -------------------------
# Helpers
# -------------------------
def get_registered_users():
    if not os.path.exists(USER_IMAGES_DIR):
        os.makedirs(USER_IMAGES_DIR)
    return sorted(os.listdir(USER_IMAGES_DIR))

def navigate_to_dashboard(profile):
    st.session_state["user_profile"] = profile
    st.switch_page("pages/1_Dashboard.py")

# -------------------------
# Styling
# -------------------------
st.markdown(
    """
    <style>
    body { font-family: 'Segoe UI', sans-serif; }
    .stApp { background-color: #F0F2F6; }
    .main .block-container { max-width: 420px; padding: 1rem; }
    .card { background-color: white; border-radius: 12px; padding: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.08); margin-bottom: 1rem; }
    h1 { text-align: center; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Main UI
# -------------------------
st.title("📱 AI Dual-Space OS")
st.caption("Secure. Personalized. Always with you.")

registered_users = get_registered_users()
tab1, tab2 = st.tabs(["🔐 Login", "👤 Register"])

# -------------------------
# Login Tab
# -------------------------
with tab1:
    if registered_users:
        st.subheader("Welcome Back 👋")
        selected_user = st.selectbox("Choose your profile", registered_users)

        login_image_bytes = st.camera_input("Look into the camera to unlock", label_visibility="collapsed")

        if st.button("✨ Unlock with Face", use_container_width=True):
            if login_image_bytes:
                registered_image_path = os.path.join(USER_IMAGES_DIR, selected_user, REGISTERED_IMAGE_NAME)
                if os.path.exists(registered_image_path):
                    login_hash = get_image_hash(login_image_bytes.getvalue())
                    with open(registered_image_path, "rb") as f:
                        registered_hash = get_image_hash(f.read())

                    distance = compare_hashes(login_hash, registered_hash)
                    if distance != -1 and distance <= SIMILARITY_THRESHOLD:
                        st.success(f"✅ Welcome, {selected_user}!")
                        profile = profile_manager.get_user_profile(selected_user)
                        if profile:
                            navigate_to_dashboard(profile)
                    else:
                        st.error("😕 Face not recognized. Try PIN instead.")
                        st.session_state["show_pin_login"] = True
                else:
                    st.error("⚠️ No registered face found.")
            else:
                st.warning("📸 Please capture your face before unlocking.")

        # PIN Fallback
        if st.session_state.get("show_pin_login", False) and selected_user:
            pin_input = st.text_input("Enter your 4-digit PIN", type="password")
            if st.button("🔑 Unlock with PIN", use_container_width=True):
                if profile_manager.verify_user_pin(selected_user, pin_input):
                    st.success("✅ PIN correct!")
                    profile = profile_manager.get_user_profile(selected_user)
                    if profile:
                        navigate_to_dashboard(profile)
                else:
                    st.error("❌ Incorrect PIN. Try again.")

    else:
        st.info("No registered users yet. Head to **Register** tab.")

    st.markdown("---")
    if st.button("🌐 Enter Guest Mode", use_container_width=True):
        guest_profile = {"username": "Guest", "age": 25, "guest_mode": True}
        st.info("👤 Guest Mode activated — limited features enabled.")
        navigate_to_dashboard(guest_profile)

# -------------------------
# Registration Tab
# -------------------------
with tab2:
    st.subheader("Create a New Profile ✨")
    with st.form("registration_form"):
        new_username = st.text_input("Username").strip()
        age = st.number_input("Your Age", min_value=1, max_value=120, step=1)
        pin = st.text_input("Set a 4-digit PIN", max_chars=4, type="password")
        register_image_bytes = st.camera_input("Take a profile picture")

        submitted = st.form_submit_button("🚀 Create Profile", use_container_width=True)
        if submitted:
            if not all([new_username, age, pin, register_image_bytes]):
                st.error("⚠️ Please fill all fields and take a picture.")
            elif len(pin) != 4 or not pin.isdigit():
                st.error("🔑 PIN must be 4 digits (numbers only).")
            else:
                success, message = profile_manager.create_user_profile(new_username, age, pin)
                if success:
                    user_dir = os.path.join(USER_IMAGES_DIR, new_username)
                    os.makedirs(user_dir, exist_ok=True)
                    img = Image.open(io.BytesIO(register_image_bytes.getvalue()))
                    img.save(os.path.join(user_dir, REGISTERED_IMAGE_NAME))
                    st.success("🎉 Profile created! You can now login.")
                else:
                    st.error(f"❌ Failed: {message}")
