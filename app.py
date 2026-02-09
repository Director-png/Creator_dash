import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
import requests
import feedparser # Add this to the very top of your app.py





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
    # Define search_query here so it's global!
    search_query = st.text_input("Global Intelligence Search", placeholder="e.g. AI, Fitness...")
    nav = st.radio("Modules", ["Global Pulse", "Script Architect"])
    # ... rest of sidebar code




# --- MODULE: GLOBAL PULSE (With Live Intelligence) ---
if nav == "Global Pulse":
    st.header("📈 Market Momentum")
    
    # 1. LIVE RSS FEED LOGIC
    st.subheader("📡 Live Intelligence Feed")
    
    # You can change this URL to any RSS feed (Google Trends, Tech News, etc.)
    RSS_URL = "https://techcrunch.com/feed/" 
    feed = feedparser.parse(RSS_URL)
    
    # Display the latest 3 headlines in a clean "Ticker" style
    if feed.entries:
        cols = st.columns(3)
        for i, entry in enumerate(feed.entries[:3]):
            with cols[i]:
                st.info(f"**{entry.title}**")
                st.caption(f"Source: {feed.feed.title}")
                st.markdown(f"[Read Intel]({entry.link})")
    
    st.divider()

    # 2. PERSONALIZED MARKET DATA
    users = load_user_db()
    user_niche = ""
    
    if not users.empty and 'user_email' in st.session_state:
        # Finding the niche column flexibly
        niche_cols = [c for c in users.columns if 'niche' in c]
        email_cols = [c for c in users.columns if 'email' in c]
        
        if niche_cols and email_cols:
            current_user_row = users[users[email_cols[0]] == st.session_state.user_email]
            if not current_user_row.empty:
                user_niche = current_user_row.iloc[0][niche_cols[0]]

    if user_niche:
        st.subheader(f"Targeted Analysis: {user_niche.capitalize()}")
        filtered_df = market_data[market_data['Niche'].str.contains(user_niche, case=False, na=False)]
    else:
        st.subheader("Global Market Overview")
        filtered_df = market_data

    # 3. DATA VISUALIZATION
    if not filtered_df.empty:
        # Show a growth chart
        fig = px.area(filtered_df, x='Niche', y='Growth', title="Growth Velocity", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.warning("No niche-specific data found. Showing all markets.")
        st.dataframe(market_data, use_container_width=True)

# --- MODULE: ENHANCED SCRIPT ARCHITECT ---
elif nav == "Script Architect":
    st.header("💎 Script Architecht")
    
topic = st.text_input("Target Topic", placeholder="Enter your niche or video idea...")
    
    # Strategy Toggle
    format_type = st.radio(
        "Select Content Architecture:",
        ["📱 Short-Form (Reels/Shorts/TikTok)", "📺 Long-Form (YouTube/Masterclass)"],
        horizontal=True
    )
    
    if st.button("Generate Strategy", use_container_width=True):
        if topic:
            # Custom prompt based on format
            if "Short-Form" in format_type:
                system_prompt = "Generate a 60-second viral script. Focus on a 3-second visual hook, fast-paced value, and a high-energy CTA."
            else:
                system_prompt = "Generate a 10-minute video outline. Focus on an intro hook, storytelling arc, 3 deep-dive sections, and a long-term retention strategy."

            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                with st.spinner("Architecting your content..."):
                    completion = client.chat.completions.create(
                        model="llama-3.1-8b-instant", 
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Topic: {topic}"}
                        ]
                    )
                    st.markdown("---")
                    st.subheader(f"Strategy: {format_type}")
                    st.markdown(completion.choices[0].message.content)
            except Exception as e:
                st.error("AI Bridge Offline. Check your Groq Key.")
        else:
            st.warning("Please enter a topic to begin.")





