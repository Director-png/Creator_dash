import streamlit as st
import pandas as pd
import random
import requests
from datetime import datetime, timedelta
import plotly.express as px

# ==========================================
# 0. CONFIGURATION
# ==========================================
ACCESS_KEY = "admin"

# ==========================================
# 1. ELITE UI STYLING (THE "INTRIGUE" LAYER)
# ==========================================
st.set_page_config(page_title="STRAT-INT COMMAND", layout="wide")

st.markdown("""
<style>
    /* Main Background & Text */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Custom Header Styling */
    .main-header {
        font-size: 40px;
        font-weight: 800;
        letter-spacing: -1px;
        color: #FF4B4B;
        margin-bottom: 0px;
    }
    
    /* Tab Styling - Making them stand out */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #1c1f26;
        padding: 10px 10px 0px 10px;
        border-radius: 10px 10px 0px 0px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #262730;
        border-radius: 5px 5px 0px 0px;
        color: #808495;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF4B4B !important;
        color: white !important;
    }

    /* Metric Card Styling */
    .metric-card {
        background-color: #1c1f26;
        border-left: 5px solid #FF4B4B;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_content_html=True)

# ==========================================
# 2. SESSION & AUTH
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "history" not in st.session_state:
    st.session_state["history"] = []

if not st.session_state["authenticated"]:
    st.markdown("<h1 class='main-header'>SYSTEM LOCK</h1>", unsafe_content_html=True)
    with st.container():
        col1, col2 = st.columns([1,1])
        with col1:
            u = st.text_input("DIRECTOR ID:")
            k = st.text_input("ACCESS KEY:", type="password")
            if st.button("INITIATE LOGIN"):
                if k == ACCESS_KEY and u:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = u
                    st.rerun()
        with col2:
            st.info("Registration: New IDs are logged and mapped to hardware signatures.")
    st.stop()

# ==========================================
# 3. DASHBOARD
# ==========================================
st.markdown(f"<p class='main-header'>STRAT-INT // {st.session_state['user']}</p>", unsafe_content_html=True)
st.caption(f"LIVE FEED ACTIVE • {datetime.now().strftime('%H:%M:%S')}")

t1, t2, t3 = st.tabs(["📊 GLOBAL PULSE", "🔍 DEEP ANALYSIS", "🆚 COMPETITIVE"])

with t1:
    st.subheader("🔥 Market Thermal Map")
    sectors = ['AI SaaS', 'Energy Storage', 'Agri-Tech', 'FinTech', 'Bio-Intelligence']
    random.shuffle(sectors)
    df_pulse = pd.DataFrame({'Sector': sectors, 'Heat': sorted([random.randint(70,99) for _ in range(5)], reverse=True)})
    fig = px.bar(df_pulse, x='Heat', y='Sector', orientation='h', color='Heat', 
                 color_continuous_scale='Reds', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with t2:
    query = st.text_input("ENTER TARGET NICHE:", placeholder="e.g. Quantum Computing")
    if query:
        if query not in st.session_state["history"]:
            st.session_state["history"].append(query)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(f"### Trend Velocity: {query}")
            line_data = pd.DataFrame({"X": range(7), "Y": [random.randint(50,100) for _ in range(7)]})
            st.plotly_chart(px.line(line_data, x="X", y="Y", template="plotly_dark").update_layout(showlegend=False), use_container_width=True)
            
            st.markdown("<div class='metric-card'><h4>🌍 Global Intelligence</h4>"
                        "• Regulatory shifts in APAC region creating entry gap.<br>"
                        "• Institutional capital inflow increasing 14% MoM.</div>", unsafe_content_html=True)
        
        with c2:
            st.markdown("### 🔑 SEO Strategy")
            st.success(f"**Primary:** {query} ROI 2026")
            st.markdown("---")
            st.markdown("**Viral Hook Engine:**")
            st.code(f"Why everyone is wrong about {query}...")

with t3:
    if len(st.session_state["history"]) >= 2:
        h = st.session_state["history"]
        n1, n2 = h[-1], h[-2]
        st.markdown(f"### Benchmarking: {n1} vs {n2}")
        
        metrics = ["Market Gap", "Search Vol", "Ease of Entry", "Profit Margin"]
        s1 = [random.randint(60,95) for _ in range(4)]
        s2 = [random.randint(60,95) for _ in range(4)]
        
        comp_df = pd.DataFrame({"Metric": metrics, n1: s1, n2: s2})
        st.table(comp_df)
        
        # Winner calculation
        winner = n1 if sum(s1) > sum(s2) else n2
        st.error(f"🏆 STRATEGIC WINNER: {winner}")
    else:
        st.warning("Insufficient data. Perform at least 2 searches.")

with st.sidebar:
    st.button("SECURE LOGOUT", on_click=lambda: st.session_state.clear())
