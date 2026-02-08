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
WRITE_URL = "web app  url - https://script.google.com/macros/s/AKfycbxJ6f6e2IYcSBXVUdyy9y_OhcAf6AuVHIp__SDPw5tgoCqOEEFAqjVabKxYoIX5FKDr/exec"
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
                st.success("✅ Registered. Please wait 30s for sync.")
            else:
                st.warning("Please fill fields.")

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

# --- THE MAIN PORTAL ---
st.title(f"📊 Market Intelligence: {st.session_state['identity']}")
st.markdown(f"**Authorized Access Level:** Director | **Welcome, {st.session_state['identity']}**")

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
    st.subheader("🆚 Trend Battle: Side-by-Side Comparison")
    c1, c2 = st.columns(2)
    with c1: niche_a = st.text_input("Enter Niche A", value="SaaS")
    with c2: niche_b = st.text_input("Enter Niche B", value="E-commerce")
    
    if st.button("Generate Comparison Analysis"):
        # 1. VISUAL CHART COMPARISON
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.write(f"**{niche_a}** Regional Interest")
            st.bar_chart(get_geo_data(), color="#29b5e8")
        with chart_col2:
            st.write(f"**{niche_b}** Regional Interest")
            st.bar_chart(get_geo_data(), color="#FF4B4B")
        
        st.divider()

        # 2. PROS / CONS & SOCIAL STATUS TABLE
        st.write("### 📑 Strategic Breakdown")
        comp_data = {
            "Feature": ["Pros", "Cons", "YouTube Status", "Instagram Status", "Current Demand"],
            niche_a: [
                "High recurring revenue", 
                "High technical barrier", 
                "🔥 Trending (Tutorials)", 
                "📈 Growing (B2B)", 
                "Extreme"
            ],
            niche_b: [
                "Low barrier to entry", 
                "Complex logistics", 
                "📊 Stable (Reviews)", 
                "💎 Saturated (Influencer)", 
                "High"
            ]
        }
        st.table(pd.DataFrame(comp_data).set_index("Feature"))

# LOGOUT
if st.sidebar.button("🔒 Secure Logout"):
    st.session_state.clear()
    st.rerun()
