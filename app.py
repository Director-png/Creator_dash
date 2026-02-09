import streamlit as st
import pandas as pd
import random
import requests
from datetime import datetime, timedelta
import plotly.express as px

# ==========================================
# 0. CONFIGURATION
# ==========================================
READ_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGThrIabwjsm42GgyOqNsPkdY3BRSwv5wnOKQMH_iMetJKnUMiPESLb7wb5_n24gn33RjEpG3VhSbD/pub?gid=0&single=true&output=csv" 
WRITE_URL = "https://script.google.com/macros/s/AKfycbwR8tBqMc4XtfMfJBrjeZbzcgjIkTTIAmMXOmq2QFBf3QFB5aIJTwl5rb5KIpKiV5O7/exec"

# ==========================================
# 1. PAGE SETTINGS & STYLING
# ==========================================
st.set_page_config(page_title="Executive Intelligence", layout="wide")

# High-Visibility Navigation Styling
import streamlit as st

# 1. Clean CSS Injection
st.set_page_config(page_title="Market Intelligence Portal", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1a1c24;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    /* This fixes the potential markdown error */
    </style>
    """, unsafe_allow_html=True)

st.title("Executive Intelligence Dashboard")

if "history" not in st.session_state:
    st.session_state["history"] = []

# ==========================================
# 2. MAIN DASHBOARD
# ==========================================
st.title("🚀 Strategic Command Portal")

tab1, tab2, tab3 = st.tabs(["🌐 GLOBAL PULSE", "🔍 INSTANT SEARCH", "🆚 COMPETITION"])

with tab1:
    st.subheader("🔥 Sector Leaderboard (Live Ranking)")
    
    # Dynamic ranking logic
    sectors = ['AI Content', 'Green Tech', 'SaaS', 'FinTech', 'Logistics']
    random.shuffle(sectors)
    scores = sorted([random.randint(70, 99) for _ in range(5)], reverse=True)
    df_pulse = pd.DataFrame({'Sector': sectors, 'Market Heat': scores})
    
    # Leaderboard Highlight
    st.error(f"🏆 TOP RANKING SECTOR: {df_pulse.iloc[0]['Sector']}")
    
    # THE VERTICAL CHART
    fig = px.bar(
        df_pulse, 
        x='Sector', 
        y='Market Heat', 
        color='Market Heat',
        text='Market Heat',
        color_continuous_scale='Reds'
    )
    fig.update_layout(yaxis_range=[0, 110], height=500, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🔍 Deep-Dive Intelligence")
    query = st.text_input("Enter target niche:")
    
    if query:
        if query not in st.session_state["history"]:
            st.session_state["history"].append(query)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            # Trend Graph
            dates = [(datetime.now() - timedelta(days=i)).strftime("%b %d") for i in range(7)]
            line_df = pd.DataFrame({"Date": list(reversed(dates)), "Interest": [random.randint(60, 100) for _ in range(7)]})
            st.plotly_chart(px.line(line_df, x="Date", y="Interest", title=f"Velocity: {query}"), use_container_width=True)
            
            st.markdown("### 🪝 Marketing Hooks")
            st.info(f"Why {query} is the key to scaling in 2026.")
        
        with c2:
            st.markdown("### 🔑 SEO Keywords")
            st.button(f"{query} ROI", use_container_width=True)
            st.button(f"Future of {query}", use_container_width=True)

with tab3:
    st.subheader("🆚 History Log")
    if st.session_state["history"]:
        for h in reversed(st.session_state["history"]):
            st.write(f"✅ Logged: **{h}**")

with st.sidebar:
    st.header("💎 Premium Features")
    tool_choice = st.selectbox("Select Tool", ["Global Pulse", "Script Architect"])

if tool_choice == "Script Architect":
    st.subheader("Video Script Generator")
    niche = st.text_input("Enter Niche (or Trend name):")
    platform = st.radio("Platform", ["YouTube", "Instagram/TikTok"])
    
    if st.button("Generate Strategy"):
        st.info(f"Analyzing past, current, and future trends for {niche}...")
        # We will plug the AI logic here next!
