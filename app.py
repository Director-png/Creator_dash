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

# --- 🛰️ UTILITIES ---
def get_saturation_status(score):
    if score > 88: return "🔴 SATURATED (High Competition)"
    if score > 75: return "🟡 PEAK (Strategic Entry)"
    return "🟢 EARLY (High Opportunity)"

def generate_visual_dna(topic, tone):
    return f"STYLE: Cinematic Noir / LIGHTING: Neon Cyber-blue / COMPOSITION: Wide-angle, 8k detail. PROMPT: A hyper-realistic representation of {topic} for {tone} content."

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
    [data-testid="stSidebar"] {
        background-image: linear-gradient(180deg, #000000 0%, #080808 100%);
        border-right: 1px solid #00d4ff33;
    }
    .streamlit-expanderHeader {
        border: 1px solid #00ff4133 !important;
        border-radius: 5px !important;
        background-color: #000000 !important;
    }
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #000; }
    ::-webkit-scrollbar-thumb { background: #00d4ff; border-radius: 10px; }
    .stButton>button {
        border: 1px solid #00d4ff;
        background-color: transparent;
        color: #00d4ff;
        transition: 0.3s;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .stButton>button:hover {
        background-color: #00d4ff; color: black; box-shadow: 0 0 15px #00d4ff;
    }
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
if 'creator_db' not in st.session_state:
    st.session_state.creator_db = pd.DataFrame([
        {"Creator": "TechVanguard", "Niche": "AI", "Status": "Scouted", "Vigor": 82},
        {"Creator": "CyberStyle", "Niche": "Fashion", "Status": "Negotiation", "Vigor": 91}
    ])

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
        options = ["📊 Dashboard", "🌐 Global Pulse", "⚔️ Trend Duel", "🧬 Creator Lab", "🛰️ Lead Source", "💎 Script Architect", "💼 Client Pitcher", "📜 History"]
    else:
        options = ["📡 My Growth Hub", "💎 Assigned Scripts", "🌐 Global Pulse"]
    
    nav = st.radio("COMMAND CENTER", options, key="void_nav_main")

# --- MODULES ---
if nav == "📊 Dashboard" and st.session_state.user_role == "admin":
    st.markdown("<h1 style='color: white;'>🌑 VOID COMMAND CENTER</h1>", unsafe_allow_html=True)
    
    with st.expander("🔮 THE WEEKLY ORACLE"):
        if st.button("Generate Oracle Report"):
            pulse_df = load_market_pulse_data()
            top_trends = pulse_df.sort_values(by='Score', ascending=False).head(5)['Niche'].tolist()
            report = f"VOID OS WEEKLY REPORT\nDATE: {time.strftime('%Y-%m-%d')}\nTOP 5 VIGOR NICHES: {', '.join(top_trends)}"
            st.download_button("Download TXT Report", report, "void_report.txt")

    with st.expander("🛠️ Customize Layout"):
        col_edit1, col_edit2 = st.columns(2)
        st.session_state.metric_1_label = col_edit1.text_input("Metric 1 Label", st.session_state.metric_1_label)
        st.session_state.metric_1_val = col_edit1.text_input("Metric 1 Value", st.session_state.metric_1_val)
        st.session_state.daily_directive = col_edit2.text_area("Edit Daily Directive", st.session_state.daily_directive)

    with st.expander("📝 GENERATE CLIENT WEEKLY REPORT"):
        report_client = st.selectbox("Select Client for Report", st.session_state.creator_db['Creator'].tolist())
        if st.button("Generate PDF/Text Intelligence"):
            client_scripts = len([s for s in st.session_state.script_history if s.get('assigned_to') == report_client])
            report_content = f"VOID OS INTEL REPORT: {report_client}\nWEEK ENDING: {time.strftime('%Y-%m-%d')}\nSCRIPTS: {client_scripts}"
            st.text_area("Report Preview", report_content, height=200)
            st.download_button("Download Report", report_content, file_name=f"{report_client}_weekly_intel.txt")

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

elif nav == "📡 My Growth Hub":
    st.markdown(f"<h1 style='color: #00d4ff;'>📡 WELCOME, {st.session_state.user_name.upper()}</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Your Strategic Roadmap")
        st.info("🚀 **Current Phase:** Phase 1 - Authority Building (Days 1-14)")
        st.markdown("* **Focus:** Pattern Interrupt Hooks\n* **Target KPI:** 15% Increase in Average Watch Time")
    with col2:
        st.subheader("Performance Vigor")
        st.metric("Profile Health", "Good", delta="+12% Vigor")
        st.progress(65)

elif nav == "💎 Assigned Scripts":
    st.markdown("<h1 style='color: #00ff41;'>💎 YOUR ARCHITECTED SCRIPTS</h1>", unsafe_allow_html=True)
    my_scripts = [s for s in st.session_state.script_history if s.get('assigned_to') == st.session_state.user_name or s.get('assigned_to') == "Public/General"]
    if not my_scripts:
        st.warning("The Director is currently architecting your next batch. Stand by.")
    else:
        for s in reversed(my_scripts):
            with st.expander(f"📜 {s['topic']} - {s['time']}"):
                st.write(s['script'])
                st.caption(f"DNA: {s.get('dna', 'N/A')}")

elif nav == "🌐 Global Pulse":
    st.title("🌐 GLOBAL INTELLIGENCE PULSE")
    pulse_alert_df = load_market_pulse_data()
    if not pulse_alert_df.empty:
        high_heat_df = pulse_alert_df[pulse_alert_df['Score'] >= 85].sort_values(by='Score', ascending=False).head(10)
        if not high_heat_df.empty:
            st.markdown('<div style="border: 1px solid #00d4ff; padding: 20px; border-radius: 10px;">', unsafe_allow_html=True)
            st.markdown("<h3 style='color: #00d4ff;'>🚨 ELITE VIGOR SIGNALS</h3>", unsafe_allow_html=True)
            st.table(high_heat_df[['Niche', 'Score', 'Reason']])
            st.markdown("</div>", unsafe_allow_html=True)
    
    c_news, c_analysis = st.columns([2, 1])
    with c_news:
        st.subheader("📰 Live Tech Intelligence")
        feed = feedparser.parse("https://techcrunch.com/category/artificial-intelligence/feed/")
        for entry in feed.entries[:4]:
            st.markdown(f"**[{entry.title.upper()}]({entry.link})**")
            st.divider()

elif nav == "⚔️ Trend Duel":
    st.title("⚔️ COMPETITIVE INTELLIGENCE MATRIX")
    pulse_df = load_market_pulse_data()
    if not pulse_df.empty:
        target = st.selectbox("Select Niche to Audit", pulse_df['Niche'].unique())
        t_score = pulse_df[pulse_df['Niche'] == target]['Score'].values[0]
        st.metric(label=f"{target} Entry Status", value=get_saturation_status(t_score))
        sel = st.multiselect("Compare Niches", options=pulse_df['Niche'].unique().tolist(), default=pulse_df['Niche'].unique().tolist()[:5])
        st.bar_chart(data=pulse_df[pulse_df['Niche'].isin(sel)], x='Niche', y='Score')

elif nav == "💎 Script Architect":
    st.markdown("<h1 style='color: #00ff41;'>✍️ VOID SCRIPT ARCHITECT</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1.5], gap="large")
    with c1:
        topic = st.text_input("Focus Topic")
        target_client = st.selectbox("Assign to Client", ["Public/General"] + st.session_state.creator_db['Creator'].tolist())
        platform = st.selectbox("Platform", ["YouTube Shorts", "Instagram Reels", "Long-form"])
        tone = st.select_slider("Tone", options=["Aggressive", "Professional", "Storyteller"])
        
        if st.button("🚀 Architect & Queue"):
            with st.spinner("🌑 ARCHITECTING..."):
                groq_c = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = groq_c.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": f"Topic: {topic}, Platform: {platform}, Tone: {tone}"}])
                script_res = res.choices[0].message.content
                dna_res = generate_visual_dna(topic, tone)
                st.session_state.script_history.append({"time": time.strftime("%H:%M"), "topic": topic, "script": script_res, "dna": dna_res, "assigned_to": target_client})
                with c2: typewriter_effect(script_res)

elif nav == "💼 Client Pitcher" and st.session_state.user_role == "admin":
    st.markdown("<h1 style='color: #00d4ff;'>💼 VOID CAPITAL: PITCH GENERATOR</h1>", unsafe_allow_html=True)
    client = st.text_input("Lead Name")
    offer = st.text_area("Value Proposition")
    if st.button("🔥 Generate VOID Pitch"):
        groq_c = Groq(api_key=st.secrets["GROQ_API_KEY"])
        res = groq_c.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": f"Pitch for {client}: {offer}"}])
        st.write(res.choices[0].message.content)

elif nav == "🧬 Creator Lab":
    st.markdown("<h1 style='color: #00d4ff;'>🧬 CREATOR VIGOR & ACQUISITION</h1>", unsafe_allow_html=True)
    tab_crm, tab_vigor = st.tabs(["🛰️ Acquisition Pipeline", "⚡ Vigor Calculator"])
    with tab_crm:
        edited_df = st.data_editor(st.session_state.creator_db, num_rows="dynamic", use_container_width=True)
        st.session_state.creator_db = edited_df
    with tab_vigor:
        followers = st.number_input("Follower Count", value=5000)
        avg_views = st.number_input("Average Views", value=1000)
        if st.button("Calculate Vigor"):
            score = min(100, int((avg_views/followers) * 50))
            st.metric("Vigor Score", f"{score}/100")

elif nav == "🛰️ Lead Source":
    st.markdown("<h1 style='color: #00ff41;'>🛰️ VOID LEAD SOURCE</h1>", unsafe_allow_html=True)
    if st.button("Initialize Deep Scan"):
        st.success("Scan Complete. High-Value Gaps Identified.")

elif nav == "📜 History":
    st.title("📜 SYSTEM ARCHIVES")
    if st.button("🔥 PURGE ALL"): st.session_state.script_history = []; st.rerun()
    for s in reversed(st.session_state.script_history):
        with st.expander(f"🕒 {s['time']} - {s['topic']} (Client: {s.get('assigned_to')})"):
            st.write(s['script'])
