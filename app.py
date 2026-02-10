import streamlit as st
import pandas as pd
import plotly.express as px
import feedparser
from groq import Groq
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="VOID OS", page_icon="🌑", layout="wide")

# --- CUSTOM CSS FOR PROFESSIONAL SIDEBAR & UI ---
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #00051a;
            border-right: 1px solid #000080;
        }
        .stButton>button {
            width: 100%;
            border-radius: 5px;
            background-color: #000080;
            color: white;
            border: none;
        }
        .stButton>button:hover {
            background-color: #0000ff;
            border: none;
        }
        h1, h2, h3 {
            font-family: 'Inter', sans-serif;
        }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: white;'>VOID</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #4f4f4f;'>Parent Company: VOID</p>", unsafe_allow_html=True)
    st.divider()
    
    nav = st.radio("COMMAND CENTER", 
                  ["Dashboard", "VOID Intelligence", "Script Architect", "Settings"],
                  index=1)
    
    st.spacer = st.container()
    st.sidebar.markdown("---")
    st.sidebar.info("Founder Level Access: 1% Potential")

# --- MODULE: DASHBOARD (Home) ---
if nav == "Dashboard":
    st.title("🌑 VOID COMMAND")
    st.write(f"Welcome back, Founder. All systems operational.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Market Pulse", "Active", "High Velocity")
    col2.metric("Scripts Ready", "12", "+2 Today")
    col3.metric("VOID Value", "Top 1%", "Rising")

# --- MODULE: VOID INTELLIGENCE (Market Trends) ---
elif nav == "VOID Intelligence":
    st.markdown("<h1 style='color: #000080;'>🌑 VOID INTELLIGENCE</h1>", unsafe_allow_html=True)
    st.caption("Strategic Market Signal Analysis | Version 1.1")

    # 1. LIVE NEWS SOURCE
    RSS_URL = "https://techcrunch.com/feed/" 
    feed = feedparser.parse(RSS_URL)
    
    # 2. THE INTEL FEED
    st.subheader("📡 Recent Market Intel")
    cols = st.columns(3)
    
    if feed.entries:
        for i, entry in enumerate(feed.entries[:3]):
            with cols[i]:
                search_term = entry.title.split()[0] if entry.title else "tech"
                img_url = f"https://loremflickr.com/800/600/{search_term}?random={i}"
                st.image(img_url, use_container_width=True)
                st.markdown(f"**{entry.title}**")
                st.markdown(f"[Access Intelligence]({entry.link})")
    
    st.divider()

    # 3. THE ANALYTICS BRAIN (10 Niches with Fallback)
    if 'market_intelligence' not in st.session_state:
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            headlines = " | ".join([e.title for e in feed.entries[:10]])
            
            with st.spinner("Decoding VOID Signals..."):
                prompt = f"Analyze: {headlines}. Identify 10 unique tech/finance niches. Output ONLY 10 lines like: Topic:Score. (Score 1-100). No talk."
              raw_text = chat_completion.choices[0].message.content
                # Fixed Regex String:
                matches = re.findall(r"([^:\n]+):(\d+)", raw_text)
                
                final_data = []
                for m in matches:
                    final_data.append([m[0].strip(), int(m[1])])
                
                # PADDING LOGIC:
                if len(final_data) < 10:
                    fallbacks = [["VOID AI", 95], ["FinTech", 88], ["SaaS", 82], ["Quantum", 79], ["Neural Nets", 75], ["DeFi", 72], ["GreenTech", 68]]
                    for f in fallbacks:
                        if len(final_data) < 10: 
                            final_data.append(f)
                
                st.session_state.market_intelligence = pd.DataFrame(final_data[:10], columns=['Niche', 'Growth'])
