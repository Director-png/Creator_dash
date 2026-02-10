import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
import requests
import feedparser

# --- 1. CONFIG & CONNECTIONS ---
st.set_page_config(page_title="VOID OS", page_icon="🌑", layout="wide")

# Market Data URL
MARKET_URL = "https://docs.google.com/spreadsheets/d/163haIuPIna3pEY9IDxncPM2kFFsuZ76HfKsULcMu1y4/export?format=csv"

# User Database (Form Responses CSV)
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"

# Google Form Submission Link
FORM_POST_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfnNLb9O-szEzYfYEL85aENIimZFtMd5H3a7o6fX-_6ftU_HA/formResponse"

# --- 2. DATA LOADING FUNCTIONS ---
def load_market_data():
    try:
        df = pd.read_csv(MARKET_URL)
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

def load_user_db():
    try:
        df = pd.read_csv(USER_DB_URL)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# --- 3. SESSION STATE INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'user_role' not in st.session_state:
    st.session_state.user_role = "user"
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'metric_1_label' not in st.session_state:
    st.session_state.metric_1_label = "Market Volatility"
if 'metric_1_val' not in st.session_state:
    st.session_state.metric_1_val = "High"
if 'daily_directive' not in st.session_state:
    st.session_state.daily_directive = "1. Code VOID OS\n2. Draft 3 Scripts\n3. 1 Client Lead\n4. Word is Law"

# --- 4. THE GATEKEEPER (LOGIN & REGISTRATION) ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🛡️ DIRECTOR'S INTELLIGENCE PORTAL</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Login", "📝 Register"])

    with t1:
        col_l, col_mid, col_r = st.columns([1, 2, 1])
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
                    # Column mapping based on your form index
                    # 0:Timestamp, 1:Name, 2:Email, 3:Niche, 4:Password
                    match = users[(users.iloc[:, 2].astype(str).str.lower() == email_in) & (users.iloc[:, 4].astype(str) == pw_in)]
                    if not match.empty:
                        st.session_state.logged_in = True
                        st.session_state.user_name = match.iloc[0, 1]
                        st.session_state.user_email = email_in
                        niche_val = str(match.iloc[0, 3]).lower()
                        st.session_state.user_role = "admin" if "fitness" in niche_val or "admin" in niche_val else "user"
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
                else:
                    st.error("Database connecting... Use admin login.")

    with t2:
        col_l, col_mid, col_r = st.columns([1, 2, 1])
        with col_mid:
            with st.form("reg_form"):
                name = st.text_input("Name")
                email = st.text_input("Email")
                niche = st.text_input("Niche (Focus Area)")
                pw = st.text_input("Set Password", type="password")
                if st.form_submit_button("Submit Registration"):
                    payload = {
                        "entry.483203499": name,
                        "entry.1873870532": email,
                        "entry.1906780868": niche,
                        "entry.1396549807": pw
                    }
                    try:
                        requests.post(FORM_POST_URL, data=payload)
                        st.success("Registration transmitted! Wait 60s for sync.")
                    except:
                        st.error("Transmission failed.")
    st.stop()

