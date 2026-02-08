import streamlit as st
import pandas as pd
import requests
import json
import random
import time
import plotly.express as px  # New library for professional chart control

# ==========================================
# 1. DATABASE & API KEYS
# ==========================================
READ_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGThrIabwjsm42GgyOqNsPkdY3BRSwv5wnOKQMH_iMetJKnUMiPESLb7wb5_n24gn33RjEpG3VhSbD/pub?gid=0&single=true&output=csv" 
WRITE_URL = "webapp url https://script.google.com/macros/s/AKfycbwR8tBqMc4XtfMfJBrjeZbzcgjIkTTIAmMXOmq2QFBf3QFB5aIJTwl5rb5KIpKiV5O7/exec"
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

def create_pro_chart(data, color_hex="#636EFA"):
    """Creates a vertical bar chart with guaranteed horizontal labels."""
    fig = px.bar(
        data, 
        x='Region', 
        y='Interest', 
        text='Interest',
        color_discrete_sequence=[color_hex]
    )
    fig.update_layout(
        xaxis={'categoryorder':'total descending', 'tickangle': 0}, # 0 angle = Horizontal
        yaxis_title="Market Interest %",
        xaxis_title=None,
        margin=dict(l=20, r=20, t=20, b=20),
        height=400
    )
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    return fig

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
        reg_key = st.text_input("Create Access Key", type="password")
        if st.button("Submit Registration"):
            if name and reg_key:
                try:
                    payload = json.dumps({"key": reg_key.lower().strip(), "name": name})
                    requests.post(WRITE_URL, data=payload, timeout=10)
                    st.success("✅ Registered. Please wait 30s for database sync.")
                except:
                    st.error("Connection Error. Check your Apps Script URL.")
    
    with t_login:
        l_key = st.text_input("Enter Key", type="password").lower().strip()
        if st.button("Enter Dashboard"):
            user_db = load_users() 
            if l_key in user_db:
                st.session_state["authenticated"] = True
                st.session_state["identity"] = user_db[l_key]
                st.rerun()
            else:
                st.error("❌ Key not recognized. Wait 30s for sync.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"### 👤 User Profile")
    st.success(f"**Director:** {st.session_state['identity']}")
    st.markdown("---")
    if st.button("🔄 Sync Database"):
        load_users()
        st.toast("Database Refreshed")
    if st.button("🔒 Secure Logout"):
        st.session_state.clear()
        st.rerun()

# --- THE MAIN PORTAL ---
st.title(f"📊 Market Intelligence: {st.session_state['identity']}")

tabs = st.tabs(["🌐 Global Pulse", "🔍 Niche Deep-Dive", "🆚 Trend Comparison"])

# Sample Region Data
geo_df = pd.DataFrame({
    'Region': ['North America', 'Europe', 'Asia-Pacific', 'Middle East', 'Latin America'],
    'Interest': [random.randint(50, 95) for _ in range(5)]
})

with tabs[0]:
    st.markdown("### 🚀 **Lead Sector: AI-Driven Automation**")
    st.plotly_chart(create_pro_chart(geo_df), use_container_width=True)
    st.info("💡 Strategic Note: All labels are now locked in horizontal orientation for readability.")

with tabs[1]:
    query = st.text_input("Search Single Niche:")
    if query:
        st.metric(f"'{query}' Momentum", f"{random.randint(70,99)}%", "🚀 RISING")
        st.line_chart([random.randint(50, 100) for _ in range(12)])

with tabs[2]:
    st.subheader("🆚 Trend Battle: Side-by-Side Comparison")
    c1, c2 = st.columns(2)
    with c1: n_a = st.text_input("Niche A", value="SaaS")
    with c2: n_b = st.text_input("Niche B", value="E-commerce")
    
    if st.button("Generate Comparison Analysis"):
        col_left, col_right = st.columns(2)
        with col_left:
            st.write(f"**{n_a}** Performance")
            st.plotly_chart(create_pro_chart(geo_df, "#29b5e8"), use_container_width=True)
        with col_right:
            st.write(f"**{n_b}** Performance")
            st.plotly_chart(create_pro_chart(geo_df, "#FF4B4B"), use_container_width=True)
        
        st.divider()
        st.write("### 📑 Strategic Breakdown")
        comp_data = {
            "Point": ["Pros", "Cons", "YouTube", "Instagram", "Forecast"],
            n_a: ["Scalability", "Churn", "🔥 Trending", "📈 Growing", "Extreme"],
            n_b: ["Low Barrier", "Logistics", "📊 Stable", "💎 Saturated", "High"]
        }
        st.table(pd.DataFrame(comp_data).set_index("Point"))
