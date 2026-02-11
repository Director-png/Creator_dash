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
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?gid=989182688&single=true&output=csv"
FORM_POST_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfnNLb9O-szEzYfYEL85aENIimZFtMd5H3a7o6fX-_6ftU_HA/formResponse"

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
# --- ADD THESE TO YOUR UTILITIES SECTION ---

def calculate_vigor(views, followers):
    """The Director's Formula: Views-to-Follower Leverage"""
    if followers == 0: return 0
    ratio = views / followers
    score = min(100, int(ratio * 50)) # Higher ratio = Higher Algorithmic Vigor
    return score

def generate_visual_dna(platform, tone):
    """Generates specific aesthetic prompts for editors"""
    styles = {
        "Instagram Reels": "High-contrast, 0.5s jump cuts, Glow-on-dark aesthetics.",
        "YouTube Shorts": "Center-framed, bold captions, neon-accent lighting.",
        "YouTube Long-form": "Cinematic 4k, shallow depth of field, 24fps motion blur.",
        "TikTok": "Raw mobile-style, high-saturation, fast-paced text overlays."
    }
    aesthetic = styles.get(platform, "Professional cinematic.")
    return f"DNA PROFILE: {aesthetic} | TONE: {tone} | LIGHTING: Cyber-Noir"
    
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
        border: 1px solid #00d4ff; background-color: transparent; color: #00d4ff;
        transition: 0.3s; text-transform: uppercase; letter-spacing: 2px;
    }
    .stButton>button:hover {
        background-color: #00d4ff; color: black; box-shadow: 0 0 15px #00d4ff;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA URLS ---
PULSE_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuN3zcXZqn9RMnPs7vNEa7vI9xr1Y2VVVlZLUcEwUVqsVqtLMadz1L_Ap4XK_WPA1nnFdpqGr8B_uS/pub?output=csv"
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"
FORM_POST_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfnNLb9O-szEzYfYEL85aENIimZFtMd5H3a7o6fX-_6ftU_HA/formResponse"
SCRIPT_VAULT_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?gid=0&single=true&output=csv"
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
    st.set_page_config(page_title="VOID LOGIN", page_icon="🌑")
    st.markdown("<h1 style='text-align: center; color: #00ff41;'>🛡️ DIRECTOR'S INTELLIGENCE PORTAL</h1>", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with t1:
        email_in = st.text_input("Email").lower().strip()
        pw_in = st.text_input("Password", type="password")
        if st.button("Access System", use_container_width=True):
            users = load_user_db()
            # Admin Bypass
            if email_in == "admin" and pw_in == "1234":
                st.session_state.logged_in = True
                st.session_state.user_name = "Master Director"
                st.session_state.user_role = "admin"
                st.rerun()
            # Database Match
            elif not users.empty:
                # Col 2: Email | Col 4: Password | Col 3: Niche
                match = users[(users.iloc[:, 2].astype(str).str.lower() == email_in) & (users.iloc[:, 4].astype(str) == pw_in)]
                if not match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_name = match.iloc[0, 1]
                    st.session_state.user_niche = match.iloc[0, 3]
                    st.session_state.user_role = "user"
                    st.rerun()
                else: st.error("Credentials Rejected.")

    with t2:
        with st.form("reg"):
            st.subheader("New Client Onboarding")
            n = st.text_input("Name")
            e = st.text_input("Email")
            ni = st.text_input("Niche (Focus Area)")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Submit to VOID"):
                payload = {"entry.483203499": n, "entry.1873870532": e, "entry.1906780868": ni, "entry.1396549807": p}
                requests.post(FORM_POST_URL, data=payload)
                st.success("Transmission Received. Try logging in after 5 seconds.")
    st.stop()

# --- SIDEBAR ---
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

    with st.expander("📝 GENERATE CLIENT WEEKLY REPORT"):
        report_client = st.selectbox("Select Client for Report", [c['Creator'] for _, c in st.session_state.creator_db.iterrows()])
        if st.button("Generate Intelligence"):
            client_scripts = len([s for s in st.session_state.script_history if s.get('assigned_to') == report_client])
            report_content = f"VOID OS INTEL REPORT: {report_client}\nDATE: {time.strftime('%Y-%m-%d')}\nSCRIPTS: {client_scripts}"
            st.text_area("Report Preview", report_content, height=150)

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

# --- UPDATED CLIENT VIEW (THE RECEIVER) ---
elif nav == "💎 Assigned Scripts":
    st.title("💎 YOUR SECURE VAULT")
    
    # We pull from the LIVE Google Sheet now, not the session memory
    try:
        scripts_df = pd.read_csv(SCRIPT_VAULT_CSV_URL)
        scripts_df.columns = [str(c).strip().lower() for c in scripts_df.columns]
        
        # Filter by the logged-in user's name
        my_vault = scripts_df[scripts_df.iloc[:, 1].astype(str) == st.session_state.user_name]
        
        if my_vault.empty:
            st.warning("The Director has not assigned any scripts to this frequency yet.")
        else:
            for _, row in my_vault.iterrows():
                with st.expander(f"📜 {row.iloc[3]}"): # Adjust index based on your sheet
                    st.write(row.iloc[4])
                    st.caption(f"DNA: {row.iloc[5]}")
    except:
        st.error("Vault Connection Offline. Director must publish the Script CSV.")


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
                st.write(BeautifulSoup(entry.summary, "html.parser").text[:120] + "...")
            st.divider()
    with c_analysis:
        st.subheader("⚡ AI Trend Analysis")
        st.info("**Trending Keywords:**\n- LangGraph\n- Sora Visuals\n- Local LLMs")
        st.image("https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400")

elif nav == "⚔️ Trend Duel":
    st.title("⚔️ COMPETITIVE INTELLIGENCE MATRIX")
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
        if not comp.empty: st.bar_chart(data=comp, x='Niche', y='Score')

# --- 🛰️ NEW DATA LINK (The Mailbox) ---
# Replace this with the link to the CSV of the sheet where your scripts are stored
SCRIPT_VAULT_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"

def transmit_script(client, platform, topic, script, dna):
    """Pushes the architected script to the Google Form/Sheet database"""
    # Replace these entry IDs with your actual Google Form entry IDs
    payload = {
        "entry.546765267": client,   # Client Name Field
        "entry.1077052292": platform, # Platform Field
        "entry.415250537": topic,    # Topic Field
        "entry.1437097100": script,   # The Script itself
        "entry.1608255172": dna       # Visual DNA
    }
    try:
        requests.post(FORM_POST_URL, data=payload) # Using your existing Form URL or a new one
        return True
    except:
        return False

# --- SCRIPT ARCHITECT (WITH DUPLICATE ID FIX) ---
if nav == "💎 Script Architect":
    st.markdown("<h1 style='color: #00ff41;'>⚔️ TACTICAL ARCHITECT</h1>", unsafe_allow_html=True)
 
def load_user_db():
    try:
        # We add a unique timestamp to the URL to force a fresh pull
        timestamp = int(time.time())
        sync_url = f"{USER_DB_URL}&cv={timestamp}" 
        
        # Adding a timeout so the app doesn't hang forever
        df = pd.read_csv(sync_url, timeout=5)
        
        if df.empty:
            return pd.DataFrame()
            
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        # If this shows up, the URL is definitely wrong or not published
        st.sidebar.warning(f"Connection Attempt Failed: {e}")
        return pd.DataFrame()
        
    users_df = load_user_db()
    
    # 1. DEBUG BOX (Only visible to help us fix the 'Public' issue)
    if not users_df.empty:
        with st.expander("🔍 DATA STRUCTURE DIAGNOSTIC"):
            st.write("Columns detected:", users_df.columns.tolist())
            st.write("Raw Data Preview:", users_df.head(3))
    else:
        st.error("📡 DATA LINK SEVERED: Check your USER_DB_URL and ensure it is 'Published to Web'.")

    # 2. CLIENT LIST LOGIC
    client_options = ["Public/General"]
    if not users_df.empty:
        # Search for any column name that contains "name"
        name_col = [c for c in users_df.columns if 'name' in c]
        if name_col:
            db_names = users_df[name_col[0]].dropna().unique().tolist()
            client_options = ["Public/General"] + db_names
        else:
            # Fallback to column index 1 if no 'name' header found
            db_names = users_df.iloc[:, 1].dropna().unique().tolist()
            client_options = ["Public/General"] + db_names

    # 3. THE UI (With Unique Key to fix the Duplicate ID error)
    c1, c2 = st.columns([1, 1.2], gap="large")
    
    with c1:
        # We add 'key="architect_target"' to make this unique
        target_client = st.selectbox(
            "Assign To Target", 
            options=client_options, 
            key="architect_target" 
        )
        
        platform = st.selectbox(
            "Platform", 
            ["Instagram Reels", "YouTube Shorts", "TikTok", "YouTube Long-form"],
            key="platform_selector"
        )
        
        topic = st.text_input("Core Topic", key="topic_input")
        tone_choice = st.select_slider("Vigor/Tone", ["Professional", "Aggressive", "Elite"], key="tone_slider")
        
 
        with st.expander("👤 COMPETITOR SHADOW"):
            c_hook = st.text_area("Their Narrative")

        if st.button("🚀 ARCHITECT & TRANSMIT", use_container_width=True):
            if topic:
                with st.spinner("🌑 ARCHITECTING..."):
                    groq_c = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    
                    # TACTICAL PROMPT USING THE CLIENT'S NICHE
                    prompt = f"System: VOID OS. Architect a {platform} script for a client in the {current_niche} niche. Topic: {topic}. Tone: {tone_choice}."
                    if c_hook: prompt += f" DISPROVE THIS: {c_hook}"
                    
                    res = groq_c.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                    txt = res.choices[0].message.content
                    dna_profile = generate_visual_dna(platform, tone_choice)
                    
                    # BROADCAST
                    transmit_status = transmit_script(target_client, platform, topic, txt, dna_profile)
                    
                    if transmit_status:
                        st.success("⚔️ BROADCAST COMPLETE")
                    
                    with c2:
                        st.subheader("💎 OUTPUT")
                        st.markdown(txt)
            else:
                st.error("Topic Required.")

elif nav == "💼 Client Pitcher":
    st.markdown("<h1 style='color: #00d4ff;'>💼 VOID CAPITAL: PITCH GENERATOR</h1>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 1.5], gap="large")
    
    with c1:
        client_name = st.text_input("Lead / Brand Name")
        niche_cat = st.selectbox("Category", ["Personal Brand", "B2B Technical", "Fashion", "Hospitality", "Local Business"])
        offer_details = st.text_area("Value Proposition (What are we selling?)", placeholder="e.g., Short-form growth, 30 videos/month, lead-gen backend")
        
        if st.button("🔥 Generate VOID Pitch"):
            if client_name and offer_details:
                with st.spinner("🌑 ACCESSING GROQ INTELLIGENCE..."):
                    groq_c = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    prompt = f"System: You are VOID OS Director. Write a professional yet 'black-label' elite pitch for {client_name} in the {niche_cat} niche. Offer: {offer_details}. Use a tone of scarcity and high-authority."
                    res = groq_c.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                    pitch_res = res.choices[0].message.content
                    
                    st.session_state.pitch_history.append({
                        "time": time.strftime("%H:%M:%S"),
                        "client": client_name,
                        "pitch": pitch_res
                    })
                    
                    with c2:
                        st.subheader(f"Strategic Pitch: {client_name}")
                        typewriter_effect(pitch_res)
                        st.divider()
                        st.download_button("Download Pitch as TXT", pitch_res, file_name=f"{client_name}_pitch.txt")
            else:
                st.error("Director, provide a Lead Name and Offer details before architecting.")

# --- NEW SECTOR: CREATOR LAB (VIGOR CALCULATOR) ---
elif nav == "🧬 Creator Lab":
    st.markdown("<h1 style='color: #00d4ff;'>🧬 CREATOR VIGOR AUDIT</h1>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns([1, 1.5])
    with col_a:
        st.subheader("Vigor Input")
        c_name = st.text_input("Creator Name")
        c_views = st.number_input("Avg Views (Last 5 Videos)", min_value=0, value=5000)
        c_subs = st.number_input("Follower Count", min_value=1, value=10000)
        
        if st.button("⚡ Calculate Vigor"):
            score = calculate_vigor(c_views, c_subs)
            with col_b:
                st.metric("VIGOR SCORE", f"{score}/100")
                if score > 80:
                    st.success(f"🔥 **HIGH VIGOR:** {c_name} is viral-prone. Sign immediately.")
                elif score > 50:
                    st.warning("⚖️ **STABLE:** Consistent growth, but needs better hooks.")
                else:
                    st.error("📉 **STAGNANT:** Low organic reach. Proceed with caution.")
                
                # Logic visualization
                st.caption("Director's Logic: We value Attention Leverage. A creator who gets 50k views with 1k followers is a 'Vigor God'.")

# --- REPAIRED MODULE: LEAD SOURCE ---
if nav == "🛰️ Lead Source":
    st.markdown("<h1 style='color: #00ff41;'>🛰️ VOID LEAD SOURCE</h1>", unsafe_allow_html=True)
    st.subheader("Automated Prospecting Layer")
    
    c1, c2 = st.columns([1, 1.5], gap="large")
    
    with c1:
        niche_search = st.selectbox("Target Niche", ["SaaS Founders", "E-commerce Brands", "Real Estate Tech", "High-Ticket Coaches"])
        min_followers = st.slider("Min Followers", 1000, 50000, 5000)
        
        if st.button("Initialize Deep Scan"):
            with st.spinner("📡 SCANNING SOCIAL GRAPHS..."):
                time.sleep(1.5)
                leads_data = [
                    {"Handle": "@NexusCore_AI", "Platform": "IG", "Gap": "No Video Content", "Vigor": "Low"},
                    {"Handle": "@Solaris_SaaS", "Platform": "TikTok", "Gap": "Poor Hooks", "Vigor": "Medium"},
                    {"Handle": "@AlphaCoach_X", "Platform": "Reels", "Gap": "Low Retention", "Vigor": "High"}
                ]
                st.session_state.found_leads = pd.DataFrame(leads_data)
                st.success("Scan Complete. 3 Gaps Identified.")

    with c2:
        if not st.session_state.found_leads.empty:
            st.write("### 🎯 Prospecting Results")
            st.table(st.session_state.found_leads)
            
            selected_lead = st.selectbox("Select Lead for Cold Strike", st.session_state.found_leads["Handle"])
            if st.button("Generate Cold Strike"):
                with st.spinner("🌑 ARCHITECTING..."):
                    groq_c = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    prompt = f"Write a 3-sentence aggressive, high-authority cold DM to {selected_lead} in {niche_search}. Point out their {st.session_state.found_leads.loc[st.session_state.found_leads['Handle']==selected_lead, 'Gap'].values[0]} is losing them money."
                    res = groq_c.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                    strike_text = res.choices[0].message.content
                    st.code(strike_text, language="markdown")
                    st.caption("Copy this for the 'Cold Strike' manual deployment.")
        else:
            st.info("Awaiting system initialization. Run 'Deep Scan' to identify targets.")

# --- UPDATED HISTORY (TO SHOW DNA) ---
elif nav == "📜 History":
    st.title("📜 ARCHIVES")
    for s in reversed(st.session_state.script_history):
        with st.expander(f"{s['assigned_to']} | {s['topic']}"):
            st.write(s['script'])
            if 'dna' in s:
                st.caption(f"🧬 DNA: {s['dna']}")
























