import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
import requests
import feedparser
from bs4 import BeautifulSoup
import time
from streamlit_lottie import st_lottie

# --- 1. CONFIG & UTILS ---
st.set_page_config(page_title="VOID OS", page_icon="🌑", layout="wide")

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

def typewriter_effect(text):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(full_text + "▌")
        time.sleep(0.005) 
    container.markdown(full_text)

def analyze_trend_saturation(score):
    if score > 85: return "🔴 SATURATED"
    if score > 65: return "🟡 PEAK"
    return "🟢 EARLY"

def generate_visual_dna(topic, tone):
    return f"Cinematic, high-fidelity, {tone} aesthetic, 8k resolution, concept art for: {topic}"

# --- 2. DATA SOURCE SETTINGS ---
PULSE_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuN3zcXZqn9RMnPs7vNEa7vI9xr1Y2VVVlZLUcEwUVqsVqtLMadz1L_Ap4XK_WPA1nnFdpqGr8B_uS/pub?output=csv"
MARKET_URL = "https://docs.google.com/spreadsheets/d/163haIuPIna3pEY9IDxncPM2kFFsuZ76HfKsULcMu1y4/export?format=csv"
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"

# --- 3. CORE LOADING FUNCTIONS ---
def load_market_pulse_data():
    try:
        df = pd.read_csv(PULSE_CSV_URL)
        df.columns = [str(c).strip().lower() for c in df.columns]
        mapping = {'niche name': 'Niche', 'score': 'Score', 'news snipett': 'Reason'}
        df = df.rename(columns=mapping)
        df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0)
        return df.dropna(subset=['Niche'])
    except: return pd.DataFrame()

def load_market_data():
    try:
        df = pd.read_csv(MARKET_URL)
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        return df
    except: return pd.DataFrame()

def load_user_db():
    try:
        df = pd.read_csv(USER_DB_URL)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except: return pd.DataFrame()

def get_intel_image(entry):
    try:
        soup = BeautifulSoup(entry.summary, 'html.parser')
        img = soup.find('img')
        if img: return img['src']
    except: pass
    return f"https://picsum.photos/seed/{len(entry.title)}/400/250"

# --- 4. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = "user"
if 'script_history' not in st.session_state: st.session_state.script_history = []
if 'pitch_history' not in st.session_state: st.session_state.pitch_history = []

# --- 5. GATEKEEPER (LOGIN) ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #00ff41;'>🛡️ DIRECTOR'S INTELLIGENCE PORTAL</h1>", unsafe_allow_html=True)
    email_in = st.text_input("Email")
    pw_in = st.text_input("Password", type="password")
    if st.button("Access"):
        if email_in == "admin" and pw_in == "1234":
            st.session_state.logged_in = True
            st.session_state.user_role = "admin"
            st.session_state.user_name = "Master Director"
            st.rerun()
    st.stop()

# --- 6. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🌑 VOID OS")
    if st.session_state.user_role == "admin":
        options = ["📊 Dashboard", "🌐 Global Pulse", "⚔️ Trend Duel", "💎 Script Architect", "💼 Client Pitcher", "📜 History"]
    else:
        options = ["🌐 Global Pulse", "⚔️ Trend Duel", "💎 Script Architect", "📜 History"]
    nav = st.radio("COMMAND", options)

# --- 7. MODULES ---

if nav == "📊 Dashboard" and st.session_state.user_role == "admin":
    st.header("🌑 DIRECTOR COMMAND CENTER")
    m1, m2, m3 = st.columns(3)
    m1.metric("System Status", "Operational")
    m2.metric("Intelligence Depth", "High")
    m3.metric("Archive Size", len(st.session_state.script_history))
    
    # NEW: WEEKLY ORACLE REPORT
    st.subheader("🔮 Weekly Oracle Report")
    if st.button("Generate Trend Forecast PDF"):
        st.download_button("Download Report.txt", "VOID OS WEEKLY TREND ANALYSIS\nPrediction: AI-Agentic workflows will spike next week.", "report.txt")

