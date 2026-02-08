import streamlit as st
import pandas as pd
import requests
import json
import random

# ==========================================
# 1. YOUR FINAL DATABASE LINKS
# ==========================================
# Link from 'Publish to Web' (Must end in output=csv)
READ_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGThrIabwjsm42GgyOqNsPkdY3BRSwv5wnOKQMH_iMetJKnUMiPESLb7wb5_n24gn33RjEpG3VhSbD/pub?gid=0&single=true&output=csv" 
# Link from 'Apps Script' (The one you just authorized)
WRITE_URL = "web app  url - https://script.google.com/macros/s/AKfycbxJ6f6e2IYcSBXVUdyy9y_OhcAf6AuVHIp__SDPw5tgoCqOEEFAqjVabKxYoIX5FKDr/exec"
# ==========================================

def load_users():
    """Reads the current user list from your Google Sheet"""
    try:
        # Use a random query parameter to bypass cache and get fresh data
        df = pd.read_csv(f"{READ_URL}&nocache={random.randint(1,1000)}")
        df.columns = df.columns.str.lower().str.strip()
        return dict(zip(df['key'].astype(str), df['name']))
    except Exception as e:
        return {"admin": "Director"}

def register_user(new_key, new_name):
    """Sends new user data to your Google Apps Script"""
    try:
        payload = json.dumps({"key": new_key.lower().strip(), "name": new_name})
        response = requests.post(WRITE_URL, data=payload)
        return response.status_code == 200
    except:
        return False

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Executive Strategy Portal", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- LOGIN / REGISTRATION LOGIC ---
if not st.session_state["authenticated"]:
    st.title("🛡️ Executive Intelligence Dashboard")
    
    t_login, t_reg = st.tabs(["🔐 Login", "📝 New Registration"])
    
    with t_reg:
        st.subheader("Create Your Access")
        st.write("Enter your details to register. You can log in immediately after.")
        reg_name = st.text_input("Full Name (e.g., Alex Reed):")
        reg_key = st.text_input("Choose an Access Key (Password):", type="password")
        
        if st.button("Register & Activate"):
            if reg_key and reg_name:
                with st.spinner("Writing to Master Database..."):
                    if register_user(reg_key, reg_name):
                        st.success("Success! Your account is active. Switch to the 'Login' tab.")
                        st.balloons()
                    else:
                        st.error("Connection error. Ensure your Web App URL is correct.")
            else:
                st.warning("Please enter both a name and a key.")

    with t_login:
        # Fetch the latest user list
        user_db = load_users()
        with st.form("login_form"):
            l_key = st.text_input("Enter Your Access Key:", type="password").lower().strip()
            if st.form_submit_button("Enter Portal"):
                if l_key in user_db:
                    st.session_state["authenticated"] = True
                    st.session_state["identity"] = user_db[l_key]
                    st.rerun()
                else:
                    st.error("Access Key not found. Please register first.")
    st.stop()

# --- THE EXECUTIVE DASHBOARD ---
st.header(f"Strategy Briefing: {st.session_state['identity']}")
st.sidebar.title(f"🫡 {st.session_state['identity']}")

if st.sidebar.button("System Logout"):
    st.session_state.clear()
    st.rerun()

# --- MARKET INTELLIGENCE TOOLS ---
t1, t2 = st.tabs(["📊 Global Pulse", "🔍 Intelligence Search"])

with t1:
    st.subheader("High-Velocity Market Trends")
    # Add your metric cards and trend tracking here...
    st.write("Displaying real-time market velocity scores.")

with t2:
    query = st.text_input("Search Niche Intelligence:")
    if query:
        st.write(f"Analyzing SEO and Market Depth for: **{query}**")
        # Insert your Serper API logic here...
