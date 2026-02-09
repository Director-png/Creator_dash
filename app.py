import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import requests

# --- CONFIG & API ---
st.set_page_config(page_title="Intelligence Portal", layout="wide")
GEMINI_API_KEY = "AIzaSyDPwcKpNTwJ-Gi2dyMMW-reTl01rm-61L4" # Add your key
genai.configure(api_key=GEMINI_API_KEY)

# --- LOGIN OVERRIDE ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    u = st.sidebar.text_input("Username")
    p = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if u == "Director" and p == "void2026":
            st.session_state['logged_in'] = True
            st.rerun()
    st.stop()

# --- SIDEBAR: SEARCH & NAVIGATION ---
with st.sidebar:
    st.title("👤 Director Dashboard")
    search_query = st.text_input("🔍 Instant Search", placeholder="Type a niche...")
    nav = st.radio("Go to:", ["Global Pulse", "Comparison Hub", "Script Architect"])

# --- DATA GENERATOR (Mock Data for Tabs) ---
df = pd.DataFrame({
    'Niche': ['AI Agents', 'Fitness Tech', 'SaaS', 'E-com'],
    'Trend_Score': [95, 70, 85, 60],
    'Status': ['🔥 Rising', '⚖️ Stable', '🔥 Rising', '📉 Dropping']
})

# --- TAB LOGIC ---
if nav == "Global Pulse":
    st.header("📈 Global Pulse Trends")
    # Instant Search Filtering
    display_df = df[df['Niche'].str.contains(search_query, case=False)] if search_query else df
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(display_df, x='Niche', y='Trend_Score', color='Status', template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Market Summary")
        for index, row in display_df.iterrows():
            st.write(f"**{row['Niche']}**: {row['Status']}")

elif nav == "Script Architect":
    st.header("💎 AI Script Architect")
    topic = st.text_input("Script Topic", value=search_query)
    
    if st.button("Generate Strategy"):
        try:
            # SWITCHED TO STABLE PRO MODEL
            model = genai.GenerativeModel('gemini-pro') 
            prompt = f"Viral script for {topic}. Hook, Body, SEO Keywords."
            response = model.generate_content(prompt)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"API Connection Error: {e}")