elif nav == "🌐 Global Pulse":
    st.title("🌐 GLOBAL INTELLIGENCE PULSE")
    
    # PULSE ALERT SYSTEM
    pulse_df = load_market_pulse_data()
    if not pulse_df.empty:
        high_heat = pulse_df[pulse_df['Score'] >= 85]
        if not high_heat.empty:
            for _, alert in high_heat.iterrows():
                st.error(f"🚨 **VIGOROUS TREND**: {alert['Niche']} is spiking! (Score: {alert['Score']})")

    # LIVE NEWS
    feed = feedparser.parse("https://techcrunch.com/category/artificial-intelligence/feed/")
    for entry in feed.entries[:5]:
        c1, c2 = st.columns([1, 3])
        with c1: st.image(get_intel_image(entry))
        with c2: st.markdown(f"**[{entry.title}]({entry.link})**\n\n{BeautifulSoup(entry.summary, 'html.parser').text[:150]}...")
        st.divider()

elif nav == "⚔️ Trend Duel":
    st.title("⚔️ TREND ANALYSIS & SATURATION")
    pulse_df = load_market_pulse_data()
    if not pulse_df.empty:
        selected = st.selectbox("Select Niche", pulse_df['Niche'].unique())
        niche_score = pulse_df[pulse_df['Niche'] == selected]['Score'].values[0]
        st.metric("Saturation Status", analyze_trend_saturation(niche_score))
        st.bar_chart(pulse_df.set_index('Niche')['Score'])

elif nav == "💎 Script Architect":
    st.title("✍️ SCRIPT ARCHITECT & DNA")
    topic = st.text_input("Focus Topic")
    tone = st.select_slider("Tone", ["Professional", "Aggressive", "Storyteller"])
    comp_shadow = st.text_input("Competitor Focus (Optional)")
    
    if st.button("Architect"):
        with st.spinner("Processing..."):
            groq_c = Groq(api_key=st.secrets["GROQ_API_KEY"])
            prompt = f"Topic: {topic}, Tone: {tone}. Counter competitor: {comp_shadow}"
            res = groq_c.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            txt = res.choices[0].message.content
            dna = generate_visual_dna(topic, tone)
            st.session_state.script_history.append({"time": time.strftime("%H:%M:%S"), "topic": topic, "script": txt, "dna": dna})
            typewriter_effect(txt)
            st.info(f"🧬 **CONTENT DNA:** {dna}")

elif nav == "💼 Client Pitcher" and st.session_state.user_role == "admin":
    st.title("💼 CLIENT PITCHER")
    elif nav == "💼 Client Pitcher" and st.session_state.user_role == "admin":
    st.markdown("<h1 style='color: #00d4ff;'>💼 VOID CAPITAL: PITCH GENERATOR</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1.5])
    with c1:
        client = st.text_input("Lead Name")
        niche_cat = st.selectbox("Category", ["Personal Brand", "B2B Technical", "Fashion", "Hospitality", "Local Business"])
        offer = st.text_area("Value Proposition")
        if st.button("🔥 Generate VOID Pitch"):
            with st.spinner("🌑 ACCESSING VOID COGNITION..."):
                groq_c = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = groq_c.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": f"Pitch for {client} in {niche_cat}: {offer}"}])
                pitch_res = res.choices[0].message.content
                st.session_state.pitch_history.append({"time": time.strftime("%H:%M:%S"), "client": client, "pitch": pitch_res})
                with c2: typewriter_effect(pitch_res)# Pitcher logic here...

elif nav == "📜 History":
    st.title("📜 ARCHIVES")
    if st.button("🔥 PURGE LOGS"):
        st.session_state.script_history = []
        st.rerun()
    for s in reversed(st.session_state.script_history):
        with st.expander(f"{s['time']} - {s['topic']}"):
            st.write(s['script'])
            st.caption(f"DNA: {s.get('dna', 'N/A')}")
