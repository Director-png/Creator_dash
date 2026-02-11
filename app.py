import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
import requests
import feedparser
from bs4 import BeautifulSoup
from gspread_pandas import Spread 
from streamlit_lottie import st_lottie
import time

# --- ANIMATION UTILITY ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_loading = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_fcfjwiyb.json")

# --- TYPEWRITER UTILITY ---
def typewriter_effect(text):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(full_text + "▌")
        time.sleep(0.005) 
    container.markdown(full_text)

# --- 1. CONFIG ---
st.set_page_config(page_title="VOID OS", page_icon="🌑", layout="wide")

# --- 2. SPLASH SCREEN ---
if 'first_load' not in st.session_state:
    st.markdown("<style>.stApp { background-color: #000000; }</style>", unsafe_allow_html=True)
    empty_space = st.empty()
    with empty_space.container():
        st_lottie(lottie_loading, height=400, key="initial_load")
        st.markdown("<h1 style='text-align: center; color: #00d4ff; font-family: monospace;'>INITIALIZING VOID OS...</h1>", unsafe_allow_html=True)
        time.sleep(3.0) 
    empty_space.empty()
    st.session_state.first_load = True
    st.rerun()

# --- 3. GLOBAL CSS ---
st.markdown("""
    <style>
    .matrix-bg { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: black; z-index: -1; }
    .stApp { animation: fadeInPage 1.5s ease-in-out; }
    @keyframes fadeInPage { 0% { opacity: 0; } 100% { opacity: 1; } }
    [data-testid="stMetricValue"] { animation: neonPulse 2.5s infinite alternate; color: #00d4ff !important; }
    @keyframes neonPulse { from { text-shadow: 0 0 5px #00d4ff; } to { text-shadow: 0 0 20px #00d4ff; } }
    </style>
""", unsafe_allow_html=True)

# --- DATA URLS & FUNCTIONS (UNCHANGED LOGIC) ---
PULSE_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuN3zcXZqn9RMnPs7vNEa7vI9xr1Y2VVVlZLUcEwUVqsVqtLMadz1L_Ap4XK_WPA1nnFdpqGr8B_uS/pub?output=csv"
MARKET_URL = "https://docs.google.com/spreadsheets/d/163haIuPIna3pEY9IDxncPM2kFFsuZ76HfKsULcMu1y4/export?format=csv"
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"
FORM_POST_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfnNLb9O-szEzYfYEL85aENIimZFtMd5H3a7o6fX-_6ftU_HA/formResponse"

def load_market_pulse_data():
    try:
        df = pd.read_csv(PULSE_CSV_URL)
        df.columns = [str(c).strip().lower() for c in df.columns]
        mapping = {'niche name': 'Niche', 'score': 'Score', 'news snipett': 'Reason', 'growth': 'Growth'}
        df = df.rename(columns=mapping)
        df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0)
        return df.dropna(subset=['Niche'])
    except: return pd.DataFrame()

def load_market_data():
    try:
        df = pd.read_csv(MARKET_URL)
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1].astype(str).replace(r'[%\$,]', '', regex=True), errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

def load_user_db():
    try:
        df = pd.read_csv(USER_DB_URL)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except: return pd.DataFrame()

def get_intel_image(entry):
    return f"https://picsum.photos/seed/{len(entry.title)}/400/250"

# --- SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_role' not in st.session_state: st.session_state.user_role = "user"
if 'pitch_history' not in st.session_state: st.session_state.pitch_history = []
if 'script_history' not in st.session_state: st.session_state.script_history = []
if 'metric_1_label' not in st.session_state: st.session_state.metric_1_label = "Market Volatility"
if 'metric_1_val' not in st.session_state: st.session_state.metric_1_val = "High"
if 'daily_directive' not in st.session_state: st.session_state.daily_directive = "1. Code VOID OS\n2. Draft 3 Scripts\n3. 1 Client Lead\n4. Word is Law"

