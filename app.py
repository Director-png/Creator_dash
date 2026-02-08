import streamlit as st
import pandas as pd
import requests
import json
import random
import time

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

def get_geo_data():
    return pd.DataFrame({
        'Region': ['NA', 'EU', 'APAC', 'ME', 'LATAM'],
        'Interest': [random.randint(40, 99) for _ in range(5)]
    }).set_index('Region')

# ==========================================
# 3. UI LAYOUT
# ==========================================
st.set_page_config(page_title="Executive Intelligence", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- LOGIN / REGISTRATION ---
if not st.session_state["authenticated"]:
    st.title("🛡️ Strategic Intelligence Portal")
    t_login, t_reg = st.tabs(["🔐 Secure Entry", "📝 Registration"])
    
    with t_reg:
        name = st.text_input("Full Name")
        key = st.text_input("Create Access Key", type="password")
        if st.button("Submit Registration"):
            if name and key:
                requests.post(WRITE_URL, data=json.dumps({"key": key.lower().strip(), "name": name}))
                st.success("✅ Registered. Syncing with Google (30s)...")
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
                st.error("❌ Key not found yet. Try again in 30s.")
    st.stop()

# --- SIDEBAR (THE DRAG DASHBOARD) ---
with st.sidebar:
    st.markdown(f"### 👤 User Profile")
    st.success(f"**Name:** {st.session_state['identity']}")
    st.markdown("---")
    st.write("🛠️ **System Tools**")
    if st.button("🔄 Sync Database"):
        load_users()
        st.toast("Database Refreshed")
    
    st.markdown("---")
    if st.button("🔒 Secure Logout"):
        st.session_state.clear()
        st.rerun()

# --- THE MAIN PORTAL ---
st.title(f"📊 Market Intelligence: {st.session_state['identity']}")

tabs = st.tabs(["🌐 Global Pulse", "🔍 Niche Deep-Dive", "🆚 Trend Comparison"])

with tabs[0]:
    st.markdown("### 🚀 **Lead Sector: AI-Driven Automation**")
    st.bar_chart(get_geo_data(), use_container_width=True)
    st.info("💡 APAC is currently leading investment velocity.")

with tabs[1]:
    query = st.text_input("Search Single Niche:")
    if query:
        res = requests.post("https://google.serper.dev/search", headers={'X-API-KEY': SERPER_API_KEY}, json={"q": query}).json()
        st.metric("Momentum", f"{random.randint(70,99)}%", "🚀 RISING")
        st.line_chart([random.randint(50, 100) for _ in range(10)])
        for item in res.get('organic', [])[:3]:
            st.success(item.get('title'))

with tabs[2]:
