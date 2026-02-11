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
# Replace YOUR_SHEET_ID with your actual ID from the URL
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?gid=989182688&single=true&output=csv"
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

# --- 1. REFINED SYNC FUNCTION ---
def load_user_db():
    try:
        # Force fresh data from the CSV link
        sync_url = f"{USER_DB_URL}&cache_bus={time.time()}"
        df = pd.read_csv(sync_url)
        
        if df.empty:
            return pd.DataFrame()
            
        # Standardize headers to lowercase to avoid "Name" vs "name" issues
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        st.sidebar.error(f"Sync Failure: {e}")
        return pd.DataFrame()

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
# --- 2. THE DROPDOWN LOGIC (WITH PROBE) ---
if nav == "💎 Script Architect":
    st.markdown("<h1 style='color: #00ff41;'>⚔️ TACTICAL ARCHITECT</h1>", unsafe_allow_html=True)
    
    users_df = load_user_db()
    
    # --- THE DEEP PROBE (Temporary) ---
    st.write("### 🔍 SYSTEM DIAGNOSTIC")
    if users_df.empty:
        st.error("❌ The Database is returning ZERO rows. Check if the 'Publish to Web' link is still active.")
    else:
        st.success(f"✅ Connection Stable. Found Columns: {list(users_df.columns)}")
        # This shows you the first 3 names found in the sheet
        st.write("Sample Data Found:", users_df.head(3)) 

    # --- CLIENT LIST LOGIC ---
    client_options = ["Public/General"]
    if not users_df.empty:
        # We try to find the 'name' column automatically
        name_col = [c for c in users_df.columns if 'name' in c]
        if name_col:
            db_names = users_df[name_col[0]].dropna().unique().tolist()
            client_options = ["Public/General"] + db_names
        else:
            # If 'name' isn't found, we grab the 2nd column (Index 1)
            db_names = users_df.iloc[:, 1].dropna().unique().tolist()
            client_options = ["Public/General"] + db_names

    # THE UI
    target_client = st.selectbox("Assign To Target", options=client_options, key="architect_target")


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
    st.title("⚔️ TREND DUEL")
    # [Trend Duel Code Preserved...]
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
            

if nav == "💎 Script Architect":
    st.markdown("<h1 style='color: #00ff41;'>⚔️ TACTICAL ARCHITECT</h1>", unsafe_allow_html=True)
    
    # 1. DATA PULL
    users_df = load_user_db()
    
    if not users_df.empty:
        st.success(f"📡 CONNECTION STABLE: {len(users_df)} Clients Synced.")
    else:
        st.warning("⚠️ Using local mode (Public/General). Database sync pending.")

    # 2. CLIENT LIST LOGIC
    client_options = ["Public/General"]
    if not users_df.empty:
        # Grabbing names from Column 2 (Index 1)
        db_names = users_df.iloc[:, 1].dropna().unique().tolist()
        client_options = ["Public/General"] + db_names

    # 3. THE UI ELEMENTS (FORCED TO APPEAR)
    c1, c2 = st.columns([1, 1.5], gap="large")
    
    with c1:
        # --- INPUT 1: CLIENT ---
        target_client = st.selectbox("Assign To Target", options=client_options, key="arch_target_final")
        
        # --- INPUT 2: PLATFORM ---
        platform = st.selectbox("Platform", ["Instagram Reels", "YouTube Shorts", "TikTok", "YouTube Long-form"], key="arch_plat_final")
        
        # --- INPUT 3: TOPIC ---
        topic = st.text_input("Core Topic", placeholder="e.g., The Future of AI in 2026", key="arch_topic_final")
        
        # --- INPUT 4: SLIDER ---
        tone_choice = st.select_slider("Vigor/Tone", ["Professional", "Aggressive", "Elite"], key="arch_tone_final")
        
        # --- INPUT 5: COMPETITOR LOGIC ---
        with st.expander("👤 COMPETITOR SHADOW"):
            c_hook = st.text_area("Their Narrative", key="arch_hook_final")
# --- THE EXECUTION BUTTON ---
        if st.button("🚀 ARCHITECT & TRANSMIT", use_container_width=True):
            if not topic:
                st.error("Director, the Topic field cannot be empty.")
            else:
                with st.spinner("🌑 ARCHITECTING..."):
                    try:
                        # 1. INITIALIZE GROQ
                        groq_c = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        
                        # 2. CRAFT THE PROMPT
                        prompt = f"""
                        System: VOID OS Content Architect.
                        Platform: {platform}
                        Topic: {topic}
                        Tone: {tone_choice}
                        Competitor Angle: {c_hook if c_hook else 'None'}
                        
                        Task: Write a high-retention script with a 1-second hook.
                        """
                        
                        # 3. CALL THE MODEL
                        res = groq_c.chat.completions.create(
                            model="llama-3.3-70b-versatile", 
                            messages=[{"role": "user", "content": prompt}]
                        )
                        
                        txt = res.choices[0].message.content
                        dna_profile = generate_visual_dna(platform, tone_choice)
                        
                        # 4. TRANSMIT TO DATABASE
                        transmit_status = transmit_script(target_client, platform, topic, txt, dna_profile)
                        
                        # 5. DISPLAY RESULTS IN THE SECOND COLUMN
                        with c2:
                            st.subheader("💎 GENERATED ARCHIVE")
                            st.markdown(txt)
                            st.divider()
                            st.caption(f"🧬 DNA: {dna_profile}")
                            if transmit_status:
                                st.success("⚔️ BROADCAST COMPLETE: Script synced to Vault.")
                            else:
                                st.warning("⚠️ Script generated, but Transmission failed.")
                                
                    except Exception as e:
                        st.error(f"Intelligence Failure: {e}")

elif nav == "💼 Client Pitcher":
    st.markdown("<h1 style='color: #00d4ff;'>💼 VOID CAPITAL</h1>", unsafe_allow_html=True)
    # [Pitcher Code Preserved...]
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
                
elif nav == "🧬 Creator Lab":
    st.markdown("<h1 style='color: #00d4ff;'>🧬 VIGOR AUDIT</h1>", unsafe_allow_html=True)
    # [Vigor Code Preserved...]
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

elif nav == "🛰️ Lead Source":
    st.markdown("<h1 style='color: #00ff41;'>🛰️ LEAD SOURCE</h1>", unsafe_allow_html=True)
    # [Lead Source Code Preserved...]
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

elif nav == "📜 History":
    st.title("📜 ARCHIVES")
    # [History Code Preserved...]
    for s in reversed(st.session_state.script_history):
        with st.expander(f"{s['assigned_to']} | {s['topic']}"):
            st.write(s['script'])
            if 'dna' in s:
                st.caption(f"🧬 DNA: {s['dna']}")












