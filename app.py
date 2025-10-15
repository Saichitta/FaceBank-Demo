# app.py
import os
import json
import time
from datetime import datetime
import streamlit as st

# -------------------- ENV / API KEYS --------------------
# from dotenv import load_dotenv
# load_dotenv()  # Load local .env if present

# Groq SDK
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except Exception:
    GROQ_AVAILABLE = False

# Speech libraries
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except Exception:
    SR_AVAILABLE = False

# Streamlit audiorecorder component (browser mic)
try:
    from audiorecorder import audiorecorder
    AUDIOREC_AVAILABLE = True
except Exception:
    AUDIOREC_AVAILABLE = False

# -------------------- CONFIG --------------------
st.set_page_config(page_title="FaceBank - Agentic AI Assistant", page_icon="🏦", layout="centered")

# -------------------- DATA --------------------
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
FD_FILE = os.path.join(DATA_DIR, "fd_plans.json")

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

users = load_json(USERS_FILE)
fd_plans = load_json(FD_FILE)

def get_user():
    return users[0]

# -------------------- SESSION STATE --------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'user_data' not in st.session_state:
    st.session_state.user_data = get_user().copy()

# -------------------- GROQ CLIENT --------------------
GROQ_API_KEY = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else None

if GROQ_AVAILABLE and GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        groq_ready = True
    except Exception as e:
        st.error(f"Groq initialization failed: {e}")
        groq_ready = False
else:
    groq_ready = False

# -------------------- AGENT LOGIC --------------------
def local_agent_response(user_input, user_data):
    text = user_input.lower()
    if "balance" in text:
        return f"Your current balance is ₹{int(user_data['balance'])}."
    if "transaction" in text or "history" in text or "last" in text:
        txns = user_data.get("transactions", [])
        reply_lines = [f"{t['date']}: {t['type'].capitalize()} ₹{t['amount']} ({t.get('desc','')})" for t in txns[-3:]]
        return "Here are your recent transactions:\n" + "\n".join(reply_lines) if reply_lines else "No transactions found."
    if "fd" in text or "fixed deposit" in text or "deposit" in text:
        eligible = [fd for fd in fd_plans if user_data['balance'] >= fd['min_amount']]
        if not eligible:
            return "You don't have enough balance for the sample FD plans."
        best = max(eligible, key=lambda x: float(x['rate'].strip('%')))
        return f"I recommend the {best['duration']} FD at {best['rate']}. Min amount ₹{best['min_amount']}."
    if text.startswith("send") or "transfer" in text:
        import re
        m = re.search(r"(\d+)", text.replace(",", ""))
        amt = int(m.group(1)) if m else 100
        st.session_state.user_data['balance'] = max(0, st.session_state.user_data['balance'] - amt)
        tx = {"date": datetime.today().strftime("%Y-%m-%d"), "type": "debit", "amount": amt, "desc": "Demo transfer"}
        st.session_state.user_data.setdefault("transactions", []).append(tx)
        return f"₹{amt} sent successfully. New balance ₹{int(st.session_state.user_data['balance'])}."
    return ("Hello — I'm FaceBank. You can ask me to 'Check my balance', 'Show transactions', "
            "'Suggest FD', or 'Send ₹500 to Ramesh'.")

def groq_agent_response(user_input, user_data):
    if not groq_ready:
        return local_agent_response(user_input, user_data)
    system_msg = {
        "role": "system",
        "content": (
            "You are FaceBank, an AI banking assistant targeting elderly and accessibility users. "
            "Be concise, polite, and always refer to the user's data when appropriate. "
            "If an action like transfer is requested, describe the simulated action and confirm it."
        )
    }
    user_context = {
        "role": "user",
        "content": (
            f"User data: name={user_data.get('name')}, balance={int(user_data.get('balance',0))}, "
            f"transactions={json.dumps(user_data.get('transactions',[]))}, fd_plans={json.dumps(fd_plans)}. "
            f"User asked: {user_input}"
        )
    }
    try:
        model_name = "openai/gpt-oss-20b"  # working free-tier demo model
        resp = groq_client.chat.completions.create(
            model=model_name,
            messages=[system_msg, user_context],
            max_tokens=256,
            temperature=0.2
        )
        return resp.choices[0].message.content
    except Exception as e:
        st.warning(f"Groq API error: {e} — falling back to local agent.")
        return local_agent_response(user_input, user_data)

