import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
import requests
import feedparser
from bs4 import BeautifulSoup
from streamlit_lottie import st_lottie
import time

# --- ANIMATION UTILITY ---
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_loading = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_fcfjwiyb.json")

# --- 1. CONFIG & CONNECTIONS ---
st.set_page_config(page_title="VOID OS", page_icon="🌑", layout="wide")

# --- 2. STARTING ANIMATION (SPLASH SCREEN) ---
if 'first_load' not in st.session_state:
    st.markdown("<style>.stApp { background-color: #000000; }</style>", unsafe_allow_html=True)
    empty_space = st.empty()
    with empty_space.container():
        st_lottie(lottie_loading, height=400, key="initial_load")
        st.markdown("<h1 style='text-align: center; color: #00d4ff; font-family: monospace;'>INITIALIZING VOID OS...</h1>", unsafe_allow_html=True)
        time.sleep(2.5)
    empty_space.empty()
    st.session_state.first_load = True
    st.rerun()

# --- 3. GLOBAL CSS & MATRIX ANIMATION ---
st.markdown("""
    <style>
    .matrix-bg {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: black;
        opacity: 0.15;
        z-index: -1;
    }
    .stApp { animation: fadeInPage 1.5s ease-in-out; }
    @keyframes fadeInPage {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    [data-testid="stMetricValue"] {
        animation: neonPulse 2.5s infinite alternate;
        color: #00d4ff !important;
    }
    @keyframes neonPulse {
        from { text-shadow: 0 0 2px #00d4ff; }
        to { text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff; }
    }
    </style>
""", unsafe_allow_html=True)

# --- TYPEWRITER UTILITY ---
def typewriter_effect(text):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(full_text + "▌")
        time.sleep(0.002)
    container.markdown(full_text)

# --- DATA FUNCTIONS ---
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
if 'metric_1_label' not in st.session_state: st.session_state.metric_1_label = "Market Volatility"
if 'metric_1_val' not in st.session_state: st.session_state.metric_1_val = "High"
if 'daily_directive' not in st.session_state: st.session_state.daily_directive = "1. Code VOID OS\n2. Draft 3 Scripts\n3. 1 Client Lead\n4. Word is Law"
if 'pitch_history' not in st.session_state: st.session_state.pitch_history = []
if 'script_history' not in st.session_state: st.session_state.script_history = []

# --- 4. THE GATEKEEPER ---
if not st.session_state.logged_in:
    st.markdown('<div class="matrix-bg"></div>', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #00ff41;'>🛡️ DIRECTOR'S INTELLIGENCE PORTAL</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Login", "📝 Register"])

    with t1:
        col_mid = st.columns([1, 2, 1])[1]
        with col_mid:
            email_in = st.text_input("Email", key="login_email").lower().strip()
            pw_in = st.text_input("Password", type="password", key="login_pw").strip()
            if st.button("Access System", use_container_width=True):
                users = load_user_db()
                if email_in == "admin" and pw_in == "1234":
                    st.session_state.logged_in = True
                    st.session_state.user_name = "Master Director"
                    st.session_state.user_role = "admin"
                    st.rerun()
                elif not users.empty:
                    match = users[(users.iloc[:, 2].astype(str).str.lower() == email_in) & (users.iloc[:, 4].astype(str) == pw_in)]
                    if not match.empty:
                        st.session_state.logged_in = True
                        st.session_state.user_name = match.iloc[0, 1]
                        niche_val = str(match.iloc[0, 3]).lower()
                        st.session_state.user_role = "admin" if any(x in niche_val for x in ["fitness", "admin"]) else "user"
                        st.rerun()
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color: #00d4ff;'>🌑 VOID OS</h1>", unsafe_allow_html=True)
    nav_options = ["📊 Dashboard", "🌐 Global Pulse", "⚔️ Trend Duel", "💎 Script Architect"]
    if st.session_state.user_role == "admin": nav_options.append("💼 Client Pitcher")
    nav = st.radio("COMMAND CENTER", nav_options)
    if st.button("🔓 Terminate Session"):
        st.session_state.logged_in = False
        st.rerun()

# --- 6. MODULES ---
if nav == "📊 Dashboard":
    st.markdown("<h1>🌑 VOID COMMAND CENTER</h1>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(st.session_state.metric_1_label, st.session_state.metric_1_val)
    m2.metric("Scripts Ready", "24", "+6")
    m3.metric("Agency Leads", "3", "Target: 10")
    m4.metric("System Status", "Operational")

    st.subheader("🕵️ ARCHIVED INTELLIGENCE")
    tab_p, tab_s = st.tabs(["Recent Pitches", "Recent Scripts"])
    with tab_p:
        for p in reversed(st.session_state.pitch_history):
            with st.expander(f"🕒 {p['time']} - {p['client']}"): st.write(p['pitch'])
    with tab_s:
        for s in reversed(st.session_state.script_history):
            with st.expander(f"🕒 {s['time']} - {s['topic']}"): st.write(s['script'])

elif nav == "🌐 Global Pulse":
    st.title("🌐 GLOBAL INTELLIGENCE PULSE")
    data = load_market_data()
    if not data.empty:
        chart_data = data.sort_values(by=data.columns[1], ascending=False).head(10)
        fig = px.bar(chart_data, x=chart_data.columns[1], y=chart_data.columns[0], orientation='h', template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

elif nav == "💼 Client Pitcher":
    st.title("💼 VOID CAPITAL: PITCH GENERATOR")
    c1, c2 = st.columns([1, 1.5])
    with c1:
        client_name = st.text_input("Lead Name")
        niche_category = st.selectbox("Category", ["Personal Brand", "B2B Technical", "Fashion", "Hospitality"])
        offer = st.text_area("Value Proposition")
        pitch_btn = st.button("🔥 Generate Pitch", type="primary")

    if pitch_btn and client_name:
        with st.spinner("🌑 ACCESSING VOID COGNITION..."):
            try:
                groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"Write a {niche_category} pitch for {client_name} about {offer}"}]
                )
                pitch_result = res.choices[0].message.content
                with c2:
                    typewriter_effect(pitch_result)
                    st.session_state.pitch_history.append({"time": time.strftime("%H:%M:%S"), "client": client_name, "pitch": pitch_result})
            except Exception as e: st.error(f"Error: {e}")

elif nav == "💎 Script Architect":
    st.title("✍️ VOID SCRIPT ARCHITECT")
    col1, col2 = st.columns([1, 1.5])
    with col1:
        topic_input = st.text_input("Focus Topic")
        generate_btn = st.button("🚀 Architect Script", type="primary")

    if generate_btn and topic_input:
        with st.spinner("🌑 COMPILING SCRIPT..."):
            try:
                groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"Write a script about {topic_input}"}]
                )
                script_result = res.choices[0].message.content
                with col2:
                    typewriter_effect(script_result)
                    st.session_state.script_history.append({"time": time.strftime("%H:%M:%S"), "topic": topic_input, "script": script_result})
            except Exception as e: st.error(f"Error: {e}")
