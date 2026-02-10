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