def get_agent_reply(user_input):
    return groq_agent_response(user_input, st.session_state.user_data) if groq_ready else local_agent_response(user_input, st.session_state.user_data)

# -------------------- SPEECH-TO-TEXT --------------------
def transcribe_uploaded_audio(uploaded_file):
    if not SR_AVAILABLE or uploaded_file is None:
        return ""
    r = sr.Recognizer()
    with open("temp_upload.wav", "wb") as f:
        f.write(uploaded_file.getbuffer())
    try:
        with sr.AudioFile("temp_upload.wav") as source:
            audio = r.record(source)
        return r.recognize_google(audio)
    except Exception as e:
        st.error(f"Failed to transcribe audio: {e}")
        return ""

# -------------------- UI --------------------
st.title("🏦 FaceBank — Agentic AI Banking Assistant")
st.write("Accessible banking for elderly & differently-abled users. (Streamlit demo)")

# -------------------- Face Recognition Login --------------------
if not st.session_state.authenticated:
    st.subheader("👤 Face Recognition Login (demo)")
    st.write("Use your webcam to take a picture. This demo simulates verification.")
    img = st.camera_input("Take a picture to verify")
    if img is not None:
        st.success("✅ Face verified.")
        st.session_state.authenticated = True
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Hello {st.session_state.user_data['name']}! I'm FaceBank. How can I assist you today?",
            "time": time.time()
        })
        st.rerun()


# -------------------- Chat Interface --------------------
else:
    user = st.session_state.user_data
    cols = st.columns([1, 3])
    with cols[0]:
        st.image("assets/logo.png" if os.path.exists("assets/logo.png") else "https://via.placeholder.com/80", width=80)
    with cols[1]:
        st.markdown(f"**{user['name']}**")
        st.caption(f"Balance: ₹{int(user['balance'])}")

    st.markdown("---")
    st.subheader("💬 Conversation")
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            else:
                st.chat_message("assistant").write(msg["content"])

    # -------------------- Chat Input --------------------
    with st.form("input_form", clear_on_submit=False):
        user_text = st.text_input("Type your message here...", key="user_input")
        cols = st.columns([1, 1])
        with cols[0]:
            submit = st.form_submit_button("Send")
        with cols[1]:
            upload_audio = st.file_uploader("Upload audio (.wav/.mp3)", type=["wav","mp3","m4a"])

    # Browser microphone recorder (Streamlit Cloud compatible)
    if AUDIOREC_AVAILABLE:
        audio = audiorecorder("🎤 Start Recording", "⏹ Stop Recording")
        if len(audio) > 0:
            st.audio(audio.tobytes(), format="audio/wav")
            with open("temp_mic.wav", "wb") as f:
                f.write(audio.tobytes())
            with st.spinner("Transcribing..."):
                spoken = transcribe_uploaded_audio(open("temp_mic.wav","rb"))
            if spoken:
                user_text = spoken
                st.success(f"You said: {user_text}")

    # Handle send
    if submit and user_text:
        st.session_state.messages.append({"role": "user", "content": user_text, "time": time.time()})
        with st.spinner("Thinking..."):
            reply = get_agent_reply(user_text)
        st.session_state.messages.append({"role": "assistant", "content": reply, "time": time.time()})
        st.rerun()

    # -------------------- Utilities --------------------
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁 Reset Conversation"):
            st.session_state.messages = []
            st.success("Conversation reset.")
            st.rerun()
    with col2:
        if st.button("💾 Save session to file (download)"):
            export = {"user": st.session_state.user_data, "messages": st.session_state.messages}
            st.download_button("Download JSON", data=json.dumps(export, indent=2), file_name="facebank_session.json", mime="application/json")

st.markdown("---")


