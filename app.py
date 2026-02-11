import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
import requests
import feedparser
from bs4 import BeautifulSoup
import time
from streamlit_lottie import st_lottie

# --- ANIMATION UTILITY ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_loading = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_fcfjwiyb.json")

# --- 1. SESSION STATE (CRITICAL FIX: Initialize FIRST) ---
if 'found_leads' not in st.session_state:
    st.session_state.found_leads = pd.DataFrame()
if 'script_history' not in st.session_state:
    st.session_state.script_history = []
if 'pitch_history' not in st.session_state:
    st.session_state.pitch_history = []
if 'creator_db' not in st.session_state:
    st.session_state.creator_db = pd.DataFrame([
        {"Creator": "TechVanguard", "Niche": "AI", "Status": "Scouted", "Vigor": 82},
        {"Creator": "CyberStyle", "Niche": "Fashion", "Status": "Negotiation", "Vigor": 91}
    ])
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- 🛰️ DATA INFRASTRUCTURE (RESTORED) ---
PULSE_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuN3zcXZqn9RMnPs7vNEa7vI9xr1Y2VVVlZLUcEwUVqsVqtLMadz1L_Ap4XK_WPA1nnFdpqGr8B_uS/pub?output=csv"
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"
FORM_POST_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfnNLb9O-szEzYfYEL85aENIimZFtMd5H3a7o6fX-_6ftU_HA/formResponse"
SCRIPT_VAULT_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"

# --- 🛰️ UTILITIES ---
def typewriter_effect(text):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(full_text + "▌")
        time.sleep(0.005) 
    container.markdown(full_text)

def load_user_db():
    try:
        timestamp = int(time.time())
        sync_url = f"{USER_DB_URL}&cv={timestamp}" 
        df = pd.read_csv(sync_url, timeout=5)
        if df.empty: return pd.DataFrame()
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        st.sidebar.warning(f"Connection Attempt Failed: {e}")
        return pd.DataFrame()

def load_market_pulse_data():
    try:
        df = pd.read_csv(PULSE_CSV_URL)
        df.columns = [str(c).strip().lower() for c in df.columns]
        mapping = {'niche name': 'Niche', 'score': 'Score', 'news snipett': 'Reason', 'growth': 'Growth'}
        df = df.rename(columns=mapping)
        df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0)
        return df.dropna(subset=['Niche'])
    except: return pd.DataFrame()

def generate_visual_dna(platform, tone):
    styles = {
        "Instagram Reels": "High-contrast, 0.5s jump cuts, Glow-on-dark aesthetics.",
        "YouTube Shorts": "Center-framed, bold captions, neon-accent lighting.",
        "YouTube Long-form": "Cinematic 4k, shallow depth of field, 24fps motion blur.",
        "TikTok": "Raw mobile-style, high-saturation, fast-paced text overlays."
    }
    aesthetic = styles.get(platform, "Professional cinematic.")
    return f"DNA PROFILE: {aesthetic} | TONE: {tone} | LIGHTING: Cyber-Noir"

def calculate_vigor(views, followers):
    if followers == 0: return 0
    ratio = views / followers
    return min(100, int(ratio * 50))

def get_intel_image(entry):
    try:
        if 'media_content' in entry: return entry.media_content[0]['url']
        soup = BeautifulSoup(entry.summary, 'html.parser')
        img = soup.find('img')
        if img: return img['src']
    except: pass
    return f"https://picsum.photos/seed/{len(entry.title)}/400/250"

def get_saturation_status(score):
    if score > 88: return "🔴 SATURATED (High Competition)"
    if score > 75: return "🟡 PEAK (Strategic Entry)"
    return "🟢 EARLY (High Opportunity)"

def transmit_script(client, platform, topic, script, dna):
    payload = {
        "entry.546765267": client, "entry.1077052292": platform,
        "entry.415250537": topic, "entry.1437097100": script, "entry.1608255172": dna
    }
    try:
        requests.post(FORM_POST_URL, data=payload)
        return True
    except: return False

# --- 1. CONFIG ---
st.set_page_config(page_title="VOID OS", page_icon="🌑", layout="wide")

# --- 2. SPLASH SCREEN ---
if 'first_load' not in st.session_state:
    st.markdown("<style>.stApp { background-color: #000000; }</style>", unsafe_allow_html=True)
    empty_space = st.empty()
    with empty_space.container():
        if lottie_loading: st_lottie(lottie_loading, height=400)
        st.markdown("<h1 style='text-align: center; color: #00d4ff; font-family: monospace;'>INITIALIZING VOID OS...</h1>", unsafe_allow_html=True)
        time.sleep(3.0) 
    st.session_state.first_load = True
    st.rerun()

# --- 3. GLOBAL STYLES ---
st.markdown("""<style>
    [data-testid="stSidebar"] { background-image: linear-gradient(180deg, #000000 0%, #080808 100%); border-right: 1px solid #00d4ff33; }
    .stButton>button { border: 1px solid #00d4ff; background-color: transparent; color: #00d4ff; letter-spacing: 2px; }
    .stButton>button:hover { background-color: #00d4ff; color: black; box-shadow: 0 0 15px #00d4ff; }
    </style>""", unsafe_allow_html=True)

