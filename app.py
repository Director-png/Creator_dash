import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai  # The AI Engine

# --- 1. CONFIG & API SETUP ---
st.set_page_config(page_title="Command Portal", layout="wide")

# Replace with your actual Gemini API Key
# Get one for free at: https://aistudio.google.com/
GEMINI_API_KEY = "AIzaSyBk9U07hY-ppxvydq2jikTsCGZTOxHjjMU"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. THE READ/WRITE URL SECTION (The "Brain" of your data) ---
st.sidebar.subheader("🔗 Data Connections")
SHEET_URL = st.sidebar.text_input("Google Sheet CSV URL", 
            placeholder="https://docs.google.com/spreadsheets/d/.../export?format=csv")

# --- 3. SESSION STATE (History & Auth) ---
if 'history' not in st.session_state:
    st.session_state['history'] = []

# --- 4. DATA LOADING LOGIC (Read) ---
def load_market_data():
    if SHEET_URL:
        try:
            df = pd.read_csv(SHEET_URL)
            return df
        except Exception as e:
            st.sidebar.error("Check Sheet URL/Permissions")
            return None
    return None

df = load_market_data()

# --- 5. THE SCRIPT ARCHITECT (With Real AI) ---
with st.sidebar:
    nav = st.radio("Intelligence Modules", ["Global Pulse", "Comparison Hub", "Script Architect"])
    st.write("---")
    st.subheader("📜 History Log")
    for item in st.session_state['history']:
        st.caption(item)

if nav == "Script Architect":
    st.header("💎 AI Script Architect (Gemini Powered)")
    topic = st.text_input("Enter Topic/Niche", placeholder="e.g. AI Automation for Real Estate")
    platform = st.selectbox("Format", ["YouTube Longform", "IG Reel", "TikTok", "X Thread"])
    tone = st.select_slider("Script Tone", ["Aggressive", "Educational", "Hype"])

    if st.button("Generate Professional Strategy"):
        if topic:
            with st.spinner("AI analyzing market sentiment..."):
                # Professional Prompt Engineering
                prompt = f"""
                Act as a viral content strategist. Create a {platform} script about {topic}.
                The tone should be {tone}.
                Include:
                1. A high-retention Hook.
                2. A body that explains WHY this is trending now based on recent market shifts.
                3. A future prediction for this niche.
                4. A strong CTA.
                Format clearly with bold headings.
                """
                response = model.generate_content(prompt)
                
                # Write to Screen
                st.markdown(response.text)
                
                # Write to History
                st.session_state['history'].append(f"Generated {platform} script for {topic}")
        else:
            st.warning("Enter a topic first.")

# --- 6. GLOBAL PULSE (With Real Data) ---
elif nav == "Global Pulse":
    st.header("📈 Real-Time Global Pulse")
    if df is not None:
        fig = px.line(df, x=df.columns[0], y=df.columns[1], title="Market Movement")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Paste your Google Sheet CSV URL in the sidebar to visualize trends.")
