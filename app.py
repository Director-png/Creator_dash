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

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title(f"🌑 VOID OS")
    st.write(f"**Director:** {st.session_state.user_name}")
    st.divider()
    
    nav_options = ["Dashboard", "Global Pulse", "Script Architect"]
    if st.session_state.user_role == "admin":
        nav_options.append("Client Pitcher")
    
    nav = st.radio("COMMAND CENTER", nav_options)
    st.divider()
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- 6. MODULES ---

# MODULE: DASHBOARD
if nav == "Dashboard":
    st.title("🌑 VOID COMMAND CENTER")
    with st.expander("🛠️ Customize Dashboard"):
        st.session_state.metric_1_label = st.text_input("Metric 1 Label", st.session_state.metric_1_label)
        st.session_state.metric_1_val = st.text_input("Metric 1 Value", st.session_state.metric_1_val)
        st.session_state.daily_directive = st.text_area("Edit Daily Directive", st.session_state.daily_directive)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(st.session_state.metric_1_label, st.session_state.metric_1_val)
    m2.metric("System", "Operational")
    m3.metric("Role", st.session_state.user_role.upper())
    m4.metric("Database", "Synced")

    st.divider()
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.subheader("🚀 Active VOID Roadmap")
        roadmap = pd.DataFrame({
            "Phase": ["Intelligence", "Architect", "Pitcher", "Agency"],
            "Status": ["Stable", "Stable", "Online", "Planned"]
        })
        roadmap.index += 1
        st.table(roadmap)
    with col_r:
        st.subheader("💡 Daily Directive")
        st.info(st.session_state.daily_directive)

# MODULE: GLOBAL PULSE
elif nav == "Global Pulse":
    st.header("📈 Market Momentum")
    feed = feedparser.parse("https://techcrunch.com/feed/")
    if feed.entries:
        cols = st.columns(3)
        for i, entry in enumerate(feed.entries[:3]):
            with cols[i]:
                st.info(f"**{entry.title}**")
                st.markdown(f"[Read Intel]({entry.link})")
    
    st.divider()
    market_data = load_market_data()
    if not market_data.empty:
        fig = px.area(market_data, x=market_data.columns[0], y=market_data.columns[1], template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(market_data, use_container_width=True)

# MODULE: SCRIPT ARCHITECT
elif nav == "Script Architect":
    st.header("💎 Script Architect")
    topic = st.text_input("Video Topic")
    type_f = st.radio("Format", ["Short-Form", "Long-Form"])
    if st.button("Architect Script"):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            prompt = f"Create a viral {type_f} script for: {topic}"
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}])
            st.markdown(res.choices[0].message.content)
        except Exception as e:
            st.error(f"Error: {e}")

# MODULE: CLIENT PITCHER (ADMIN ONLY)
elif nav == "Client Pitcher" and st.session_state.user_role == "admin":
    st.header("💼 VOID CAPITAL: PITCH GENERATOR")
    c_name = st.text_input("Client Business Name")
    offer = st.text_area("Your Offer")
    if st.button("Generate Pitch"):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            prompt = f"Write a cold DM for {c_name} about {offer}. Minimalist and powerful."
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}])
            st.write(res.choices[0].message.content)
        except Exception as e:
            st.error(f"Error: {e}")
