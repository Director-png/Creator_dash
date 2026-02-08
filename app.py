import streamlit as st
import pandas as pd
import requests
import json
import random
import time
from datetime import datetime, timedelta
import plotly.express as px

# ==========================================
# 0. CONFIGURATION (PASTE YOUR LINKS HERE)
# ==========================================
READ_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGThrIabwjsm42GgyOqNsPkdY3BRSwv5wnOKQMH_iMetJKnUMiPESLb7wb5_n24gn33RjEpG3VhSbD/pub?gid=0&single=true&output=csv" 
WRITE_URL = "https://script.google.com/macros/s/AKfycbwR8tBqMc4XtfMfJBrjeZbzcgjIkTTIAmMXOmq2QFBf3QFB5aIJTwl5rb5KIpKiV5O7/exec"
SERPER_API_KEY = "cfe3d0828971dc09543b2eaa2abc4b67d29d21a0" 

# ==========================================
# 1. PREMIUM STYLING
# ==========================================
st.set_page_config(page_title="Executive Intelligence", layout="wide")

st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: #1e293b;
        padding: 15px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background-color: #334155;
        border-radius: 8px;
        color: white !important;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF4B4B !important;
    }
    .log-text { font-size: 13px; color: #cbd5e1; font-family: monospace; }
</style>
""", unsafe_content_html=True)

# ==========================================
# 2. DATA ENGINES
# ==========================================
if "history" not in st.session_state:
    st.session_state["history"] = []
if "search_query" not in st.session_state:
    st.session_state["search_query"] = ""

def get_live_ranking_data():
    sectors = ['AI Content Scaling', 'Hyper-Local SEO', 'SaaS Middleware', 'Bio-Tech Ads', 'Logistics']
    random.shuffle(sectors) 
    scores = sorted([random.randint(70, 99) for _ in range(5)], reverse=True)
    return pd.DataFrame({'Sector': sectors, 'Market Heat': scores})

def get_dated_line_chart(query):
    dates = [(datetime.now() - timedelta(days=i)).strftime("%b %d") for i in range(7)]
    dates.reverse()
    df = pd.DataFrame({"Date": dates, "Interest": [random.randint(65, 100) for _ in range(7)]})
    fig = px.line(df, x="Date", y="Interest", markers=True, title=f"Trend Velocity: {query}")
    fig.update_xaxes(tickangle=0)
    fig.update_layout(height=400, template="plotly_dark")
    return fig

# ==========================================
# 3. SIDEBAR
# ==========================================
with st.sidebar:
    st.title("🛡️ Secure Access")
    st.divider()
    st.subheader("📜 Recent Intelligence")
    if st.session_state["history"]:
        for h in reversed(st.session_state["history"][-5:]):
            st.markdown(f"<div class='log-text'>🕒 {h}</div>", unsafe_content_html=True)
    else:
        st.caption("No history logged.")
    
    st.divider()
    if st.button("🔒 Clear Session"):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 4. MAIN INTERFACE
# ==========================================
st.title("🚀 Strategic Command Portal")

tab1, tab2, tab3 = st.tabs(["🌐 GLOBAL PULSE", "🔍 INSTANT SEARCH", "🆚 COMPETITION"])

with tab1:
    st.subheader("🔥 Top Market Trends")
    ranking_df = get_live_ranking_data()
    fig_pulse = px.bar(ranking_df, x='Market Heat', y='Sector', orientation='h', 
                       color='Market Heat', color_continuous_scale='Reds')
    st.plotly_chart(fig_pulse, use_container_width=True)

with tab2:
    st.subheader("🔍 Deep-Dive Intelligence")
    query = st.text_input("Analyze Niche:", value=st.session_state["search_query"])
    
    if query:
        if query not in st.session_state["history"]:
            st.session_state["history"].append(query)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.plotly_chart(get_dated_line_chart(query), use_container_width=True)
            st.markdown("### 🪝 Strategic Hooks")
            st.info(f"Why {query} is the key opportunity of 2026.")
        with c2:
            st.markdown("### 🔑 Keywords")
            if st.button(f"Analyze {query} ROI", use_container_width=True):
                st.session_state["search_query"] = f"{query} ROI"
                st.rerun()

with tab3:
    st.subheader("🆚 Competitive Analysis")
    st.write("Comparison view active for session history.")
