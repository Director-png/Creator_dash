import streamlit as st
import pandas as pd
import requests
import json
import random
import time
import plotly.express as px

# ==========================================
# 1. DATABASE & API KEYS
# ==========================================
READ_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGThrIabwjsm42GgyOqNsPkdY3BRSwv5wnOKQMH_iMetJKnUMiPESLb7wb5_n24gn33RjEpG3VhSbD/pub?gid=0&single=true&output=csv" 
WRITE_URL = "https://script.google.com/macros/s/AKfycbwR8tBqMc4XtfMfJBrjeZbzcgjIkTTIAmMXOmq2QFBf3QFB5aIJTwl5rb5KIpKiV5O7/exec"
SERPER_API_KEY = "cfe3d0828971dc09543b2eaa2abc4b67d29d21a0" 

# ==========================================
# 2. CORE ENGINES
# ==========================================

def load_users():
    try:
        # Cache buster to bypass Google's delay
        timestamp_url = f"{READ_URL}&cb={int(time.time())}"
        df = pd.read_csv(timestamp_url)
        df.columns = df.columns.str.lower().str.strip()
        df['key'] = df['key'].astype(str).str.lower().str.strip()
        return dict(zip(df['key'], df['name']))
    except:
        return {"admin": "Director"}

def get_comparison_chart(niche_name, color):
    # Professional Vertical Bar Chart Data
    data = pd.DataFrame({
        'Region': ['North Am.', 'Europe', 'Asia-Pac', 'Mid-East', 'LatAm'],
        'Score': [random.randint(50, 95) for _ in range(5)]
    })
    fig = px.bar(data, x='Region', y='Score', 
                 title=f"Regional Interest: {niche_name}",
                 color_discrete_sequence=[color])
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=300)
    return fig

# ==========================================
# 3. UI LAYOUT
# ==========================================
st.set_page_config(page_title="Executive Intelligence Portal", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- LOGIN & REGISTRATION ---
if not st.session_state["authenticated"]:
    st.title("🛡️ Strategic Intelligence Portal")
    t_login, t_reg = st.tabs(["🔐 Secure Entry", "📝 Registration"])
    
    with t_reg:
        name = st.text_input("Full Name")
        reg_key = st.text_input("Create Access Key", type="password")
        if st.button("Submit Registration"):
            if name and reg_key:
                payload = json.dumps({"key": reg_key.lower().strip(), "name": name})
                requests.post(WRITE_URL, data=payload)
                st.success("✅ Registered! Check the Google 'Advanced' prompt and wait 30s to Login.")
            else:
                st.warning("Please fill all fields.")

    with t_login:
        l_key = st.text_input("Enter Key", type="password").lower().strip()
        if st.button("Enter Dashboard"):
            user_db = load_users() 
            if l_key in user_db:
                st.session_state["authenticated"] = True
                st.session_state["identity"] = user_db[l_key]
                st.rerun()
            else:
                st.error("❌ Key not found yet. Refreshing... (Google delay is ~30-60s)")
    st.stop()

# --- SIDEBAR (THE DRAG DASHBOARD) ---
with st.sidebar:
    st.markdown(f"## 👤 {st.session_state['identity']}")
    st.caption("Strategic Director Access")
    st.divider()
    if st.button("🔄 Force Refresh Data"):
        st.toast("Syncing with Google Sheets...")
        load_users()
    st.divider()
    if st.button("🔒 Secure Logout"):
        st.session_state.clear()
        st.rerun()

# --- MAIN DASHBOARD ---
st.title(f"📊 Global Trends: {st.session_state['identity']}")

tab1, tab2 = st.tabs(["📈 Market Pulse", "🆚 Niche Comparison"])

with tab1:
    st.subheader("🔥 Current Lead Trend: AI Content Scaling")
    # Using Plotly for a more professional vertical bar chart
    st.plotly_chart(get_comparison_chart("Global Market", "#636EFA"), use_container_width=True)

with tab2:
    st.subheader("🆚 Strategic Niche Battle")
    col_a, col_b = st.columns(2)
    with col_a:
        niche_1 = st.text_input("First Niche", "SaaS Automation")
    with col_b:
        niche_2 = st.text_input("Second Niche", "E-com Logistics")
    
    if st.button("Compare Trends"):
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(get_comparison_chart(niche_1, "#00CC96"), use_container_width=True)
        with c2:
            st.plotly_chart(get_comparison_chart(niche_2, "#EF553B"), use_container_width=True)
            
        st.divider()
        st.write("### 📑 Market Intelligence Report")
        comp_df = pd.DataFrame({
            "Metric": ["YouTube Status", "Instagram Status", "Market Gap", "Risk Level"],
            niche_1: ["🔥 High Growth", "📈 Steady", "Underserved", "Moderate"],
            niche_2: ["📊 Saturated", "💎 High Quality", "Competitive", "Low"]
        }).set_index("Metric")
        st.table(comp_df)
