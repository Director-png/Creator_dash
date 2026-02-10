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
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"
FORM_POST_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfnNLb9O-szEzYfYEL85aENIimZFtMd5H3a7o6fX-_6ftU_HA/formResponse"

# --- 2. DATA LOADING ---
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

# --- 3. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = "user"
if 'user_name' not in st.session_state: st.session_state.user_name = ""

# --- 4. AUTH PORTAL ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🛡️ DIRECTOR'S INTELLIGENCE PORTAL</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Login", "📝 Register"])
    with t1:
        email_in = st.text_input("Email").lower().strip()
        pw_in = st.text_input("Password", type="password")
        if st.button("Access System", use_container_width=True):
            users = load_user_db()
            if email_in == "director@void.com" and pw_in == "VOID_LEADER_2026":
                st.session_state.logged_in = True
                st.session_state.user_name = "The Director"
                st.session_state.user_role = "admin"
                st.rerun()
            elif not users.empty:
                match = users[(users.iloc[:, 2].astype(str).str.lower() == email_in) & (users.iloc[:, 4].astype(str) == pw_in)]
                if not match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_name = match.iloc[0, 1]
                    st.session_state.user_role = "user"
                    st.rerun()
            else: st.error("Access Denied.")
    st.stop()

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🌑 VOID OS")
    nav_options = ["Dashboard", "Live Intelligence", "Trend Comparison", "Script Architect"]
    if st.session_state.user_role == "admin":
        nav_options.append("Client Pitcher")
    nav = st.radio("COMMAND CENTER", nav_options)
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- 6. MODULES ---

# MODULE: DASHBOARD (Horizontal Niche Charts)
if nav == "Dashboard":
    st.header("🌑 SYSTEM OVERVIEW")
    data = load_market_data()
    if not data.empty:
        # Pulling top 8 niches for the blue horizontal bars
        fig = px.bar(data.head(8), x=data.columns[1], y=data.columns[0], orientation='h', 
                     title="Niche Momentum Index", color_discrete_sequence=['#00d4ff'])
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("VOID Status", "Active")
    m2.metric("Director Access", "Verified" if st.session_state.user_role == "admin" else "Restricted")
    m3.metric("Network", "Secure")

# MODULE: LIVE INTELLIGENCE (Image Feed)
elif nav == "Live Intelligence":
    st.header("🌐 LIVE INTEL FEED")
    feed = feedparser.parse("https://techcrunch.com/category/artificial-intelligence/feed/")
    for entry in feed.entries[:5]:
        col1, col2 = st.columns([1, 2])
        # Image Logic
        img_url = entry.media_content[0]['url'] if 'media_content' in entry else "https://images.unsplash.com/photo-1614728263952-84ea206f99b6?w=400"
        col1.image(img_url, use_container_width=True)
        col2.subheader(entry.title)
        col2.write(entry.summary[:150] + "...")
        col2.markdown(f"[Deploy Intel]({entry.link})")
        st.divider()

# MODULE: TREND COMPARISON (Charts & Performance Table)
elif nav == "Trend Comparison":
    st.header("📊 KEYWORD GROWTH & ANALYSIS")
    trend_df = pd.DataFrame({
        'Keyword': ['AI Automation', 'UGC', 'SaaS', 'Ghostwriting', 'Short-form'],
        'Growth': [95, 88, 72, 65, 91],
        'YT Performance': ['Viral', 'High', 'Medium', 'High', 'Viral'],
        'IG Performance': ['High', 'Viral', 'Low', 'Medium', 'Viral'],
        'Pros': ['High Margin', 'Easy Sale', 'Passive', 'High Demand', 'Massive Reach'],
        'Cons': ['Tech Complexity', 'Ad Spend', 'Churn', 'Burnout', 'Retention']
    })
    
    fig = px.line(trend_df, x='Keyword', y='Growth', markers=True, title="Recent Growth Trajectory (%)")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Performance Breakdown")
    st.table(trend_df)

# MODULE: SCRIPT ARCHITECT (Multi-Platform + Meter)
elif nav == "Script Architect":
    st.header("💎 SCRIPT ARCHITECT")
    colA, colB = st.columns(2)
    with colA:
        platform = st.selectbox("Platform", ["YouTube", "Instagram Reels", "Threads", "LinkedIn"])
        topic = st.text_input("Topic/Keyword")
    with colB:
        tone = st.select_slider("Intensity Meter", options=["Minimalist", "Engaging", "High-Energy", "Aggressive"])
    
    if st.button("Architect Script"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        prompt = f"Generate a {tone} {platform} script about {topic}. Focus on retention and hook strength."
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}])
        st.success(f"{platform} Script Ready")
        st.markdown(res.choices[0].message.content)

# MODULE: CLIENT PITCHER (Admin Only)
elif nav == "Client Pitcher":
    st.header("💼 DIRECTOR'S PITCH VAULT")
    c_name = st.text_input("Client Name")
    offer = st.text_area("The Offer")
    if st.button("Generate Pitch"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        prompt = f"Write a world-class cold pitch to {c_name} regarding {offer}. Keep it sharp and elite."
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}])
        st.info(res.choices[0].message.content)
