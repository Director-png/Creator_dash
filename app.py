import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
import requests
import feedparser

# --- 1. CONFIG & CONNECTIONS ---
st.set_page_config(page_title="VOID OS", page_icon="🌑", layout="wide")

MARKET_URL = "https://docs.google.com/spreadsheets/d/163haIuPIna3pEY9IDxncPM2kFFsuZ76HfKsULcMu1y4/export?format=csv"
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"
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

# --- 4. THE GATEKEEPER ---
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

# --- 5. SIDEBAR COMMAND CONSOLE ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #00d4ff; margin-bottom: 0;'>🌑 VOID OS</h1>", unsafe_allow_html=True)
    user_display = st.session_state.get('user_name', 'Operator')
    st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'><p style='color: #00ff41; font-family: monospace;'>● ONLINE: {user_display.upper()}</p></div>", unsafe_allow_html=True)
    
    st.divider()
    nav_map = {
        "📊 Dashboard": "Dashboard",
        "🌐 Global Pulse": "Global Pulse",
        "⚔️ Trend Duel": "Trend Comparison",
        "💎 Script Architect": "Script Architect"
    }
    if st.session_state.user_role == "admin":
        nav_map["💼 Client Pitcher"] = "Client Pitcher"

    selection = st.radio("SELECT MODULE", list(nav_map.keys()))
    nav = nav_map[selection]

    if st.button("🔓 Terminate Session", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- 6. CORE LOGIC & MODULES ---

if nav == "Dashboard":
    st.title("🌑 VOID COMMAND CENTER")
    # Customization Logic
    with st.expander("🛠️ Customize Dashboard"):
        st.session_state.metric_1_label = st.text_input("Metric 1 Label", st.session_state.metric_1_label)
        st.session_state.metric_1_val = st.text_input("Metric 1 Value", st.session_state.metric_1_val)
        st.session_state.daily_directive = st.text_area("Edit Directive", st.session_state.daily_directive)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(st.session_state.metric_1_label, st.session_state.metric_1_val)
    m2.metric("Scripts Ready", "24", "+6")
    m3.metric("Leads", "3", "Target: 10")
    m4.metric("Status", "Operational")

    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.subheader("🚀 Roadmap")
        df_road = pd.DataFrame({
            "Phase": ["VOID Intelligence", "Script Architect", "Client Pitcher"],
            "Status": ["Stable", "Stable", "Online"]
        })
        st.table(df_road)
    with col_r:
        st.subheader("💡 Directive")
        st.info(st.session_state.daily_directive)

elif nav == "Global Pulse":
    st.title("🌐 GLOBAL INTELLIGENCE PULSE")
    data = load_market_data()
    if not data.empty:
        fig = px.treemap(data.head(15), path=[data.columns[0]], values=data.columns[1], color=data.columns[1], template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    
    col_news, col_analysis = st.columns([2, 1])
    with col_news:
        st.subheader("📰 Live Tech Intelligence")
        feed = feedparser.parse("https://techcrunch.com/category/artificial-intelligence/feed/")
        for entry in feed.entries[:5]:
            st.markdown(f"**{entry.title}**")
            st.write(entry.summary[:150] + "...")
            st.markdown(f"[Intel Link]({entry.link})")
            st.divider()
    with col_analysis:
        st.warning("Director's Note: Focus on Agentic Workflows.")
        st.image("https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400")

elif nav == "Trend Comparison":
    st.title("⚔️ TREND DUEL ENGINE")
    trend_data = {
        'Keyword': ['AI Agents', 'Short-form SaaS', 'UGC Ads', 'Newsletter Alpha', 'Faceless YT', 'High-Ticket DM'],
        'Growth': [94, 82, 77, 65, 89, 72],
        'Saturation': [20, 45, 80, 30, 60, 50],
        'YT_Potential': [95, 80, 60, 85, 98, 40],
        'IG_Potential': [88, 92, 95, 70, 85, 90]
    }
    df = pd.DataFrame(trend_data)
    kw1 = st.selectbox("Primary Keyword", df['Keyword'].unique(), index=0)
    kw2 = st.selectbox("Challenger Keyword", df['Keyword'].unique(), index=1)
    
    d1 = df[df['Keyword'] == kw1].iloc[0]
    d2 = df[df['Keyword'] == kw2].iloc[0]
    
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.bar(x=['Growth', 'Saturation', 'YT Pot', 'IG Pot'], y=[d1[1], d1[2], d1[3], d1[4]], title=kw1), use_container_width=True)
    with c2:
        st.plotly_chart(px.bar(x=['Growth', 'Saturation', 'YT Pot', 'IG Pot'], y=[d2[1], d2[2], d2[3], d2[4]], title=kw2), use_container_width=True)

elif nav == "Client Pitcher":
    st.title("💼 VOID CAPITAL: PITCH GENERATOR")
    c_name = st.text_input("Business Name")
    offer = st.text_area("What are you selling?")
    if st.button("Generate Pitch") and c_name:
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": f"Write a cold DM for {c_name}. Offer: {offer}"}]
            )
            st.success(res.choices[0].message.content)
        except Exception as e:
            st.error(f"Error: {e}")

elif nav == "Script Architect":
    st.title("✍️ VOID SCRIPT ARCHITECT")
    topic = st.text_input("Focus Topic")
    platform = st.selectbox("Platform", ["YouTube Shorts", "Instagram Reels", "Long-form"])
    if st.button("🚀 Architect Script") and topic:
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": f"Write a {platform} script about {topic} using the VOID framework."}]
            )
            st.markdown(res.choices[0].message.content)
        except Exception as e:
            st.error(f"Error: {e}")
