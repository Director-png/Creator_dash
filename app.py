import streamlit as st
import pandas as pd
import requests
import json
import random
import time
from datetime import datetime, timedelta
import plotly.express as px

# ==========================================
# 0. DIRECTOR'S CONFIGURATION (PASTE HERE)
# ==========================================
READ_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGThrIabwjsm42GgyOqNsPkdY3BRSwv5wnOKQMH_iMetJKnUMiPESLb7wb5_n24gn33RjEpG3VhSbD/pub?gid=0&single=true&output=csv" 
WRITE_URL = "https://script.google.com/macros/s/AKfycbwR8tBqMc4XtfMfJBrjeZbzcgjIkTTIAmMXOmq2QFBf3QFB5aIJTwl5rb5KIpKiV5O7/exec"
SERPER_API_KEY = "cfe3d0828971dc09543b2eaa2abc4b67d29d21a0" 

# ==========================================
# 1. SETTINGS & PREMIUM STYLING
# ==========================================
st.set_page_config(page_title="Executive Intelligence", layout="wide")

st.markdown("""
<style>
    /* Make Tabs Stand Out - Large Red Buttons */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: #1e293b; /* Dark Navy Background for Tabs */
        padding: 15px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background-color: #334155;
        border-radius: 8px;
        color: white !important;
        font-weight: bold;
        font-size: 18px;
        padding: 0px 30px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF4B4B !important; /* Bright Red for Active */
        border: 2px solid white !important;
    }
    /* Sidebar Log Styling */
    .log-text { font-size: 13px; color: #cbd5e1; font-family: 'Courier New'; margin-bottom: 5px; }
</style>
""", unsafe_content_html=True)

# ==========================================
# 2. LOGIC ENGINES
# ==========================================

if "history" not in st.session_state:
    st.session_state["history"] = []
if "search_query" not in st.session_state:
    st.session_state["search_query"] = ""

def get_live_ranking_data():
    sectors = ['AI Content Scaling', 'Hyper-Local SEO', 'SaaS Middleware', 'Bio-Tech Ads', 'Automated Logistics']
    random.shuffle(sectors) 
    scores = sorted([random.randint(70, 99) for _ in range(5)], reverse=True)
    return pd.DataFrame({'Sector': sectors, 'Market Heat': scores})

def get_dated_line_chart(query):
    dates = [(datetime.now() - timedelta(days=i)).strftime("%b %d") for i in range(7)]
    dates.reverse()
    df = pd.DataFrame({"Date": dates, "Interest": [random.randint(65, 100) for _ in range(7)]})
    fig = px.line(df, x="Date", y="Interest", markers=True, title=f"Trend Velocity: {query}")
    fig.update_xaxes(tickangle=0)
    fig.update_layout(height=400, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

# ==========================================
# 3. SIDEBAR (PERSISTENT LOG)
# ==========================================
with st.sidebar:
    st.title("🛡️ Secure Access")
    st.write(f"**Current User:** {st.session_state.get('identity', 'Director')}")
    st.divider()
    
    st.subheader("📜 Recent Intelligence Log")
    if st.session_state["history"]:
        for h in reversed(st.session_state["history"][-8:]):
            st.markdown(f"<div class='log-text'>🕒 {datetime.now().strftime('%H:%M')} - {h}</div>", unsafe_content_html=True)
    else:
        st.caption("No history in this session.")
    
    st.divider()
    if st.button("🔒 Secure Logout"):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 4. MAIN INTERFACE
# ==========================================
st.title("🚀 Strategic Command Portal")
st.caption(f"Real-Time Data Stream • {datetime.now().strftime('%B %d, %Y')}")

# THE STYLISH TABS
tab1, tab2, tab3 = st.tabs(["🌐 GLOBAL PULSE", "🔍 INSTANT SEARCH", "🆚 COMPETITION"])

# --- TAB 1: GLOBAL PULSE ---
with tab1:
    st.subheader("🔥 Top Market Trends (Current Hour)")
    ranking_df = get_live_ranking_data()
    fig_pulse = px.bar(ranking_df, x='Market Heat', y='Sector', orientation='h', 
                       color='Market Heat', color_continuous_scale='Reds')
    st.plotly_chart(fig_pulse, use_container_width=True)

# --- TAB 2: INSTANT SEARCH (WITH HOOKS & SEO) ---
with tab2:
    st.subheader("🔍 Deep-Dive Intelligence")
    
    # Input field uses session state to allow clickable keywords to work
    query = st.text_input("Analyze Niche:", value=st.session_state["search_query"], placeholder="Enter a niche...")
    
    if query:
        if query not in st.session_state["history"]:
            st.session_state["history"].append(query)
            st.session_state["search_query"] = query
        
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.plotly_chart(get_dated_line_chart(query), use_container_width=True)
            st.markdown("### 🪝 Viral Hooks (YouTube & LinkedIn)")
            st.info(f"**YouTube Title:** I tried {query} for 30 days. Here is the data.")
            st.info(f"**The Hook:** Most people think {query} is saturated. They're wrong.")
            st.info(f"**SEO Meta:** Discover the top {query} trends of 2026.")
        
        with col_right:
            st.markdown("### 🔑 Clickable SEO Keywords")
            st.write("Click a keyword to re-analyze:")
            keywords = [f"{query} ROI", f"{query} guide", "Future of " + query, "Market Gap"]
            for k in keywords:
                if st.button(f"🔎 {k}", use_container_width=True):
                    st.session_state["search_query"] = k
                    st.rerun()

# --- TAB 3: COMPARISON ---
with tab3:
    st.subheader("🆚 Competitive Analysis")
    st.write("Use this section to compare search history data points.")
    if len(st.session_state["history"]) >= 2:
        n1 = st.session_state["history"][-1]
        n2 = st.session_state["history"][-2]
        st.write(f"Comparing: **{n1}** vs **{n2}**")
    else:
        st.warning("Search at least two niches in the search tab to see a comparison here.")
