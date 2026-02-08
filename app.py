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
WRITE_URL = "https://script.google.com/macros/s/AKfycbxJ6f6e2IYcSBXVUdyy9y_OhcAf6AuVHIp__SDPw5tgoCqOEEFAqjVabKxYoIX5FKDr/exec"
SERPER_API_KEY = "cfe3d0828971dc09543b2eaa2abc4b67d29d21a0" 

# ==========================================
# 2. CORE ENGINES
# ==========================================

def load_users():
    """Forces Google to bypass the 5-minute cache delay."""
    try:
        # The 't' parameter tells Google this is a brand new request
        timestamp_url = f"{READ_URL}&cachebust={int(time.time())}"
        df = pd.read_csv(timestamp_url)
        df.columns = df.columns.str.lower().str.strip()
        # Clean up whitespace in keys
        df['key'] = df['key'].astype(str).str.lower().str.strip()
        return dict(zip(df['key'], df['name']))
    except Exception as e:
        return {"admin": "Director"}

# ==========================================
# 3. UI LAYOUT
# ==========================================
st.set_page_config(page_title="Executive Intelligence", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- LOGIN / REGISTRATION ---
if not st.session_state["authenticated"]:
    st.title("🛡️ Strategic Portal")
    t_login, t_reg = st.tabs(["🔐 Login", "📝 Register"])
    
    with t_reg:
        name = st.text_input("Full Name")
        key = st.text_input("Access Key (Password)", type="password")
        if st.button("Create Account"):
            if name and key:
                requests.post(WRITE_URL, data=json.dumps({"key": key.lower().strip(), "name": name}))
                st.success("✅ Registered! Please wait about 30-60 seconds for the database to sync, then Login.")
            else:
                st.warning("Please fill both fields.")

    with t_login:
        # We fetch the database ONLY when the button is clicked to be as fresh as possible
        l_key = st.text_input("Enter Access Key", type="password").lower().strip()
        if st.button("Enter Portal"):
            user_db = load_users() 
            if l_key in user_db:
                st.session_state["authenticated"] = True
                st.session_state["identity"] = user_db[l_key]
                st.rerun()
            else:
                st.error("❌ Key not found yet. Google is still processing
