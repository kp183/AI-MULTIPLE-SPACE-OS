# 🚀 AI Dual-Space OS – A Simulated Mobile OS

🔥 **A Smart & Secure AI-Powered Operating System with Biometric Security & Personalization**

---

## 💡 Project Description

**AI Dual-Space OS** is a fully functional prototype of a next-generation mobile operating system, built in **Python + Streamlit**.  
It solves the critical problem of **privacy, security, and personalization on shared family devices** by creating a unique, persistent, and adaptive **digital space** for each user.

This OS simulation offers:

- 🔥 **Persistent Multi-User Spaces** – One device, multiple secure spaces that remember each user's last activity.  
- 🔒 **AI-Powered Biometrics** – Secure login with **face recognition (DeepFace)** and PIN fallback.  
- 🎯 **Age-Adaptive Environments** – UI and available apps change based on the user's age.  
- ⚡ **AI Assistant & Smart Launcher** – Proactively suggests apps and responds to natural commands (voice + text).  
- 📊 **Digital Wellbeing Insights** – Adults can monitor kids’ usage for balance and healthy digital habits.  

---

## 🚀 Key Features

### 🔐 1️⃣ AI Biometric Security
- ✅ **Face Recognition** using `deepface` with deep learning models.  
- 🔢 **PIN Fallback** for backup authentication.  
- 🛡️ **Isolated User Spaces** – Each user has their own sandboxed data.  

### 📱 2️⃣ Persistent & Adaptive Spaces
- 🔁 **Stateful Sessions** – Reopens where the user left off.  
- 🎨 **Age-Based UI** –  
  - **Children** → Creative apps (Notes, Gallery, Games)  
  - **Teens** → Study + fun balance (Notes, Music, Games)  
  - **Adults** → Productivity + monitoring (Reminders, Wellbeing, Notes)  
- 🚀 **Smart Launcher** – Ranks apps based on usage, streaks, and time of day.  

### 🤖 3️⃣ AI Assistant & Wellbeing
- 🗣️ **Voice + Text Assistant** (SpeechRecognition + pyttsx3).  
- 🔊 **Text-to-Speech Replies** – The assistant talks back.  
- ⏰ **Reminders** – Add, list, and track tasks with natural language.  
- 📊 **Digital Wellbeing** – Adults can view children’s app usage charts.  
- 🕵️ **Guest Mode** – Temporary session with **no data saved**.  

---

## 🖼️ Screenshots (Demo Flow)

- 🔐 **Login Screen (Face + PIN)**  
- 📲 **Dashboard with Smart Launcher**  
- 🧠 **AI Feed with personalized nudges**  
- 🎙️ **Assistant handling voice/text commands**  
- 📊 **Digital Wellbeing for parents**  

---

## 💻 Tech Stack

- **Core Language:** Python  
- **UI Framework:** Streamlit  

**AI & Machine Learning**
- Biometrics: DeepFace, TensorFlow, Keras  
- Speech-to-Text: SpeechRecognition (Google API)  

**Voice & Audio**
- Text-to-Speech: pyttsx3  
- Mic Recorder: `streamlit_mic_recorder`  
- Audio Processing: PyAudio, pydub  

**Data & Visualization**
- Pandas, NumPy, Matplotlib/Streamlit Charts  

**Other**
- Pillow, OpenCV  

---

## 🛠️ Installation & Usage

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/kp183/AI-MULTIPLE-SPACE-OS.git
cd AI-MULTIPLE-SPACE-OS
2️⃣ Create Virtual Environment
bash
Copy code
python -m venv venv
# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
3️⃣ Install Dependencies
bash
Copy code
pip install -r requirements.txt
4️⃣ Run the Application
bash
Copy code
streamlit run app.py
🎯 Demo Highlights
Child logs in → sees kid-safe apps.

Teen logs in → gets extra apps + streak tracking.

Adult logs in → has Reminders & Digital Wellbeing dashboard.

Assistant responds to “Open Notes”, “Remind me…”, or “Tell me a joke”.

AI Feed shows personalized cards (reminders, streaks, nudges).

🔮 Future Improvements
📱 Mobile-first UI version

🔔 Push Notifications for reminders

🌐 Cloud sync of user profiles

🧠 More advanced AI personalization

## 👨‍💻 Authors

- **Kunal** – Lead Developer, System Architecture, Core Features (Multi-User Spaces, Biometrics, Smart Launcher, AI Feed, Age-Adaptive Apps, etc.)
- **Krishna** – Co-Developer, Voice Assistant Integration, AI Assistant Features, and Idea Co-Creation

💡 The idea and project were envisioned and built together by **Kunal & Krishna**.
