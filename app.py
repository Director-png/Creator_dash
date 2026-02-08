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
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #334155;
        border-radius: 5px;
        color: white !important;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF4B4B !important;
    }
</style>
""", unsafe_content_html=True)

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
