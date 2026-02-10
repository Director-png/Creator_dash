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

# --- 4. AUTH GATEKEEPER ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🛡️ DIRECTOR'S INTELLIGENCE PORTAL</h1>", unsafe_allow_html=True)
    email_in = st.text_input("Email").lower().strip()
    pw_in = st.text_input("Password", type="password")
    if st.button("Access System", use_container_width=True):
        if (email_in == "admin" and pw_in == "1234") or (email_in == "director@void.com" and pw_in == "VOID_2026"):
            st.session_state.logged_in = True
            st.session_state.user_role = "admin"
            st.rerun()
        else:
            users = load_user_db()
            if not users.empty:
                match = users[(users.iloc[:, 2].astype(str).str.lower() == email_in) & (users.iloc[:, 4].astype(str) == pw_in)]
                if not match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_role = "user"
                    st.rerun()
            else: st.error("Database connection failure.")
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🌑 VOID OS")
    nav_items = ["Dashboard", "Global Pulse", "Trend Comparison", "Script Architect"]
    if st.session_state.user_role == "admin":
        nav_items.append("Client Pitcher")
    nav = st.radio("COMMAND", nav_items)
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- 6. MODULES ---

if nav == "Dashboard":
    st.title("🌑 COMMANDER'S HUB")
    st.write("System online. Intelligence gathering active.")

elif nav == "Global Pulse":
    st.title("🌐 GLOBAL PULSE")
    
    # CHARTS: Horizontal Niche Momentum
    data = load_market_data()
    if not data.empty:
        st.subheader("📊 Niche Momentum Index")
        # Ensure we are plotting Niche vs Growth/Value
        fig = px.bar(data.head(8), x=data.columns[1], y=data.columns[0], orientation='h', 
                     color_discrete_sequence=['#00d4ff'])
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # LIVE INTEL FEED: With Image Fix
    st.subheader("📰 Live Intelligence Feed")
    feed = feedparser.parse("https://techcrunch.com/category/artificial-intelligence/feed/")
    for entry in feed.entries[:5]:
        col1, col2 = st.columns([1, 2])
        # Image Extraction Logic
        img = "https://images.unsplash.com/photo-1614728263952-84ea206f99b6?w=400" # Default VOID Style
        if 'media_content' in entry: img = entry.media_content[0]['url']
        elif 'media_thumbnail' in entry: img = entry.media_thumbnail[0]['url']
        
        col1.image(img, use_container_width=True)
        col2.subheader(entry.title)
        col2.write(entry.summary[:160] + "...")
        col2.markdown(f"[Deploy Intel]({entry.link})")
        st.write("---")

elif nav == "Trend Comparison":
    st.title("📊 KEYWORD GROWTH")
    # Simulation table for YouTube/IG performance
    trend_df = pd.DataFrame({
        'Keyword': ['AI Agents', 'Short-form SaaS', 'UGC Ads', 'Newsletter Alpha'],
        'Growth': [94, 82, 77, 65],
        'YT Performance': ['Viral', 'High', 'Medium', 'High'],
        'IG Performance': ['High', 'Viral', 'Viral', 'Medium'],
        'Pros': ['High Moat', 'Recurring', 'Quick Cash', 'Asset Ownership'],
        'Cons': ['Complex', 'Churn', 'Burnout', 'Slow Build']
    })
    st.plotly_chart(px.line(trend_df, x='Keyword', y='Growth', markers=True), use_container_width=True)
    st.table(trend_df)

elif nav == "Script Architect":
    st.title("💎 SCRIPT ARCHITECT")
    platform = st.selectbox("Platform", ["YouTube", "Instagram Reels", "Threads", "LinkedIn"])
    tone = st.select_slider("Intensity", ["Minimal", "Engaging", "High-Energy", "Aggressive"])
    topic = st.text_input("Topic")
    if st.button("Architect Plan"):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            res = client.chat.completions.create(model="llama-3.1-8b-instant", 
                                                 messages=[{"role":"user","content":f"Write a {tone} {platform} script for {topic}"}])
            st.markdown(res.choices[0].message.content)
        except Exception as e: st.error(f"Groq Offline: {e}")

elif nav == "Client Pitcher":
    st.title("💼 DIRECTOR'S PITCH VAULT")
    c_name = st.text_input("Client Name")
    offer = st.text_area("The Offer")
    if st.button("Generate Pitch"):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            res = client.chat.completions.create(model="llama-3.1-8b-instant", 
                                                 messages=[{"role":"user","content":f"Draft an elite cold pitch to {c_name} regarding {offer}"}])
            st.info(res.choices[0].message.content)
        except Exception as e: st.error(f"Error: {e}")
