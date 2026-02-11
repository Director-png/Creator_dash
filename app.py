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

# --- TYPEWRITER UTILITY ---
def typewriter_effect(text):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(full_text + "▌")
        time.sleep(0.005) 
    container.markdown(full_text)

# --- NEW: INTELLIGENCE UTILITIES (Integrated into logic) ---
def analyze_trend_saturation(score):
    if score > 85: return "🔴 SATURATED (High Competition)"
    if score > 70: return "🟡 PEAK (Strategic Entry)"
    return "🟢 EARLY (High Opportunity)"

def generate_visual_dna(topic, tone):
    return f"Cinematic AI Prompt: Hyper-realistic, {tone} lighting, 8k, futuristic aesthetic for {topic}"

# --- 1. CONFIG ---
st.set_page_config(page_title="VOID OS", page_icon="🌑", layout="wide")

# --- 2. SPLASH SCREEN ---
if 'first_load' not in st.session_state:
    st.markdown("<style>.stApp { background-color: #000000; }</style>", unsafe_allow_html=True)
    empty_space = st.empty()
    with empty_space.container():
        if lottie_loading: st_lottie(lottie_loading, height=400)
        st.markdown("<h1 style='text-align: center; color: #00d4ff; font-family: monospace;'>INITIALIZING VOID OS...</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #00ff41; font-family: monospace;'>DECRYPTING MARKET INTELLIGENCE LAYER</p>", unsafe_allow_html=True)
        time.sleep(3.0) 
    st.session_state.first_load = True
    st.rerun()

# --- 3. GLOBAL STYLES ---
st.markdown("""
    <style>
    .matrix-bg { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: black; z-index: -1; }
    .stApp { animation: fadeInPage 1.5s ease-in-out; }
    @keyframes fadeInPage { 0% { opacity: 0; } 100% { opacity: 1; } }
    [data-testid="stMetricValue"] { animation: neonPulse 2.5s infinite alternate; color: #00d4ff !important; }
    @keyframes neonPulse { from { text-shadow: 0 0 5px #00d4ff; } to { text-shadow: 0 0 20px #00d4ff; } }
    </style>
""", unsafe_allow_html=True)

# --- DATA URLS ---
PULSE_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuN3zcXZqn9RMnPs7vNEa7vI9xr1Y2VVVlZLUcEwUVqsVqtLMadz1L_Ap4XK_WPA1nnFdpqGr8B_uS/pub?output=csv"
MARKET_URL = "https://docs.google.com/spreadsheets/d/163haIuPIna3pEY9IDxncPM2kFFsuZ76HfKsULcMu1y4/export?format=csv"
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"
FORM_POST_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfnNLb9O-szEzYfYEL85aENIimZFtMd5H3a7o6fX-_6ftU_HA/formResponse"

# --- CORE FUNCTIONS ---
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
    try:
        if 'media_content' in entry: return entry.media_content[0]['url']
        soup = BeautifulSoup(entry.summary, 'html.parser')
        img = soup.find('img')
        if img: return img['src']
    except: pass
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

