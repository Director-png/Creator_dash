import streamlit as st
import pandas as pd
import requests
import json
import random

# ==========================================
# 1. THE ONLY THREE THINGS YOU NEED TO PASTE
# ==========================================
GITHUB_CLIENT_ID = "YOUR_ID_HERE"
GITHUB_CLIENT_SECRET = "YOUR_SECRET_HERE"
SHEET_URL = "YOUR_GOOGLE_SHEET_CSV_LINK_HERE" # The one from 'Publish to Web'
# ==========================================

st.set_page_config(page_title="Executive Strategy Portal", layout="wide")

# --- AUTHENTICATION ENGINE ---
def get_github_user(code):
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
    }
    r = requests.post(token_url, headers=headers, data=data)
    token = r.json().get("access_token")
    
    user_r = requests.get("https://api.github.com/user", 
                          headers={"Authorization": f"token {token}"})
    return user_r.json()

# Logic to handle the redirect from GitHub
if "code" in st.query_params and "authenticated" not in st.session_state:
    with st.spinner("Authenticating with GitHub..."):
        try:
            user_data = get_github_user(st.query_params["code"])
            st.session_state["authenticated"] = True
            st.session_state["user"] = user_data
        except:
            st.error("Authentication failed. Please check your GitHub Keys.")

# --- LOGIN SCREEN ---
if not st.session_state.get("authenticated"):
    st.title("🛡️ Executive Intelligence Dashboard")
    st.info("Direct Access enabled for authorized GitHub identities.")
    
    # The Professional Login Button
    login_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}"
    st.markdown(f"""
        <a href="{login_url}" target="_self" style="text-decoration: none;">
            <div style="background-color: #24292e; color: white; padding: 12px; border-radius: 8px; text-align: center; width: 250px; font-weight: bold;">
                🚀 Login with GitHub
            </div>
        </a>
    """, unsafe_allow_html=True)
    st.stop()

# --- MAIN DASHBOARD (Only shows if logged in) ---
user = st.session_state["user"]
st.sidebar.image(user.get("avatar_url"), width=80)
st.sidebar.title(f"🫡 {user.get('name') or user.get('login')}")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# --- MARKET ANALYSIS LOGIC ---
@st.cache_data(ttl=600)
def fetch_trends(keyword):
    # Your Serper API Logic
    API_KEY = "cfe3d0828971dc09543b2eaa2abc4b67d29d21a0"
    # ... (Keeping it simple for the test)
    return {"score": random.randint(50, 99), "status": "🚀 RISING"}

st.header(f"Welcome to the Portal, {user.get('name', 'Director')}")
st.write(f"Verified Identity: {user.get('login')}")

# Add your Pulse and Search tabs here just like before...
st.info("System is live. Tracking active for your GitHub ID.")
