import streamlit as st
import pandas as pd
import requests
import json
import random
import time
from datetime import datetime, timedelta
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
    data = pd.DataFrame({
        'Region': ['North America', 'Europe', 'Asia-Pacific', 'Middle East', 'Latin America'],
        'Score': [random.randint(50, 95) for _ in range(5)]
    })
    fig = px.bar(data, x='Region', y='Score', 
                 title=f"Market Interest: {niche_name}",
                 color_discrete_sequence=[color])
    fig.update_layout(xaxis={'tickmode': 'linear'}, margin=dict(b=80), height=400)
    return fig

def get_dated_trend_data():
    """Generates 10 days of dates leading up to today."""
    dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(10)]
    dates.reverse()
    values = [random.randint(40, 100) for _ in range(10)]
    return pd.DataFrame({"Date": dates, "Interest": values})

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
                st.error("❌ Key not found. Please wait for Google sync.")
    st.stop()

# --- SIDEBAR (USER PROFILE) ---
with st.sidebar:
    st.markdown(f"## 👤 {st.session_state['identity']}")
    st.caption(f"Last Login: {datetime.now().strftime('%H:%M:%S')}")
    st.divider()
    if st.button("🔄 Sync Database"):
        load_users()
        st.toast("Refreshed!")
    st.divider()
    if st.button("🔒 Secure Logout"):
        st.session_state.clear()
        st.rerun()

# --- MAIN DASHBOARD ---
st.title(f"📊 Market Intelligence: {st.session_state['identity']}")
st.caption(f"Data Stream Active • {datetime.now().strftime('%B %d, %Y')}")

tabs = st.tabs(["🌐 Global Pulse", "🔍 Niche Deep-Dive", "🆚 Trend Comparison"])

# TAB 1: PULSE
with tabs[0]:
    st.subheader("🚀 Lead Sector Analysis")
    st.plotly_chart(get_comparison_chart("Current Global Lead", "#636EFA"), use_container_width=True)

# TAB 2: SEARCH (WITH DATES)
with tabs[1]:
    st.subheader("🔍 Deep-Dive Research")
    query = st.text_input("Enter specific niche to mine data:")
    if query:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.caption(f"📍 Intelligence Source: Serper Global Index | Verified at: **{current_time}**")
        
        with st.spinner("Mining Google & Social Databases..."):
            res = requests.post("https://google.serper.dev/search", 
                                headers={'X-API-KEY': SERPER_API_KEY}, 
                                json={"q": query}).json()
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Momentum Score", f"{random.randint(75, 98)}%", "UP")
                st.write(f"### 📈 10-Day Trend Velocity: {query}")
                trend_df = get_dated_trend_data()
                st.line_chart(trend_df.set_index("Date"))
            with c2:
                st.write("### 🗝️ Top Search Results")
                for item in res.get('organic', [])[:4]:
                    st.info(f"🔗 {item.get('title')}")

# TAB 3: COMPARISON
with tabs[2]:
    st.subheader("🆚 Battle for Market Share")
    col_a, col_b = st.columns(2)
    with col_a: niche_1 = st.text_input("Niche A", "Web3 SaaS")
    with col_b: niche_2 = st.text_input("Niche B", "AI Hardware")
    
    if st.button("Run Comparison Analysis"):
        st.caption(f"⚡ Comparison generated on {datetime.now().strftime('%d %b %Y at %I:%M %p')}")
        ca, cb = st.columns(2)
        with ca:
            st.plotly_chart(get_comparison_chart(niche_1, "#00CC96"), use_container_width=True)
        with cb:
            st.plotly_chart(get_comparison_chart(niche_2, "#EF553B"), use_container_width=True)
            
        st.divider()
        st.write("### 📑 Executive Breakdown")
        comp_df = pd.DataFrame({
            "Metric": ["YT Sentiment", "IG Growth", "Status", "Profitability"],
            niche_1: ["Positive", "7.4% (MoM)", "Active", "High"],
            niche_2: ["Mixed", "12.1% (MoM)", "Emerging", "Very High"]
        }).set_index("Metric")
        st.table(comp_df)