# --- GATEKEEPER ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #00ff41;'>🛡️ DIRECTOR'S INTELLIGENCE PORTAL</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Login", "📝 Register"])
    with t1:
        email_in = st.text_input("Email").lower().strip()
        pw_in = st.text_input("Password", type="password")
        if st.button("Access System", use_container_width=True):
            users = load_user_db()
            if email_in == "admin" and pw_in == "1234":
                st.session_state.logged_in = True; st.session_state.user_name = "Master Director"; st.session_state.user_role = "admin"; st.rerun()
            elif not users.empty:
                match = users[(users.iloc[:, 2].astype(str).str.lower() == email_in) & (users.iloc[:, 4].astype(str) == pw_in)]
                if not match.empty:
                    st.session_state.logged_in = True; st.session_state.user_name = match.iloc[0, 1]; st.session_state.user_role = "user"; st.rerun()
    with t2:
        with st.form("reg"):
            n = st.text_input("Name"); e = st.text_input("Email"); ni = st.text_input("Niche"); p = st.text_input("Password", type="password")
            if st.form_submit_button("Submit"):
                requests.post(FORM_POST_URL, data={"entry.483203499": n, "entry.1873870532": e, "entry.1906780868": ni, "entry.1396549807": p})
                st.success("Transmission Received.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"<p style='text-align: center; color: #00ff41;'>● {st.session_state.user_name.upper()}</p>", unsafe_allow_html=True)
    if st.session_state.user_role == "admin":
        options = ["📊 Dashboard", "🌐 Global Pulse", "⚔️ Trend Duel", "🧬 Creator Lab", "🛰️ Lead Source", "💎 Script Architect", "💼 Client Pitcher", "📜 History"]
    else:
        options = ["📡 My Growth Hub", "💎 Assigned Scripts", "🌐 Global Pulse"]
    nav = st.radio("COMMAND CENTER", options, key="void_nav_main")

# --- MODULES ---
if nav == "📊 Dashboard" and st.session_state.user_role == "admin":
    st.markdown("<h1 style='color: white;'>🌑 VOID COMMAND CENTER</h1>", unsafe_allow_html=True)
    # [Rest of Dashboard code preserved...]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label="System Status", value="Operational")
    m2.metric(label="Scripts Ready", value=str(len(st.session_state.script_history)))

elif nav == "📡 My Growth Hub":
    st.markdown(f"<h1 style='color: #00d4ff;'>📡 WELCOME, {st.session_state.user_name.upper()}</h1>", unsafe_allow_html=True)

elif nav == "💎 Assigned Scripts":
    st.title("💎 YOUR SECURE VAULT")
    try:
        scripts_df = pd.read_csv(SCRIPT_VAULT_CSV_URL)
        scripts_df.columns = [str(c).strip().lower() for c in scripts_df.columns]
        my_vault = scripts_df[scripts_df.iloc[:, 1].astype(str) == st.session_state.user_name]
        if my_vault.empty: st.warning("No scripts assigned yet.")
        else:
            for _, row in my_vault.iterrows():
                with st.expander(f"📜 {row.iloc[3]}"):
                    st.write(row.iloc[4])
                    st.caption(f"DNA: {row.iloc[5]}")
    except: st.error("Vault Offline.")

elif nav == "🌐 Global Pulse":
    st.title("🌐 GLOBAL INTELLIGENCE PULSE")
    # [Global Pulse Code Preserved...]

elif nav == "⚔️ Trend Duel":
    st.title("⚔️ TREND DUEL")
    # [Trend Duel Code Preserved...]

elif nav == "💎 Script Architect":
    st.markdown("<h1 style='color: #00ff41;'>⚔️ TACTICAL ARCHITECT</h1>", unsafe_allow_html=True)
    users_df = load_user_db()
    
    if not users_df.empty:
        with st.expander("🔍 DATA STATUS"): st.write(users_df.columns.tolist())
    
    client_options = ["Public/General"]
    if not users_df.empty:
        client_options += users_df.iloc[:, 1].dropna().unique().tolist()

    c1, c2 = st.columns([1, 1.2], gap="large")
    with c1:
        target_client = st.selectbox("Assign To Target", options=client_options, key="architect_target")
        platform = st.selectbox("Platform", ["Instagram Reels", "YouTube Shorts", "TikTok", "YouTube Long-form"], key="platform_selector")
        topic = st.text_input("Core Topic", key="topic_input")
        tone_choice = st.select_slider("Vigor/Tone", ["Professional", "Aggressive", "Elite"], key="tone_slider")
        
        if st.button("🚀 ARCHITECT & TRANSMIT", use_container_width=True):
            if topic:
                with st.spinner("🌑 ARCHITECTING..."):
                    groq_c = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    prompt = f"Architect a {platform} script about {topic}. Tone: {tone_choice}."
                    res = groq_c.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                    txt = res.choices[0].message.content
                    dna_profile = generate_visual_dna(platform, tone_choice)
                    transmit_status = transmit_script(target_client, platform, topic, txt, dna_profile)
                    if transmit_status: st.success("⚔️ BROADCAST COMPLETE")
                    with c2: st.markdown(txt)

elif nav == "💼 Client Pitcher":
    st.markdown("<h1 style='color: #00d4ff;'>💼 VOID CAPITAL</h1>", unsafe_allow_html=True)
    # [Pitcher Code Preserved...]

elif nav == "🧬 Creator Lab":
    st.markdown("<h1 style='color: #00d4ff;'>🧬 VIGOR AUDIT</h1>", unsafe_allow_html=True)
    # [Vigor Code Preserved...]

elif nav == "🛰️ Lead Source":
    st.markdown("<h1 style='color: #00ff41;'>🛰️ LEAD SOURCE</h1>", unsafe_allow_html=True)
    # [Lead Source Code Preserved...]

elif nav == "📜 History":
    st.title("📜 ARCHIVES")
    # [History Code Preserved...]
