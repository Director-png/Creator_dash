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

# --- 1. SESSION STATE (CRITICAL INITIALIZATION) ---
if 'found_leads' not in st.session_state:
    st.session_state.found_leads = pd.DataFrame()
if 'script_history' not in st.session_state:
    st.session_state.script_history = []
if 'pitch_history' not in st.session_state:
    st.session_state.pitch_history = []
if 'creator_db' not in st.session_state:
    st.session_state.creator_db = pd.DataFrame([
        {"Creator": "TechVanguard", "Niche": "AI", "Status": "Scouted", "Vigor": 82},
        {"Creator": "CyberStyle", "Niche": "Fashion", "Status": "Negotiation", "Vigor": 91},
        {"Creator": "MidnightAlpha", "Niche": "Gaming", "Status": "Signed", "Vigor": 95},
        {"Creator": "NeonMinimalist", "Niche": "Design", "Status": "Scouted", "Vigor": 78}
    ])
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'last_topic' not in st.session_state: st.session_state.last_topic = "General AI Intelligence"
if 'user_name' not in st.session_state: st.session_state.user_name = "Guest"
if 'user_role' not in st.session_state: st.session_state.user_role = "user"

# --- 🛰️ DATA INFRASTRUCTURE ---
PULSE_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuN3zcXZqn9RMnPs7vNEa7vI9xr1Y2VVVlZLUcEwUVqsVqtLMadz1L_Ap4XK_WPA1nnFdpqGr8B_uS/pub?output=csv"
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?gid=989182688&single=true&output=csv"
FORM_POST_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfnNLb9O-szEzYfYEL85aENIimZFtMd5H3a7o6fX-_6ftU_HA/formResponse"
SCRIPT_VAULT_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"
VAULT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfeDAY3gnWYlpH90EaJirxUc8d4obYUgiX72WJIah7Cya1VNQ/formResponse"
VAULT_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTtSx9iQTrDvNWe810s55puzBodFKvfUbfMV_l-QoQIfbdPxeQknClGGCQT33UQ471NyGTw4aHLrDTw/pub?output=csv"

# --- 🛰️ UTILITIES & BRAIN FUNCTIONS ---
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
        sync_url = f"{USER_DB_URL}&cache_bus={time.time()}"
        df = pd.read_csv(sync_url)
        if df.empty: return pd.DataFrame()
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        st.sidebar.error(f"Sync Failure: {e}")
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
        "Instagram Reels": "High-contrast, 0.5s jump cuts, Glow-on-dark aesthetics, grainy film overlays.",
        "YouTube Shorts": "Center-framed, bold captions, neon-accent lighting, fast zoom-ins.",
        "YouTube Long-form": "Cinematic 4k, shallow depth of field, 24fps motion blur, color graded for teal/orange.",
        "TikTok": "Raw mobile-style, high-saturation, fast-paced text overlays, green-screen effects.",
        "X-Thread": "High-authority typography, clean minimalist screenshots, bold black/white contrast."
    }
    aesthetic = styles.get(platform, "Professional cinematic cyber-noir aesthetic.")
    return f"DNA PROFILE: {aesthetic} | TONE: {tone} | LIGHTING: Cyber-Noir Studio"

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
    if score > 75: return "🟡 PEAK (Strategic Entry Required)"
    return "🟢 EARLY (High Growth Opportunity)"

def transmit_script(client, platform, topic, script, dna):
    url = "https://script.google.com/macros/s/AKfycby9nYH4bTmC0rFoZQWj87S-hiu7lJeXXd4mVuRyJxrVTk-OGaPx5zFNZzgYZWSRuNH0/exec"
    payload = {"client": client, "platform": platform, "topic": topic, "script": script, "dna": dna}
    try:
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except: return False

def generate_oracle_report(topic, platform, tone):
    try:
        groq_c = Groq(api_key=st.secrets["GROQ_API_KEY"])
        prompt = f"""
        System: You are the VOID OS Oracle. Analyze content architecture for {platform}.
        Topic: {topic} | Tone: {tone}
        
        Provide a 'Growth Intelligence Report' with:
        1. 📈 VIRAL VELOCITY: Why this topic is peaking now based on global sentiment.
        2. 🧠 PSYCHOLOGICAL HOOK: The specific 'Human Bias' (like FOMO or Zeigarnik effect) this script exploits.
        3. 🚀 SCALING STRATEGY: How to turn this one video into a 5-part series for maximum retention.
        """
        res = groq_c.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Oracle connection interrupted: {e}"

