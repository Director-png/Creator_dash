import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
import requests

# --- 1. CONFIG & CONNECTIONS ---
st.set_page_config(page_title="Director Portal", layout="wide")

# Market Data (Your original sheet)
MARKET_URL = "https://docs.google.com/spreadsheets/d/163haIuPIna3pEY9IDxncPM2kFFsuZ76HfKsULcMu1y4/export?format=csv"

# User Database (The CSV link from "Publish to Web" for your Form's Sheet)
# IMPORTANT: Replace the link below with your CSV link!
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"

# Google Form Submission Link (The 'formResponse' version)
FORM_POST_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfnNLb9O-szEzYfYEL85aENIimZFtMd5H3a7o6fX-_6ftU_HA/formResponse"

# --- 2. DATA LOADING FUNCTIONS ---
def load_market_data():
    df = pd.read_csv(MARKET_URL)
    df.columns = [str(c).strip().capitalize() for c in df.columns]
    return df

def load_user_db():
    try:
        df = pd.read_csv(USER_DB_URL)
        # This part renames columns so the code can find 'Email' and 'Password' 
        # even if the Google Form headers are long questions.
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# --- 3. SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- 4. THE GATEKEEPER ---
if not st.session_state.logged_in:
    st.title("🛡️ Director's Intelligence Portal")
    t1, t2 = st.tabs(["🔑 Login", "📝 Register"])

    with t1:
        email_in = st.text_input("Email").lower().strip()
        pw_in = st.text_input("Password", type="password").strip()
        
        if st.button("Access System", use_container_width=True):
            users = load_user_db()
            
            # Master Bypass
            if email_in == "admin" and pw_in == "1234":
                st.session_state.logged_in = True
                st.session_state.user_name = "Master Director"
                st.session_state.user_email = "Admin"
                st.rerun()
            
            # Check the DB for matching Email/Password
            elif not users.empty:
                # We search for any column containing 'email' or 'password' to be safe
                email_col = [c for c in users.columns if 'email' in c][0]
                pw_col = [c for c in users.columns if 'password' in c][0]
                name_col = [c for c in users.columns if 'name' in c][0]
                
                match = users[(users[email_col] == email_in) & (users[pw_col].astype(str) == pw_in)]
                
                if not match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_name = match.iloc[0][name_col]
                    st.session_state.user_email = email_in
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
            else:
                st.error("Database connecting... Use admin login.")

    with t2:
        with st.form("reg_form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            niche = st.text_input("Niche (Focus Area)") # <--- NICHE COLUMN ADDED
            pw = st.text_input("Set Password", type="password")
            
            if st.form_submit_button("Submit Registration"):
                # PAYLOAD WITH NICHE ENTRY KEY
                payload = {
                    "entry.483203499": name,
                    "entry.1873870532": email,
                    "entry.1906780868": niche, # <--- NICHE ENTRY KEY
                    "entry.1396549807": pw
                }
                try:
                    requests.post(FORM_POST_URL, data=payload)
                    st.success("Registration transmitted! Please wait 60s for Google to sync.")
                    st.balloons()
                except:
                    st.error("Transmission failed. Check internet connection.")
    st.stop()

# --- 5. DASHBOARD (Unlocked) ---
market_data = load_market_data()

with st.sidebar:
    st.title(f"Director: {st.session_state.user_name}")
    nav = st.radio("Modules", ["Global Pulse", "Script Architect"])
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- MODULE: GLOBAL PULSE (Personalized) ---
if nav == "Global Pulse":
    st.header("📈 Market Momentum")
    
    # 1. Get the User's Niche from the Database
    users = load_user_db()
    user_niche = ""
    
    if not users.empty:
        # Finding the niche column (flexible naming)
        niche_col = [c for c in users.columns if 'niche' in c][0]
        email_col = [c for c in users.columns if 'email' in c][0]
        
        # Look up the current user's niche
        current_user_row = users[users[email_col] == st.session_state.get('user_email', '')]
        if not current_user_row.empty:
            user_niche = current_user_row.iloc[0][niche_col]

    # 2. Filtering Logic
    if user_niche:
        st.subheader(f"Focus Area: {user_niche.capitalize()}")
        # Filter market data where 'Niche' matches user's registered niche
        filtered_df = market_data[market_data['Niche'].str.contains(user_niche, case=False, na=False)]
    else:
        filtered_df = market_data

    # 3. Display Data
    if not filtered_df.empty:
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.warning(f"No specific data found for {user_niche}. Showing global feed.")
        st.dataframe(market_data, use_container_width=True)


elif nav == "Script Architect":
    st.header("💎 AI Strategy")
    topic = st.text_input("Niche Topic")
    if st.button("Generate"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": f"Outline for {topic}"}]
        )
        st.write(res.choices[0].message.content)

