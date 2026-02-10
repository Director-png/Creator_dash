import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
import feedparser

# --- 1. CONFIG & CONNECTIONS ---
st.set_page_config(page_title="VOID OS", page_icon="🌑", layout="wide")

MARKET_URL = "https://docs.google.com/spreadsheets/d/163haIuPIna3pEY9IDxncPM2kFFsuZ76HfKsULcMu1y4/export?format=csv"
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"

# --- 2. DATA LOADING ---
@st.cache_data(ttl=600)
def load_market_data():
    try:
        df = pd.read_csv(MARKET_URL)
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        return df
    except: return pd.DataFrame()

def load_user_db():
    try:
        df = pd.read_csv(USER_DB_URL)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except: return pd.DataFrame()

# --- 3. MASTER SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = "user"
if 'user_name' not in st.session_state: st.session_state.user_name = "Operator"

# --- 4. AUTH PORTAL ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🛡️ DIRECTOR'S INTELLIGENCE PORTAL</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Login", "📝 Register"])
    with t1:
        email_in = st.text_input("Email").lower().strip()
        pw_in = st.text_input("Password", type="password")
        if st.button("Access System", use_container_width=True):
            if (email_in == "admin" and pw_in == "1234") or (email_in == "director@void.com" and pw_in == "VOID_2026"):
                st.session_state.update({"logged_in": True, "user_role": "admin", "user_name": "The Director"})
                st.rerun()
            else:
                users = load_user_db()
                if not users.empty:
                    match = users[(users.iloc[:, 2].astype(str).str.lower() == email_in) & (users.iloc[:, 4].astype(str) == pw_in)]
                    if not match.empty:
                        st.session_state.update({"logged_in": True, "user_name": match.iloc[0, 1], "user_role": "user"})
                        st.rerun()
                else: st.error("Database Connection Failure.")
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #00d4ff;'>🌑 VOID OS</h1>", unsafe_allow_html=True)
    st.write(f"● **ONLINE:** {st.session_state.user_name.upper()}")
    st.divider()
    nav = st.radio("SELECT MODULE", ["📊 Dashboard", "🌐 Global Pulse", "⚔️ Trend Duel", "💎 Script Architect"] + (["💼 Client Pitcher"] if st.session_state.user_role == "admin" else []))
    if st.button("🔓 Terminate Session"):
        st.session_state.logged_in = False
        st.rerun()

# --- 6. MODULES ---
def style_plot(fig):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", 
        paper_bgcolor="rgba(0,0,0,0)", 
        font_color="white",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

if nav == "📊 Dashboard":
    st.header("🌑 SYSTEM OVERVIEW")
    data = load_market_data()
    if not data.empty:
        fig = px.bar(data.head(8), x=data.columns[1], y=data.columns[0], orientation='h', title="Niche Momentum Index", color_discrete_sequence=['#00d4ff'])
        st.plotly_chart(style_plot(fig), use_container_width=True)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("VOID Status", "Active")
    m2.metric("Director Access", "Verified" if st.session_state.user_role == "admin" else "Restricted")
    m3.metric("Network", "Secure")

elif nav == "🌐 Global Pulse":
    st.title("🌐 GLOBAL PULSE")
    feed = feedparser.parse("https://techcrunch.com/category/artificial-intelligence/feed/")
    for entry in feed.entries[:5]:
        with st.container():
            st.subheader(entry.title)
            st.write(entry.summary[:200] + "...")
            st.markdown(f"[Deploy Intel]({entry.link})")
            st.divider()

elif nav == "⚔️ Trend Duel":
    st.title("📊 TREND INTELLIGENCE")
    trend_data = {'Rank': ['#01', '#02', '#03'], 'Keyword': ['AI Agents', 'Short-form SaaS', 'UGC Ads'], 'Growth': [94, 82, 77]}
    df = pd.DataFrame(trend_data)
    kw1 = st.selectbox("Compare", df['Keyword'].unique())
    st.table(df[df['Keyword'] == kw1])

elif nav == "💎 Script Architect":
    st.header("💎 SCRIPT ARCHITECT")
    topic = st.text_input("Topic")
    if st.button("Architect Script") and topic:
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":f"Write a script about {topic}"}])
            st.markdown(res.choices[0].message.content)
        except Exception as e: st.error(f"API Error: {e}")

elif nav == "💼 Client Pitcher":
    st.header("💼 DIRECTOR'S PITCH VAULT")
    offer = st.text_area("The Offer")
    if st.button("Generate Pitch"): st.info("Drafting elite outreach...")
