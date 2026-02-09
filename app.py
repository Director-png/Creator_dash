import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
from datetime import datetime
import requests

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Director Portal", layout="wide", initial_sidebar_state="expanded")

# --- 2. DATA LOAD (Market Pulse) ---
SHEET_ID = "163haIuPIna3pEY9IDxncPM2kFFsuZ76HfKsULcMu1y4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        if 'Growth' in df.columns:
            df['Growth'] = df['Growth'].astype(str).str.replace('%', '').str.replace(',', '').str.strip()
            df['Growth'] = pd.to_numeric(df['Growth'], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame({'Niche': ['Global Data'], 'Growth': [0], 'Status': ['⚖️']})

data = load_data()

# --- 3. SESSION STATE (Authentication Memory) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- 4. THE GATEKEEPER (Login/Registration Screen) ---
if not st.session_state.logged_in:
    st.title("🛡️ Director's Intelligence Portal")
    st.markdown("---")
    
    tab_login, tab_reg = st.tabs(["🔑 Authorized Login", "📝 Request New Access"])
    
    with tab_login:
        st.subheader("Enter Credentials")
        login_email = st.text_input("Email", key="l_email")
        login_pw = st.text_input("Password", type="password", key="l_pw")
        
        if st.button("Unlock Dashboard", use_container_width=True):
            # MASTER BYPASS: Use these to enter the app
            if login_email == "admin" and login_pw == "1234":
                st.session_state.logged_in = True
                st.session_state.user_name = "Master Director"
                st.rerun()
            else:
                st.error("Access Denied. Please check your credentials.")

    with tab_reg:
        st.subheader("Secure Registration")
        st.info("Submitted details will be transmitted for HQ review.")
        
        # This URL will be your Google Form 'formResponse' link
        GOOGLE_FORM_URL = "YOUR_FORM_RESPONSE_URL_HERE"
        
        with st.form("reg_form", clear_on_submit=True):
            reg_name = st.text_input("Full Name")
            reg_email = st.text_input("Email")
            reg_pw = st.text_input("Choose Password", type="password")
            
            submit = st.form_submit_button("Send Access Request", use_container_width=True)
            
            if submit:
                if reg_name and reg_email and reg_pw:
                    # Logic to send data to Google Form silently
                    form_data = {
                        "entry.123456": reg_name, 
                        "entry.789012": reg_email, 
                        "entry.345678": reg_pw
                    }
                    try:
                        # This sends the data to your Google Sheet via the Form
                        requests.post(GOOGLE_FORM_URL, data=form_data)
                        st.success(f"Request for {reg_name} transmitted.")
                        st.balloons()
                    except:
                        st.warning("Preview Mode: Registration logic is ready, awaiting Form Link.")
                else:
                    st.error("All fields are mandatory.")
    
    st.stop() # Prevents the app from loading until logged_in is True

# --- 5. THE MAIN DASHBOARD (Only runs if logged_in is True) ---
with st.sidebar:
    st.title(f"Director HQ")
    st.caption(f"Authenticated: {st.session_state.user_name}")
    st.divider()
    
    search_query = st.text_input("Global Search", placeholder="Filter niches...")
    nav = st.radio("Intelligence Modules", ["Global Pulse", "Script Architect"])
    
    st.divider()
    if st.button("🔴 Terminate Session"):
        st.session_state.logged_in = False
        st.rerun()

# MODULE: GLOBAL PULSE
if nav == "Global Pulse":
    st.header("📈 Market Momentum")
    filtered_df = data[data['Niche'].str.contains(search_query, case=False)] if search_query else data
    
    if not filtered_df.empty:
        m1, m2 = st.columns(2)
        m1.metric("Active Niches", len(filtered_df))
        m2.metric("Avg Growth", f"{filtered_df['Growth'].mean():.1f}%")

        fig = px.bar(filtered_df, x='Niche', y='Growth', color='Status', template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("📂 View Raw Intelligence Feed"):
            display_df = filtered_df.copy()
            display_df.index = range(1, len(display_df) + 1)
            st.dataframe(display_df, use_container_width=True)
    else:
        st.warning("No data matches your search.")

# MODULE: SCRIPT ARCHITECT
elif nav == "Script Architect":
    st.header("💎 AI Strategy Generator")
    topic = st.text_input("Topic", value=search_query)
    
    if st.button("Generate Strategy"):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            with st.spinner("AI is thinking..."):
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant", 
                    messages=[{"role": "user", "content": f"Script for: {topic}"}]
                )
                st.write(completion.choices[0].message.content)
        except Exception as e:
            st.error("AI Bridge Offline. Check your Secrets.")
