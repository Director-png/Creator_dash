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
ACCESS_KEY = "admin" # Your Master Key

# ==========================================
# 1. SECURITY LAYER (FORCED ENTRY)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🛡️ Executive Access Required")
    choice = st.radio("Select Action:", ["Login", "Register New User"])
    
    key_input = st.text_input("Enter Access Key:", type="password")
    user_id = st.text_input("Username / Director ID:")
    
    if st.button("Authorize Access"):
        if key_input == ACCESS_KEY and user_id:
            st.session_state["authenticated"] = True
            st.session_state["user"] = user_id
            st.rerun()
        else:
            st.error("Invalid Credentials. Access Denied.")
    st.stop()

# ==========================================
# 2. CORE LOGIC & STATE
# ==========================================
if "history" not in st.session_state:
    st.session_state["history"] = []

def get_niche_news(query):
    # Simulating global niche intelligence
    news = [
        f"Global trade shifts impacting {query} production.",
        f"New regulatory framework for {query} announced in EU.",
        f"VC sentiment for {query} startups hits 2-year high."
    ]
    return news

# ==========================================
# 3. MAIN INTERFACE
# ==========================================
st.title(f"🚀 Command Portal: {st.session_state['user']}")

tab1, tab2, tab3 = st.tabs(["🌐 GLOBAL PULSE", "🔍 INSTANT SEARCH", "🆚 COMPARISON"])

with tab1:
    st.subheader("🔥 Live Ranking: Global Sectors")
    sectors = ['AI Automation', 'Green Tech', 'E-com', 'FinTech', 'Health']
    random.shuffle(sectors)
    df_pulse = pd.DataFrame({'Sector': sectors, 'Heat': sorted([random.randint(70,99) for _ in range(5)], reverse=True)})
    st.plotly_chart(px.bar(df_pulse, x='Heat', y='Sector', orientation='h', color='Heat', color_continuous_scale='Reds'), use_container_width=True)

with tab2:
    st.subheader("🔍 Deep-Dive & News")
    query = st.text_input("Analyze Niche:")
    
    if query:
        if query not in st.session_state["history"]:
            st.session_state["history"].append(query)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            # Trend Chart
            dates = [(datetime.now() - timedelta(days=i)).strftime("%b %d") for i in range(7)]
            line_df = pd.DataFrame({"Date": list(reversed(dates)), "Interest": [random.randint(60, 100) for _ in range(7)]})
            st.plotly_chart(px.line(line_df, x="Date", y="Interest", title=f"Velocity: {query}"), use_container_width=True)
            
            st.markdown("### 🌍 Worldly Intelligence")
            for item in get_niche_news(query):
                st.write(f"📰 {item}")

        with c2:
            st.markdown("### 🔑 SEO & Strategy")
            st.info(f"**Primary Keyword:** {query} ROI")
            st.success(f"**Strategy:** Focus on 'Gap Markets' in {query} for Q3.")
            st.markdown("---")
            st.markdown("**Viral Hook:**")
            st.code(f"The truth about {query} that no one is telling you.")

with tab3:
    st.subheader("🆚 Benchmarking & Tabular Data")
    if len(st.session_state["history"]) >= 2:
        # Comparison Table
        comp_data = {
            "Metric": ["Market Heat", "SEO Difficulty", "Viral Potential", "ROI Score"],
            st.session_state["history"][-1]: [random.randint(70,99) for _ in range(4)],
            st.session_state["history"][-2]: [random.randint(70,99) for _ in range(4)]
        }
        comp_df = pd.DataFrame(comp_data)
        
        st.table(comp_df) # Tabular View
        
        # Comparison Chart
        st.markdown("### 📊 Performance Comparison")
        fig_comp = px.bar(comp_df, x="Metric", y=[st.session_state["history"][-1], st.session_state["history"][-2]], barmode='group')
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.warning("Please analyze at least two niches in the search tab to generate a comparison.")

# Sidebar Log
with st.sidebar:
    st.write(f"Logged in as: **{st.session_state['user']}**")
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