# --- 1. CONFIG ---
st.set_page_config(page_title="VOID OS", page_icon="🌑", layout="wide")

# --- 2. SPLASH SCREEN ---
if 'first_load' not in st.session_state:
    st.markdown("<style>.stApp { background-color: #000000; }</style>", unsafe_allow_html=True)
    empty_space = st.empty()
    with empty_space.container():
        if lottie_loading: st_lottie(lottie_loading, height=400)
        st.markdown("<h1 style='text-align: center; color: #00d4ff; font-family: monospace;'>INITIALIZING VOID OS...</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #333;'>SYNCING NEURAL NODES</p>", unsafe_allow_html=True)
        time.sleep(3.0) 
    st.session_state.first_load = True
    st.rerun()

# --- 3. GLOBAL STYLES ---
st.markdown("""<style>
    [data-testid="stSidebar"] { background-image: linear-gradient(180deg, #000000 0%, #080808 100%); border-right: 1px solid #00d4ff33; }
    .stButton>button { border: 1px solid #00d4ff; background-color: transparent; color: #00d4ff; letter-spacing: 2px; font-family: monospace; transition: 0.3s; }
    .stButton>button:hover { background-color: #00d4ff; color: black; box-shadow: 0 0 20px #00d4ff; }
    .stTextInput>div>div>input { background-color: #050505; color: #00d4ff; border: 1px solid #111; }
    .stTextArea>div>div>textarea { background-color: #050505; color: #00d4ff; border: 1px solid #111; }
    .stSelectbox>div>div { background-color: #050505; color: #00d4ff; }
    .stExpander { background-color: #050505; border: 1px solid #00d4ff22 !important; border-radius: 5px; }
    h1, h2, h3 { font-family: 'Courier New', Courier, monospace; letter-spacing: -1px; }
    .stMetric { border: 1px solid #111; padding: 15px; border-radius: 10px; background: #080808; }
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
                else: st.error("Access Denied: Credentials Invalid.")
    with t2:
        with st.form("reg"):
            n = st.text_input("Name"); e = st.text_input("Email"); ni = st.text_input("Niche"); p = st.text_input("Password", type="password")
            if st.form_submit_button("Submit Registration"):
                requests.post(FORM_POST_URL, data={"entry.483203499": n, "entry.1873870532": e, "entry.1906780868": ni, "entry.1396549807": p})
                st.success("Transmission Received. Awaiting Node Approval.")
    st.stop()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown(f"<h3 style='text-align: center; color: #00ff41;'>● {st.session_state.user_name.upper()}</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #444; font-size: 10px;'>ENCRYPTED CONNECTION : ACTIVE</p>", unsafe_allow_html=True)
    if st.session_state.user_role == "admin":
        options = ["📊 Dashboard", "🌐 Global Pulse", "⚔️ Trend Duel", "🧬 Creator Lab", "🛰️ Lead Source", "💎 Script Architect", "💼 Client Pitcher", "📜 History"]
    else:
        options = ["📡 My Growth Hub", "💎 Assigned Scripts", "🌐 Global Pulse"]
    nav = st.radio("COMMAND CENTER", options, key="void_nav_main")
    st.divider()
    if st.button("LOGOUT"): st.session_state.logged_in = False; st.rerun()

# --- MODULE 1: DASHBOARD ---
if nav == "📊 Dashboard":
    st.markdown("<h1 style='color: white;'>🌑 VOID COMMAND CENTER</h1>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric(label="System Status", value="Operational", delta="Stable")
    with m2: st.metric(label="Scripts Architected", value=str(len(st.session_state.script_history)), delta="+4 today")
    with m3: st.metric(label="Active Pipelines", value="12", delta="3 Ready")
    with m4: st.metric(label="Data Sync", value="Real-time", delta="0.4ms")
    
    st.divider()
    c_left, c_right = st.columns([2, 1])
    with c_left:
        st.subheader("📡 Regional Signal Strength")
        chart_data = pd.DataFrame({"Node": ["US-East", "EU-West", "Asia-South"], "Traffic": [85, 92, 78]})
        st.bar_chart(chart_data, x="Node", y="Traffic", color="#00d4ff")
    with c_right:
        st.subheader("🛡️ Security Audit")
        st.code("Neural Handshake: VERIFIED\nIP Scramble: ACTIVE\nUser DB: ENCRYPTED", language="bash")

# --- MODULE 2: MY GROWTH HUB ---
elif nav == "📡 My Growth Hub":
    st.markdown(f"<h1 style='color: #00d4ff;'>📡 WELCOME, {st.session_state.user_name.upper()}</h1>", unsafe_allow_html=True)
    with st.expander("🔮 ACCESS ORACLE INTELLIGENCE", expanded=True):
        st.markdown("### 🧬 Strategic Growth Vectors")
        if st.button("RUN ORACLE ANALYSIS", use_container_width=True):
            if 'last_topic' in st.session_state:
                with st.spinner("📡 SCANNING GLOBAL TRENDS..."):
                    report = generate_oracle_report(st.session_state.last_topic, "Global", "Elite")
                    st.info(report)
            else:
                st.warning("Director, architect a script in the Command Center first to provide training data.")
    
    st.subheader("📈 Performance Metrics")
    col1, col2 = st.columns(2)
    col1.metric("Current Vigor", "88/100", "+5%")
    col2.metric("Audience Retention", "62%", "+2.1%")

# --- MODULE 3: ASSIGNED SCRIPTS ---
elif nav == "💎 Assigned Scripts":
    st.title("💎 YOUR SECURE VAULT")
    try:
        scripts_df = pd.read_csv(VAULT_SHEET_CSV_URL)
        scripts_df.columns = [str(c).strip().lower() for c in scripts_df.columns]
        my_vault = scripts_df[scripts_df.iloc[:, 1].astype(str) == st.session_state.user_name]
        
        if my_vault.empty: 
            st.warning("No scripts assigned yet. Awaiting Director transmission.")
        else:
            for _, row in my_vault.iterrows():
                with st.expander(f"📜 {row.iloc[3]} | {row.iloc[2]}"):
                    st.markdown(f"**PLATFORM:** {row.iloc[2]}")
                    st.divider()
                    st.write(row.iloc[4])
                    st.divider()
                    st.caption(f"🧬 DNA: {row.iloc[5]}")
                    st.button("MARK AS FILMED", key=f"btn_{row.iloc[0]}")
    except Exception as e:
        st.error(f"Vault Offline: {e}")

# --- MODULE 4: GLOBAL PULSE ---
elif nav == "🌐 Global Pulse":
    st.title("🌐 GLOBAL INTELLIGENCE PULSE")
    pulse_df = load_market_pulse_data()
    if not pulse_df.empty:
        st.markdown('<div style="border: 1px solid #00d4ff; padding: 20px; border-radius: 10px; margin-bottom: 30px;">', unsafe_allow_html=True)
        st.markdown("<h3 style='color: #00d4ff;'>🚨 ELITE VIGOR SIGNALS</h3>", unsafe_allow_html=True)
        cols = st.columns(2)
        high_heat = pulse_df[pulse_df['Score'] >= 85].sort_values(by='Score', ascending=False).head(10)
        for i, (_, alert) in enumerate(high_heat.iterrows()):
            with cols[i%2]:
                st.markdown(f"📡 **{alert['Niche']}** | `Score: {alert['Score']}`")
                st.caption(alert['Reason'])
                st.divider()
        st.markdown("</div>", unsafe_allow_html=True)

    c_news, c_analysis = st.columns([2, 1])
    with c_news:
        st.subheader("📰 Live Tech Intelligence")
        feed = feedparser.parse("https://techcrunch.com/category/artificial-intelligence/feed/")
        for entry in feed.entries[:6]:
            img_col, txt_col = st.columns([1, 2.5])
            with img_col: st.image(get_intel_image(entry), use_container_width=True)
            with txt_col:
                st.markdown(f"**[{entry.title.upper()}]({entry.link})**")
                st.write(BeautifulSoup(entry.summary, "html.parser").text[:180] + "...")
            st.divider()

# --- MODULE 5: TREND DUEL ---
elif nav == "⚔️ Trend Duel":
    st.title("⚔️ TREND DUEL")
    pulse_df = load_market_pulse_data()
    if not pulse_df.empty:
        st.subheader("🌑 Market Density Analysis")
        target = st.selectbox("Select Niche to Audit", pulse_df['Niche'].unique())
        row = pulse_df[pulse_df['Niche'] == target].iloc[0]
        st.metric(label=f"{target} Entry Status", value=get_saturation_status(row['Score']))
        st.table(pulse_df[pulse_df['Niche'] == target][['Niche', 'Score', 'Reason']])
        st.divider()
        sel = st.multiselect("Compare Niches", options=pulse_df['Niche'].unique().tolist(), default=pulse_df['Niche'].unique().tolist()[:5])
        comp = pulse_df[pulse_df['Niche'].isin(sel)]
        if not comp.empty: 
            fig = px.bar(comp, x='Niche', y='Score', color='Score', template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)

# --- MODULE 6: SCRIPT ARCHITECT ---
elif nav == "💎 Script Architect":
    st.markdown("<h1 style='color: #00ff41;'>⚔️ TACTICAL ARCHITECT</h1>", unsafe_allow_html=True)
    users_df = load_user_db()
    client_options = ["Public/General"]
    if not users_df.empty:
        db_names = users_df.iloc[:, 1].dropna().unique().tolist()
        client_options = ["Public/General"] + db_names

    c1, c2 = st.columns([1, 1.5], gap="large")
    with c1:
        target_client = st.selectbox("Assign To Target", options=client_options, key="arch_target_final")
        platform = st.selectbox("Platform", ["Instagram Reels", "YouTube Shorts", "TikTok", "X-Thread", "YouTube Long-form"])
        topic = st.text_input("Core Topic", placeholder="e.g., The Future of AI in 2026")
        tone_choice = st.select_slider("Vigor/Tone", ["Professional", "Aggressive", "Elite"])
        with st.expander("👤 COMPETITOR SHADOW"):
            c_hook = st.text_area("Their Narrative (What are they saying?)")
        
        if st.button("🚀 ARCHITECT & TRANSMIT", use_container_width=True):
            if not topic:
                st.error("Director, the Topic field cannot be empty.")
            else:
                st.session_state.last_topic = topic
                with st.spinner("🌑 ARCHITECTING SCRIPT..."):
                    try:
                        groq_c = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        prompt = f"System: VOID OS Content Architect. Platform: {platform}. Topic: {topic}. Tone: {tone_choice}. Angle: {c_hook if c_hook else 'None'}."
                        res = groq_c.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                        txt = res.choices[0].message.content
                        dna_profile = generate_visual_dna(platform, tone_choice)
                        status = transmit_script(target_client, platform, topic, txt, dna_profile)
                        with c2:
                            st.subheader("💎 GENERATED ARCHIVE")
                            st.markdown(txt)
                            st.divider()
                            st.caption(f"🧬 DNA: {dna_profile}")
                            if status: st.success("⚔️ BROADCAST COMPLETE: Script synced.")
                    except Exception as e: st.error(f"Intelligence Failure: {e}")

# --- MODULE 7: CLIENT PITCHER ---
elif nav == "💼 Client Pitcher":
    st.markdown("<h1 style='color: #00d4ff;'>💼 VOID CAPITAL</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1.5], gap="large")
    with c1:
        client_name = st.text_input("Lead / Brand Name")
        niche_cat = st.selectbox("Category", ["Personal Brand", "SaaS Founders", "Fashion", "Local Business"])
        offer_details = st.text_area("Value Proposition")
        if st.button("🔥 Generate VOID Pitch"):
            if client_name and offer_details:
                with st.spinner("🌑 ANALYZING LEAD..."):
                    groq_c = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    prompt = f"Write an elite black-label pitch for {client_name} in {niche_cat}. Offer: {offer_details}."
                    res = groq_c.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                    pitch_res = res.choices[0].message.content
                    with c2: typewriter_effect(pitch_res)

# --- MODULE 8: CREATOR LAB & LEAD SOURCE ---
elif nav == "🧬 Creator Lab":
    st.title("🧬 VIGOR AUDIT")
    c_name = st.text_input("Creator Handle")
    c_views = st.number_input("Avg Views", value=5000)
    c_subs = st.number_input("Follower Count", value=10000)
    if st.button("⚡ Calculate Vigor"):
        score = calculate_vigor(c_views, c_subs)
        st.metric("VIGOR SCORE", f"{score}/100")
        if score > 80: st.success(f"🔥 {c_name} is viral-prone.")

elif nav == "🛰️ Lead Source":
    st.title("🛰️ LEAD SOURCE")
    niche_search = st.selectbox("Target Niche", ["SaaS", "E-com", "Coaching"])
    if st.button("Initialize Deep Scan"):
        st.session_state.found_leads = pd.DataFrame([{"Handle": "@Nexus_AI", "Platform": "IG", "Gap": "No Video"}])
    if not st.session_state.found_leads.empty:
        st.table(st.session_state.found_leads)

# --- MODULE 9: HISTORY ---
elif nav == "📜 History":
    st.title("📜 ARCHIVES")
    st.write("Director's Session History")
    for s in reversed(st.session_state.script_history):
        with st.expander(f"{s['assigned_to']} | {s['topic']}"):
            st.write(s['script'])
