import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
import requests
import feedparser

# --- 1. CONFIG & CONNECTIONS ---
st.set_page_config(page_title="VOID OS", page_icon="🌑", layout="wide")

MARKET_URL = "https://docs.google.com/spreadsheets/d/163haIuPIna3pEY9IDxncPM2kFFsuZ76HfKsULcMu1y4/export?format=csv"
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"

# --- 2. DATA LOADING ---
def load_market_data():
    try:
        df = pd.read_csv(MARKET_URL)
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        return df
    except: return pd.DataFrame()

def load_user_db():
    try:
        df = pd.read_csv(USER_DB_URL)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except: return pd.DataFrame()

# --- 3. MASTER SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = "user"
if 'user_name' not in st.session_state: st.session_state.user_name = "Operator"

# --- 4. AUTH PORTAL (Restored Original Tabs) ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🛡️ DIRECTOR'S INTELLIGENCE PORTAL</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with t1:
        email_in = st.text_input("Email").lower().strip()
        pw_in = st.text_input("Password", type="password")
        if st.button("Access System", use_container_width=True):
            if (email_in == "admin" and pw_in == "1234") or (email_in == "director@void.com" and pw_in == "VOID_2026"):
                st.session_state.logged_in = True
                st.session_state.user_role = "admin"
                st.session_state.user_name = "The Director"
                st.rerun()
            else:
                users = load_user_db()
                if not users.empty:
                    # Column 2 is Email, Column 4 is Password
                    match = users[(users.iloc[:, 2].astype(str).str.lower() == email_in) & (users.iloc[:, 4].astype(str) == pw_in)]
                    if not match.empty:
                        st.session_state.logged_in = True
                        st.session_state.user_name = match.iloc[0, 1]
                        st.session_state.user_role = "user"
                        st.rerun()
                else: st.error("Access Denied / Database Offline.")
    
    with t2:
        st.info("Registration points to internal database. Contact Admin for credentials.")
    st.stop()

# --- 5. SIDEBAR (Your Custom Layout) ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #00d4ff; margin-bottom: 0;'>🌑 VOID OS</h1>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 20px;'>
            <p style='color: #00ff41; font-family: monospace; font-size: 0.9em; margin: 0;'>● ONLINE: {st.session_state.user_name.upper()}</p>
            <p style='color: gray; font-size: 0.7em; margin: 0;'>V 2.0 | {st.session_state.user_role.upper()} ACCESS</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    with st.expander("📡 SYSTEM STATUS", expanded=False):
        st.write("🟢 Core: Operational")
        st.write("🔵 Intelligence: Syncing")
        st.write("🔒 Security: Level 5")
    
    st.divider()
    st.subheader("🛠️ COMMANDS")
    nav_map = {
        "📊 Dashboard": "Dashboard",
        "🌐 Global Pulse": "Global Pulse",
        "⚔️ Trend Duel": "Trend Comparison",
        "💎 Script Architect": "Script Architect"
    }
    if st.session_state.user_role == "admin": nav_map["💼 Client Pitcher"] = "Client Pitcher"

    selection = st.radio("SELECT MODULE", list(nav_map.keys()), label_visibility="collapsed")
    nav = nav_map[selection]

    st.divider()
    if st.button("🔄 Force Data Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    if st.button("🔓 Terminate Session", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- 6. MODULES ---

if nav == "Dashboard":
    st.header("🌑 SYSTEM OVERVIEW")
    data = load_market_data()
    if not data.empty:
        fig = px.bar(data.head(8), x=data.columns[1], y=data.columns[0], orientation='h', 
                     title="Niche Momentum Index", color_discrete_sequence=['#00d4ff'])
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("VOID Status", "Active")
    m2.metric("Director Access", "Verified" if st.session_state.user_role == "admin" else "Restricted")
    m3.metric("Network", "Secure")

elif nav == "Global Pulse":
    st.title("🌐 GLOBAL PULSE")
    data = load_market_data()
    if not data.empty:
        st.subheader("📊 Niche Momentum Index")
        fig = px.bar(data.head(8), x=data.columns[1], y
