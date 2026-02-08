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

# Styling to separate Tabs from Header
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: #f1f4f9;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #d1d9e6;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        font-weight: bold;
        font-size: 16px;
    }
    .stTabs [aria-selected="true"] {
        color: #FF4B4B !important;
        border-bottom: 3px solid #FF4B4B !important;
    }
</style>
""", unsafe_content_html=True)

if "history" not in st.session_state:
    st.session_state["history"] = []

# ==========================================
# 2. MAIN DASHBOARD
# ==========================================
st.title("🚀 Strategic Command Portal")
st.caption(f"Market Intelligence Feed • {datetime.now().strftime('%H:%M')} Local Time")

tab1, tab2, tab3 = st.tabs(["🌐 GLOBAL PULSE", "🔍 INSTANT SEARCH", "🆚 COMPETITION"])

with tab1:
    st.subheader("🔥 Sector Leaderboard (Vertical Velocity)")
    
    # Dynamic shuffle for ranking
    sectors = ['AI Automation', 'Green Logistics', 'SaaS Fintech', 'HealthTech', 'Ad-Tech']
    random.shuffle(sectors)
    heat_scores = sorted([random.randint(70, 99) for _ in range(5)], reverse=True)
    
    df_pulse = pd.DataFrame({'Sector': sectors, 'Market Heat': heat_scores})
    
    # Top Performer Badge
    st.error(f"🏆 CURRENT TRENDING LEADER: {df_pulse.iloc[0]['Sector']}")
    
    # Vertical Bar Chart
    fig = px.bar(
        df_pulse, 
        x='Sector', 
        y='Market Heat', 
        color='Market Heat',
        text='Market Heat',
        color_continuous_scale='Reds',
        template="plotly_white"
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(yaxis_range=[0, 110], height=500)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🔍 Deep-Dive Intelligence")
    query = st.text_input("Enter target niche:", placeholder="e.g. Eco-SaaS")
    
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
            st.code(f"1. Why {query} is the hidden goldmine of 2026.\n2. Stop wasting time on old trends; {query} is the future.", language=None)
        
        with c2:
            st.markdown("### 🔑 SEO Keywords")
            keywords = [f"{query} ROI", f"Best {query} tools", f"Future of {query}"]
            for kw in keywords:
                st.button(kw, use_container_width=True)

with tab3:
    st.subheader("🆚 History & Comparison")
    if st.session_state["history"]:
        for h in reversed(st.session_state["history"]):
            st.write(f"✅ Intelligence Gathered: **{h}**")
    else:
        st.info("Your search history will appear here.")
