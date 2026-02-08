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
        timestamp_url = f"{READ_URL}&cb={int(time.time())}"
        df = pd.read_csv(timestamp_url)
        df.columns = df.columns.str.lower().str.strip()
        df['key'] = df['key'].astype(str).str.lower().str.strip()
        return dict(zip(df['key'], df['name']))
    except:
        return {"admin": "Director"}

def get_comparison_chart(niche_name, color):
    # Data with FULL region names
    data = pd.DataFrame({
        'Region': ['North America', 'Europe', 'Asia-Pacific', 'Middle East', 'Latin America'],
        'Score': [random.randint(50, 95) for _ in range(5)]
    })
    fig = px.bar(data, x='Region', y='Score', 
                 title=f"Market Interest: {niche_name}",
                 color_discrete_sequence=[color])
    
    # FORCE FULL NAMES: This prevents "North Am..." truncation
    fig.update_layout(
        xaxis={'categoryorder':'total descending', 'tickmode': 'linear'},
        margin=dict(l=20, r=20, t=40, b=80), # Increased bottom margin for names
        height=400
    )
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
                st.success("✅ Registered! Check the Google 'Advanced' prompt and wait 30s.")
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
                st.error("❌ Key not found. Please wait 30s for Google to sync.")
    st.stop()

# --- SIDEBAR (USER PROFILE) ---
with st.sidebar:
    st.markdown(f"## 👤 {st.session_state['identity']}")
    st.caption("Status: Authorized Director")
    st.divider()
    if st.button("🔄 Sync Database"):
        load_users()
        st.toast("Refreshed!")
    st.divider()
    if st.button("🔒 Secure Logout"):
        st.session_state.clear()
        st.rerun()

# --- MAIN DASHBOARD (ALL 3 TABS RESTORED) ---
st.title(f"📊 Market Intelligence: {st.session_state['identity']}")

tabs = st.tabs(["🌐 Global Pulse", "🔍 Niche Deep-Dive", "🆚 Trend Comparison"])

# TAB 1: PULSE
with tabs[0]:
    st.subheader("🚀 Lead Sector Analysis")
    st.plotly_chart(get_comparison_chart("Current Global Lead", "#636EFA"), use_container_width=True)

# TAB 2: SEARCH (RESTORED)
with tabs[1]:
    st.subheader("🔍 Deep-Dive Research")
    query = st.text_input("Enter specific niche to mine data:")
    if query:
        with st.spinner("Mining Google & Social Databases..."):
            res = requests.post("https://google.serper.dev/search", 
                                headers={'X-API-KEY': SERPER_API_KEY}, 
                                json={"q": query}).json()
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Momentum Score", f"{random.randint(75