# --- 5. ENHANCED SIDEBAR COMMAND CONSOLE ---
with st.sidebar:
    # System Identity
    st.markdown("<h1 style='text-align: center; color: #00d4ff; margin-bottom: 0;'>🌑 VOID OS</h1>", unsafe_allow_html=True)
    
    # Dynamic User Identity
    user_display = st.session_state.get('user_name', 'Operator')
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 20px;'>
            <p style='color: #00ff41; font-family: monospace; font-size: 0.9em; margin: 0;'>
                ● ONLINE: {user_display.upper()}
            </p>
            <p style='color: gray; font-size: 0.7em; margin: 0;'>ACCESS LEVEL: {st.session_state.user_role.upper()}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    # System Status Readout
    with st.expander("📡 SYSTEM STATUS", expanded=False):
        st.write("🟢 Core: Operational")
        st.write("🔵 Intel: Synchronized")
        st.write("🔒 Security: Level 5")
    
    st.divider()

    # Navigation with Icons
    st.subheader("🛠️ COMMANDS")
    nav_map = {
        "📊 Dashboard": "Dashboard",
        "🌐 Global Pulse": "Global Pulse",
        "⚔️ Trend Duel": "Trend Comparison",
        "💎 Script Architect": "Script Architect"
    }
    
    if st.session_state.user_role == "admin":
        nav_map["💼 Client Pitcher"] = "Client Pitcher"

    selection = st.radio("SELECT MODULE", list(nav_map.keys()), label_visibility="collapsed")
    nav = nav_map[selection]

    st.divider()

    # Quick Intelligence Actions
    st.subheader("⚡ QUICK ACTIONS")
    if st.button("🔄 Force Data Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    if st.button("📤 Export Intel Report", use_container_width=True):
        st.toast(f"Generating {user_display}'s Report...", icon="📄")

    st.sidebar.markdown("---")
    if st.button("🔓 Terminate Session", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
        

# --- MODULE: DASHBOARD (CUSTOMIZABLE) ---
if nav == "Dashboard":
    st.markdown("<h1 style='color: white;'>🌑 VOID COMMAND CENTER</h1>", unsafe_allow_html=True)
    
    # --- CUSTOMIZATION DRAWER ---
    with st.expander("🛠️ Customize Dashboard Layout"):
        col_edit1, col_edit2 = st.columns(2)
        st.session_state.metric_1_label = col_edit1.text_input("Metric 1 Label", st.session_state.metric_1_label)
        st.session_state.metric_1_val = col_edit1.text_input("Metric 1 Value", st.session_state.metric_1_val)
        st.session_state.daily_directive = col_edit2.text_area("Edit Daily Directive", st.session_state.daily_directive)

    st.divider()

    # TOP ROW: METRICS (Using Custom State)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label=st.session_state.metric_1_label, value=st.session_state.metric_1_val)
    m2.metric(label="Scripts Ready", value="24", delta="+6")
    m3.metric(label="Agency Leads", value="3", delta="Target: 10")
    m4.metric(label="System Status", value="Operational")

    st.markdown("---")

    # MIDDLE ROW
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader("🚀 Active VOID Roadmap")
        roadmap_data = {
            "Phase": ["VOID Intelligence", "Script Architect", "Client Pitcher", "Agency Portal"],
            "Status": ["Stable", "Stable", "Online", "Planned"],
            "Priority": ["Completed", "Active", "High", "Critical"]
        }
        df_road = pd.DataFrame(roadmap_data)
        df_road.index = df_road.index + 1
        st.table(df_road)

    with col_right:
        st.subheader("💡 Daily Directive")
        st.info(st.session_state.daily_directive)
        st.write("Grind Completion")
        st.progress(45)

# --- MODULE: CLIENT PITCHER (VOID CAPITAL) ---
elif nav == "Client Pitcher":
    st.markdown("<h1 style='color: #000080;'>💼 VOID CAPITAL: PITCH GENERATOR</h1>", unsafe_allow_html=True)
    st.caption("Closing high-ticket clients with AI precision.")

    c1, c2 = st.columns([1, 1.5])
    with c1:
        client_name = st.text_input("Business Name")
        niche = st.selectbox("Niche", ["Real Estate", "E-commerce", "SaaS", "Local Business"])
        offer = st.text_area("What are you selling?", placeholder="e.g., Short-form video growth packages")
        pitch_btn = st.button("🔥 Generate Power Pitch")

    with c2:
        if pitch_btn and client_name:
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                prompt = f"Write a high-converting, professional cold DM for {client_name} in the {niche} niche. Our offer: {offer}. Tone: Confident, minimalist, and value-driven. No fluff."
                
                with st.spinner("Crafting..."):
                    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                    st.markdown("### The Pitch")
                    st.write(res.choices[0].message.content)
            except Exception as e:
                st.error(f"Sync Error: {e}")
elif nav == "Global Pulse":
    st.header("🌐 GLOBAL INTELLIGENCE")
    feed = feedparser.parse("https://techcrunch.com/category/artificial-intelligence/feed/")
    for entry in feed.entries[:3]:
        st.subheader(entry.title)
        st.write(entry.summary[:150] + "...")
        st.markdown(f"[Intel Link]({entry.link})")
        st.divider()

elif nav == "Script Architect":
    st.header("💎 SCRIPT ARCHITECT")
    topic = st.text_input("Core Topic")
    if st.button("Generate") and topic:
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            chat = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":f"Short script: {topic}"}])
            st.write(chat.choices[0].message.content)
        except Exception as e: st.error(f"Error: {e}")



