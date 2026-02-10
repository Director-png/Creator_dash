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
        if email_in == "director@void.com" and pw_in == "VOID_2026":
            st.session_state.logged_in = True
            st.session_state.user_role = "admin"
            st.rerun()
        else:
            users = load_user_db()
            match = users[(users.iloc[:, 2].astype(str).str.lower() == email_in) & (users.iloc[:, 4].astype(str) == pw_in)]
            if not match.empty:
                st.session_state.logged_in = True
                st.session_state.user_role = "user"
                st.rerun()
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🌑 VOID OS")
    nav = st.radio("COMMAND", ["Dashboard", "Global Pulse", "Trend Comparison", "Script Architect"] + (["Client Pitcher"] if st.session_state.user_role == "admin" else []))

# --- 6. MODULES ---

if nav == "Dashboard":
    st.title("🌑 COMMANDER'S HUB")
    st.info("System operational. Navigate to Global Pulse for live intelligence.")

elif nav == "Global Pulse":
    st.title("🌐 GLOBAL PULSE & INTEL")
    
    # PART 1: THE CHARTS (Horizontal Blue Bars)
    st.subheader("📈 Niche Momentum Index")
    data = load_market_data()
    if not data.empty:
        fig = px.bar(data.head(8), x=data.columns[1], y=data.columns[0], orientation='h', 
                     color_discrete_sequence=['#00d4ff'])
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # PART 2: LIVE INTELLIGENCE FEED (With Live Images)
    st.subheader("📰 Live Intelligence Feed")
    feed = feedparser.parse("https://techcrunch.com/category/artificial-intelligence/feed/")
    
    for entry in feed.entries[:6]:
        with st.container():
            c1, c2 = st.columns([1, 2])
            
            # Robust Image Extraction Logic
            img_url = ""
            if 'media_thumbnail' in entry and entry.media_thumbnail:
                img_url = entry.media_thumbnail[0]['url']
            elif 'media_content' in entry and entry.media_content:
                img_url = entry.media_content[0]['url']
            elif 'links' in entry:
                for link in entry.links:
                    if 'image' in link.get('type', ''):
                        img_url = link.get('href', '')
            
            # Final Fallback to prevent "Crashed" look
            if not img_url:
                img_url = f"https://source.unsplash.com/400x250/?technology,cyberpunk,{entry.title[:10]}"
            
            c1.image(img_url, use_container_width=True)
            c2.subheader(entry.title)
            c2.write(entry.summary[:180] + "...")
            c2.markdown(f"[Deploy Intel]({entry.link})")
            st.write("---")

elif nav == "Trend Comparison":
    st.title("📊 KEYWORD GROWTH")
    # Trend line and comparison table here as per previous logic...
    trend_df = pd.DataFrame({'Keyword':['AI', 'SaaS', 'UGC'], 'Growth':[90, 70, 85]})
    st.plotly_chart(px.line(trend_df, x='Keyword', y='Growth', markers=True), use_container_width=True)
    st.table(trend_df)

elif nav == "Script Architect":
    st.title("💎 SCRIPT ARCHITECT")
    platform = st.selectbox("Platform", ["YouTube", "Reels", "Threads", "LinkedIn"])
    tone = st.select_slider("Intensity", ["Minimal", "Engaging", "High-Energy", "Aggressive"])
    topic = st.text_input("Topic")
    if st.button("Architect"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":f"Write a {tone} {platform} script for {topic}"}])
        st.markdown(res.choices[0].message.content)

elif nav == "Client Pitcher":
    st.title("💼 DIRECTOR'S PITCH VAULT")
    # Pitcher logic...
st.header("💼 DIRECTOR'S PITCH VAULT")
    c_name = st.text_input("Client Name")
    offer = st.text_area("The Offer")
    if st.button("Generate Pitch"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        prompt = f"Write a world-class cold pitch to {c_name} regarding {offer}. Keep it sharp and elite."
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}])
        st.info(res.choices[0].message.content)

