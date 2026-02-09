import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import requests
import time

# --- 1. SYSTEM CONFIG & API INITIALIZATION ---
st.set_page_config(page_title="Intelligence Command Portal", layout="wide")

# Replace with your actual Gemini API Key
GEMINI_API_KEY = "AIzaSyBk9U07hY-ppxvydq2jikTsCGZTOxHjjMU"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# --- 2. DATABASE CONNECTIONS (Read/Write) ---
# Replace with your Published CSV URL from Google Sheets
USER_DB_READ_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGThrIabwjsm42GgyOqNsPkdY3BRSwv5wnOKQMH_iMetJKnUMiPESLb7wb5_n24gn33RjEpG3VhSbD/pub?gid=0&single=true&output=csv"
# Replace with your Google Apps Script Webhook URL for Writing
USER_DB_WRITE_WEBHOOK = "https://script.google.com/macros/s/AKfycbwR8tBqMc4XtfMfJBrjeZbzcgjIkTTIAmMXOmq2QFBf3QFB5aIJTwl5rb5KIpKiV5O7/exec"

# --- 3. AUTHENTICATION & REGISTRATION ENGINE ---
def check_login(u, p):
    try:
        df = pd.read_csv(USER_DB_READ_URL)
        user_match = df[(df['username'] == u) & (df['password'] == p)]
        return not user_match.empty
    except:
        return False

def register_user_to_db(u, p):
    if USER_DB_WRITE_WEBHOOK:
        try:
            # Sends data to Google Sheet via Webhook
            response = requests.post(USER_DB_WRITE_WEBHOOK, json={"username": u, "password": p})
            return response.status_code == 200
        except:
            return False
    return False

# --- 4. ACCESS CONTROL LAYER ---
if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'user': "", 'history': []})

if not st.session_state['logged_in']:
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    with tab1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("Access Portal"):
            if check_login(u, p):
                st.session_state.update({'logged_in': True, 'user': u})
                st.rerun()
            else:
                st.error("Invalid credentials.")
    with tab2:
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            if register_user_to_db(new_u, new_p):
                st.success("Account created! Please Login.")
            else:
                st.error("Registration failed. Check Webhook.")
    st.stop()

# --- 5. SIDEBAR: NAVIGATION & INSTANT SEARCH ---
with st.sidebar:
    st.title(f"👤 {st.session_state['user']}")
    st.write("---")
    
    # INSTANT SEARCH TAB (SEO & Strategy focused)
    st.subheader("🔍 Instant Search")
    search_query = st.text_input("Analyze Niche/Trend", placeholder="e.g. AI Fitness")
    
    if search_query:
        st.info(f"Analysis for: {search_query}")
        # SEO Logic
        st.write(f"**SEO Keywords:** #{search_query.replace(' ','')}, #FutureTech, #MarketShift")
        st.write("**Hook Idea:** 'They told you {search_query} was dead... they lied.'")
    
    st.write("---")
    nav = st.radio("Intelligence Modules", ["Global Pulse", "Comparison Hub", "Script Architect"])

# --- 6. MODULES ---

# A. GLOBAL PULSE (Charts & Status Labels)
if nav == "Global Pulse":
    st.header("📈 Global Pulse trends")
    # Mock data for visualization
    data = pd.DataFrame({
        'Niche': ['AI Agents', 'Green Tech', 'SaaS', 'Bio-Hacking'],
        'Score': [98, 75, 82, 60],
        'Status': ['🔥 Rising', '⚖️ Stable', '🔥 Rising', '📉 Dropping']
    })
    
    st.table(data) # Show the labels clearly
    
    fig = px.bar(data, x='Niche', y='Score', color='Status', 
                 color_discrete_map={'🔥 Rising': 'red', '⚖️ Stable': 'blue', '📉 Dropping': 'grey'},
                 template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# B. COMPARISON HUB
elif nav == "Comparison Hub":
    st.header("⚖️ Niche Comparison Hub")
    col1, col2 = st.columns(2)
    with col1: n1 = st.selectbox("Primary Niche", ["AI", "Crypto", "Fitness"])
    with col2: n2 = st.selectbox("Comparison Niche", ["SaaS", "Real Estate", "E-com"])
    
    st.write(f"Comparing **{n1}** vs **{n2}**")
    # Comparison chart logic here

# C. SCRIPT ARCHITECT (GEMINI API)
elif nav == "Script Architect":
    st.header("💎 AI Script Architect (Premium)")
    topic = st.text_input("Video Topic", value=search_query if search_query else "")
    
    if st.button("Generate Strategy"):
        with st.status("Consulting Gemini AI...", expanded=True):
            prompt = f"""
            Generate a viral video strategy for {topic}. 
            Include: 
            1. 3 High-Retention Hooks. 
            2. Full Script Body with market insights. 
            3. SEO Keywords and Tags. 
            4. Future Trend Prediction.
            """
            response = model.generate_content(prompt)
            st.write("Strategy Ready!")
        
        st.markdown(response.text)
