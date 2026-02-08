import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import plotly.express as px

# ==========================================
# 0. CONFIGURATION (PASTE YOUR LINKS HERE)
# ==========================================
READ_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGThrIabwjsm42GgyOqNsPkdY3BRSwv5wnOKQMH_iMetJKnUMiPESLb7wb5_n24gn33RjEpG3VhSbD/pub?gid=0&single=true&output=csv" 
WRITE_URL = "https://script.google.com/macros/s/AKfycbwR8tBqMc4XtfMfJBrjeZbzcgjIkTTIAmMXOmq2QFBf3QFB5aIJTwl5rb5KIpKiV5O7/exec"

# ==========================================
# 1. CLEAN UI SETTINGS
# ==========================================
st.set_page_config(page_title="Executive Intelligence", layout="wide")

# High-Visibility Tab Styling
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 0 20px;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF4B4B !important;
        color: white !important;
    }
</style>
""", unsafe_content_html=True)

# Initialize Session State
if "history" not in st.session_state:
    st.session_state["history"] = []

# ==========================================
# 2. MAIN INTERFACE
# ==========================================
st.title("🚀 Strategic Command Portal")

# THE TABS
tab1, tab2, tab3 = st.tabs(["🌐 GLOBAL PULSE", "🔍 INSTANT SEARCH", "🆚 COMPETITION"])

with tab1:
    st.subheader("🔥 Top Market Trends")
    # Live shuffle logic
    sectors = ['AI Content', 'Hyper-Local SEO', 'SaaS', 'Bio-Tech', 'Logistics']
    random.shuffle(sectors)
    df = pd.DataFrame({'Sector': sectors, 'Heat': sorted([random.randint(70,99) for _ in range(5)], reverse=True)})
    fig = px.bar(df, x='Heat', y='Sector', orientation='h', color='Heat', color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🔍 Deep-Dive Intelligence")
    query = st.text_input("Enter Niche to Analyze:")
    
    if query:
        if query not in st.session_state["history"]:
            st.session_state["history"].append(query)
        
        col_a, col_b = st.columns([2, 1])
        with col_a:
            # Generate trend line
            dates = [(datetime.now() - timedelta(days=i)).strftime("%b %d") for i in range(7)]
            line_df = pd.DataFrame({"Date": reversed(dates), "Interest": [random.randint(60, 100) for _ in range(7)]})
            st.plotly_chart(px.line(line_df, x="Date", y="Interest", title=f"Velocity: {query}"), use_container_width=True)
            
            st.markdown("### 🪝 Viral Hooks")
            st.info(f"Why {query} is the #1 gap in the market right now.")
            st.info(f"The truth about {query} that competitors are missing.")
            
        with col_b:
            st.markdown("### 🔑 SEO Keywords")
            st.button(f"Analyze {query} ROI", use_container_width=True)
            st.button(f"Future of {query}", use_container_width=True)

with tab3:
    st.subheader("🆚 History & Comparison")
    st.write("Recent Intelligence Log:")
    for h in reversed(st.session_state["history"][-10:]):
        st.write(f"🕒 {h}")