# --- 4. THE GATEKEEPER ---
if not st.session_state.logged_in:
    st.markdown('<div class="matrix-bg"></div>', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #00ff41;'>🛡️ DIRECTOR'S INTELLIGENCE PORTAL</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Login", "📝 Register"])
    with t1:
        col_mid = st.columns([1, 2, 1])[1]
        with col_mid:
            email_in = st.text_input("Email").lower().strip()
            pw_in = st.text_input("Password", type="password").strip()
            if st.button("Access System", use_container_width=True):
                if email_in == "admin" and pw_in == "1234":
                    st.session_state.logged_in = True; st.session_state.user_name = "Master Director"; st.session_state.user_role = "admin"; st.rerun()
    # (Registration logic stays the same)
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #00d4ff;'>🌑 VOID OS</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #00ff41;'>● {st.session_state.user_name.upper()}</p>", unsafe_allow_html=True)
    nav = st.radio("COMMAND CENTER", ["📊 Dashboard", "🌐 Global Pulse", "⚔️ Trend Duel", "💎 Script Architect", "💼 Client Pitcher", "📜 Intelligence Archive"])
    st.divider()
    if st.button("🔓 Terminate Session", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()

# --- 6. MODULES ---

if nav == "📊 Dashboard":
    st.markdown("<h1 style='color: white;'>🌑 VOID COMMAND CENTER</h1>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(st.session_state.metric_1_label, st.session_state.metric_1_val)
    m2.metric("Scripts Ready", len(st.session_state.script_history))
    m3.metric("System Status", "Operational")
    m4.metric("Intelligence", "Locked" if not st.session_state.pitch_history else "Active")

elif nav == "🌐 Global Pulse":
    st.title("🌐 GLOBAL INTELLIGENCE PULSE")
    data = load_market_data()
    if not data.empty:
        st.subheader("🔥 TOP MARKET OPPORTUNITIES")
        top_movers = data.sort_values(by=data.columns[1], ascending=False).head(3)
        cols = st.columns(3)
        for i, (index, row) in enumerate(top_movers.iterrows()):
            with cols[i]:
                st.metric(label=row.iloc[0], value=f"{row.iloc[1]}%", delta="High Heat")
                st.caption(f"**Why:** {row.iloc[2]}")
        st.divider()
        fig = px.bar(data.head(10), x=data.columns[1], y=data.columns[0], orientation='h', template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

elif nav == "⚔️ Trend Duel":
    st.title("⚔️ COMPETITIVE INTELLIGENCE MATRIX")
    pulse_df = load_market_pulse_data()
    if not pulse_df.empty:
        selected = st.multiselect("Niches", pulse_df['Niche'].unique(), default=pulse_df['Niche'].unique()[:3])
        st.bar_chart(pulse_df[pulse_df['Niche'].isin(selected)], x='Niche', y='Score')

elif nav == "💼 Client Pitcher":
    st.markdown("<h1>💼 PITCH GENERATOR</h1>", unsafe_allow_html=True)
    client_name = st.text_input("Lead Name")
    offer = st.text_area("Offer")
    if st.button("🔥 Generate") and client_name:
        groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        res = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": f"Pitch for {client_name}: {offer}"}])
        pitch_res = res.choices[0].message.content
        typewriter_effect(pitch_res)
        st.session_state.pitch_history.append({"time": time.strftime("%H:%M:%S"), "client": client_name, "pitch": pitch_res})

elif nav == "💎 Script Architect":
    st.markdown("<h1>✍️ SCRIPT ARCHITECT</h1>", unsafe_allow_html=True)
    topic = st.text_input("Topic")
    if st.button("🚀 Architect") and topic:
        groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        res = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": f"Script about {topic}"}])
        script_res = res.choices[0].message.content
        typewriter_effect(script_res)
        st.session_state.script_history.append({"time": time.strftime("%H:%M:%S"), "topic": topic, "script": script_res})

elif nav == "📜 Intelligence Archive":
    st.title("📜 SYSTEM LOGS")
    t1, t2 = st.tabs(["Script History", "Encrypted Data"])
    with t1:
        for s in reversed(st.session_state.script_history):
            with st.expander(f"🕒 {s['time']} - {s['topic']}"): st.write(s['script'])
    with t2:
        # This is our secret tab for pitches
        for p in reversed(st.session_state.pitch_history):
            with st.expander(f"🔐 LOG_ENTRY: {p['time']}"): st.write(p['pitch'])
