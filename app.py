import streamlit as st
import pandas as pd
import random
import requests
from datetime import datetime, timedelta
import plotly.express as px

# ==========================================
# 0. CONFIGURATION (PASTE YOUR LINKS HERE)
# ==========================================
READ_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGThrIabwjsm42GgyOqNsPkdY3BRSwv5wnOKQMH_iMetJKnUMiPESLb7wb5_n24gn33RjEpG3VhSbD/pub?gid=0&single=true&output=csv" 
WRITE_URL = "https://script.google.com/macros/s/AKfycbwR8tBqMc4XtfMfJBrjeZbzcgjIkTTIAmMXOmq2QFBf3QFB5aIJTwl5rb5KIpKiV5O7/exec"

# ==========================================
# 1. PAGE SETTINGS
# ==========================================
st.set_page_config(page_title="Executive Intelligence", layout="wide")

# Initialize Session State for Persistence
if "history" not in st.session_state:
    st.session_state["history"] = []
if "search_val" not in st.session_state:
    st.session_state["search_val"] = ""

# ==========================================
# 2. SIDEBAR LOG
# ==========================================
with st.sidebar:
    st.title("🛡️ Secure Access")
    st.divider()
    st.subheader("📜 Recent Intelligence")
    if st.session_state["history"]:
        for h in reversed(st.session_state["history"][-5:]):
            st.markdown(f"🕒 `{h}`")
    else:
        st.caption("No history logged yet.")
    
    if st.button("🗑️ Clear History"):
        st.session_state["history"] = []
        st.rerun()

# ==========================================
# 3. MAIN DASHBOARD
# ==========================================
st.title("🚀 Strategic Command Portal")

# High-Contrast Tabs
tab1, tab2, tab3 = st.tabs(["🌐 GLOBAL PULSE", "🔍 INSTANT SEARCH", "🆚 COMPETITION"])

with tab1:
    st.header("🔥 Top Market Trends")
    # Live dynamic ranking simulation
    sectors = ['AI Content Scaling', 'Hyper-Local SEO', 'SaaS Middleware', 'Bio-Tech Ads', 'Logistics']
    random.shuffle(sectors)
    chart_data = pd.DataFrame({
        'Sector': sectors, 
        'Heat Index': sorted([random.randint(75, 99) for _ in range(5)], reverse=True)
    })
    fig = px.bar(chart_data, x='Heat Index', y='Sector', orientation='h', color='Heat Index', color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("🔍 Intelligence Deep-Dive")
    query = st.text_input("Enter Niche:", value=st.session_state["search_val"])
    
    if query:
        if query not in st.session_state["history"]:
            st.session_state["history"].append(query)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            # Trend Graph
            dates = [(datetime.now() - timedelta(days=i)).strftime("%b %d") for i in range(7)]
            line_df = pd.DataFrame({"Date": reversed(dates), "Interest": [random.randint(60, 100) for _ in range(7)]})
            st.plotly_chart(px.line(line_df, x="Date", y="Interest", title=f"Trend Velocity: {query}"), use_container_width=True)
        
        with c2:
            st.subheader("🔑 SEO & Strategy")
            if st.button(f"Analyze {query} ROI", use_container_width=True):
                st.session_state["search_val"] = f"{query} ROI"
                st.rerun()
            st.info(f"**Hook:** Why {query} is the #1 gap in the market right now.")

with tab3:
    st.header("🆚 Competitive Log")
    if len(st.session_state["history"]) >= 2:
        st.write(f"Comparing latest: **{st.session_state['history'][-1]}** vs **{st.session_state['history'][-2]}**")
    else:
        st.warning("Search more niches to unlock comparison data.")