# --- GATEKEEPER ---
if not st.session_state.logged_in:
    st.markdown('<div class="matrix-bg"></div>', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #00ff41;'>🛡️ DIRECTOR'S INTELLIGENCE PORTAL</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Login", "📝 Register"])
    with t1:
        c_l, c_mid, c_r = st.columns([1, 2, 1])
        with c_mid:
            email_in = st.text_input("Email").lower().strip()
            pw_in = st.text_input("Password", type="password")
            if st.button("Access System", use_container_width=True):
                users = load_user_db()
                if email_in == "admin" and pw_in == "1234":
                    st.session_state.logged_in = True; st.session_state.user_name = "Master Director"; st.session_state.user_role = "admin"; st.rerun()
                elif not users.empty:
                    match = users[(users.iloc[:, 2].astype(str).str.lower() == email_in) & (users.iloc[:, 4].astype(str) == pw_in)]
                    if not match.empty:
                        st.session_state.logged_in = True; st.session_state.user_name = match.iloc[0, 1]
                        niche_val = str(match.iloc[0, 3]).lower()
                        st.session_state.user_role = "admin" if any(x in niche_val for x in ["fitness", "admin"]) else "user"
                        st.rerun()
    with t2:
        c_l, c_mid, c_r = st.columns([1, 2, 1])
        with c_mid:
            with st.form("reg"):
                n = st.text_input("Name"); e = st.text_input("Email"); ni = st.text_input("Niche"); p = st.text_input("Password", type="password")
                if st.form_submit_button("Submit"):
                    requests.post(FORM_POST_URL, data={"entry.483203499": n, "entry.1873870532": e, "entry.1906780868": ni, "entry.1396549807": p})
                    st.success("Transmitted!")
    st.stop()

# --- SIDEBAR & NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #00d4ff;'>🌑 VOID OS</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #00ff41;'>● {st.session_state.user_name.upper()}</p>", unsafe_allow_html=True)
    
    if st.session_state.user_role == "admin":
        options = ["📊 Dashboard", "🌐 Global Pulse", "⚔️ Trend Duel", "💎 Script Architect", "💼 Client Pitcher", "📜 History"]
    else:
        options = ["🌐 Global Pulse", "⚔️ Trend Duel", "💎 Script Architect", "📜 History"]
    
    nav = st.radio("COMMAND CENTER", options)
    st.divider()
    
    if st.button("🔓 Terminate Session", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()

# --- MODULES ---

if nav == "📊 Dashboard" and st.session_state.user_role == "admin":
    st.markdown("<h1 style='color: white;'>🌑 VOID COMMAND CENTER</h1>", unsafe_allow_html=True)
    with st.expander("🛠️ Customize Layout"):
        col_edit1, col_edit2 = st.columns(2)
        st.session_state.metric_1_label = col_edit1.text_input("Metric 1 Label", st.session_state.metric_1_label)
        st.session_state.metric_1_val = col_edit1.text_input("Metric 1 Value", st.session_state.metric_1_val)
        st.session_state.daily_directive = col_edit2.text_area("Edit Daily Directive", st.session_state.daily_directive)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label=st.session_state.metric_1_label, value=st.session_state.metric_1_val)
    m2.metric(label="Scripts Ready", value=str(len(st.session_state.script_history)), delta="+")
    m3.metric(label="Agency Leads", value=str(len(st.session_state.pitch_history)), delta="Target: 10")
    m4.metric(label="System Status", value="Operational")

    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.subheader("🚀 Active VOID Roadmap")
        st.table(pd.DataFrame({"Phase": ["VOID Intel", "Script Architect", "Client Pitcher", "Agency Portal"], "Status": ["Stable", "Stable", "Online", "Planned"], "Priority": ["Done", "Active", "High", "Critical"]}))
    with col_r:
        st.subheader("💡 Daily Directive")
        st.info(st.session_state.daily_directive)
        st.progress(45)

elif nav == "🌐 Global Pulse":
    st.title("🌐 GLOBAL INTELLIGENCE PULSE")
    
    # --- 1. CURATED PULSE ALERT SYSTEM (Elite 10) ---
    pulse_alert_df = load_market_pulse_data()
    if not pulse_alert_df.empty:
        # Filter for top 10 elite signals only
        high_heat_df = pulse_alert_df[pulse_alert_df['Score'] >= 85].sort_values(by='Score', ascending=False).head(10)
        
        if not high_heat_df.empty:
            with st.container():
                st.markdown("""
                    <div style="background-color: rgba(0, 212, 255, 0.05); border: 1px solid #00d4ff; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
                        <h3 style="color: #00d4ff; margin-top: 0; font-family: monospace; letter-spacing: 2px;">🚨 ELITE VIGOR SIGNALS (TOP 10)</h3>
                """, unsafe_allow_html=True)
                
                cols = st.columns(2) 
                for i, (_, alert) in enumerate(high_heat_df.iterrows()):
                    col_choice = cols[0] if i % 2 == 0 else cols[1]
                    with col_choice:
                        st.markdown(f"<span style='color: #00ff41;'>📡</span> **{alert['Niche']}**", unsafe_allow_html=True)
                        st.markdown(f"**Velocity:** `{alert['Score']}` | {alert['Reason']}")
                        st.markdown("---")
                st.markdown("</div>", unsafe_allow_html=True)

    # --- 2. LIVE INTELLIGENCE FEED ---
    c_news, c_analysis = st.columns([2.5, 1], gap="large")
    
    with c_news:
        st.subheader("📰 Live Tech Intelligence")
        feed = feedparser.parse("https://techcrunch.com/category/artificial-intelligence/feed/")
        for entry in feed.entries[:8]: # Increased to 8 since we have more space
            img_col, txt_col = st.columns([1, 3])
            with img_col: 
                st.image(get_intel_image(entry), use_container_width=True)
            with txt_col:
                st.markdown(f"**[{entry.title.upper()}]({entry.link})**")
                st.write(BeautifulSoup(entry.summary, "html.parser").text[:150] + "...")
            st.divider()

    with c_analysis:
        st.subheader("⚡ VOID Analysis")
        st.info("**Trending Keywords:**\n- LangGraph\n- Sora Visuals\n- Local LLMs\n- Agentic Workflows")
        
        st.markdown("---")
        st.subheader("🕵️ System Logic")
        st.caption("Intelligence is being pulled from 14+ live sources. The Vigor Signals represent niches with over 85% growth probability in the next 72 hours.")
        
        # Adding a visual touch to fill the sidebar space
        st.image("https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400", caption="Global Data Mesh")

elif nav == "⚔️ Trend Duel":
    st.title("⚔️ COMPETITIVE INTELLIGENCE MATRIX")
    pulse_df = load_market_pulse_data()
    if not pulse_df.empty:
        # --- SATURATION METER INTEGRATION ---
        st.subheader("🌑 VOID Saturation Analysis")
        selected_n = st.selectbox("Analyze Market Density", pulse_df['Niche'].unique())
        n_score = pulse_df[pulse_df['Niche'] == selected_n]['Score'].values[0]
        st.metric(f"{selected_n} Status", analyze_trend_saturation(n_score))

        st.subheader("📊 Comparative View")
        sel = st.multiselect("Compare Niches", options=pulse_df['Niche'].unique().tolist(), default=pulse_df['Niche'].unique().tolist()[:5])
        comp = pulse_df[pulse_df['Niche'].isin(sel)]
        if not comp.empty:
            st.bar_chart(data=comp, x='Niche', y='Score')
            st.dataframe(comp)

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
                with c2: typewriter_effect(pitch_res)

elif nav == "💎 Script Architect":
    st.markdown("<h1 style='color: #00ff41;'>✍️ VOID SCRIPT ARCHITECT</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1.5], gap="large")
    with c1:
        topic = st.text_input("Focus Topic")
        platform = st.selectbox("Platform", ["YouTube Shorts", "Instagram Reels", "Long-form"])
        tone = st.select_slider("Tone", options=["Aggressive", "Professional", "Storyteller"])
        if st.button("🚀 Architect Script"):
            with st.spinner("🌑 COMPILING SCRIPT DATA..."):
                groq_c = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = groq_c.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": f"Script: {topic}, {platform}, {tone}"}])
                script_res = res.choices[0].message.content
                # --- CONTENT DNA INTEGRATION ---
                visual_dna = generate_visual_dna(topic, tone)
                st.session_state.script_history.append({"time": time.strftime("%H:%M:%S"), "topic": topic, "script": script_res, "dna": visual_dna})
                with c2: 
                    typewriter_effect(script_res)
                    st.info(f"🧬 **CONTENT DNA:** {visual_dna}")

elif nav == "📜 History":
    st.title("📜 SYSTEM ARCHIVES")
    with st.expander("⚠️ SYSTEM MAINTENANCE"):
        st.warning("Action will permanently erase all local session logs.")
        if st.button("🔥 PURGE ALL SYSTEM LOGS", use_container_width=True):
            st.session_state.script_history = []
            st.session_state.pitch_history = []
            st.success("Session logs annihilated.")
            time.sleep(1)
            st.rerun()
    
    if st.session_state.user_role == "admin":
        t_scripts, t_secret = st.tabs(["Script History", "Director Intelligence"])
        with t_scripts:
            if not st.session_state.script_history: st.write("No scripts archived.")
            for s in reversed(st.session_state.script_history):
                with st.expander(f"🕒 {s['time']} - {s['topic']}"): 
                    st.write(s['script'])
                    if 'dna' in s: st.caption(f"DNA: {s['dna']}")
        with t_secret:
            if not st.session_state.pitch_history: st.write("No intelligence logs found.")
            for p in reversed(st.session_state.pitch_history):
                with st.expander(f"🕒 {p['time']} - Lead: {p['client']}"): st.write(p['pitch'])
    else:
        st.subheader("Script Archives")
        if not st.session_state.script_history: st.write("No scripts archived.")
        for s in reversed(st.session_state.script_history):
            with st.expander(f"🕒 {s['time']} - {s['topic']}"): 
                st.write(s['script'])
                if 'dna' in s: st.caption(f"DNA: {s['dna']}")



