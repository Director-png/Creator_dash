import streamlit as st
import subprocess
import sys

# --- EMERGENCY INSTALLER ---
# This forces the app to install groq even if requirements.txt failed
try:
    from groq import Groq
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "groq"])
    from groq import Groq

import pandas as pd
import plotly.express as px

# --- CONFIG ---
st.set_page_config(page_title="Director Portal", layout="wide")

# --- DATABASE / API KEYS ---
# Use Streamlit Secrets or paste your key here
GROQ_API_KEY = "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" 

# --- SESSION STATE (The Login Memory) ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# --- LOGIN GATE ---
if not st.session_state['authenticated']:
    st.title("🛡️ Director's Command")
    user = st.text_input("ID")
    pw = st.text_input("Key", type="password")
    if st.button("Unlock"):
        if user == "Director" and pw == "void2026":
            st.session_state['authenticated'] = True
            st.rerun()
    st.stop()

# --- SIDEBAR: INSTANT SEARCH ---
with st.sidebar:
    st.header("🔍 Global Search")
    # This search bar controls the charts AND the AI prompts
    search_query = st.text_input("Enter Niche", placeholder="e.g., Solar Tech").strip()
    
    st.divider()
    nav = st.radio("Intelligence Modules", ["Global Pulse", "Script Architect"])

# --- DATA FOR GLOBAL PULSE ---
# This simulates your Google Sheet data
data = pd.DataFrame({
    'Niche': ['AI Agents', 'SaaS', 'Solar Tech', 'E-com', 'Bio-Hacking'],
    'Growth': [98, 85, 92, 60, 45],
    'Status': ['🔥 Rising', '🔥 Rising', '🔥 Rising', '⚖️ Stable', '📉 Dropping']
})

# --- MODULE 1: GLOBAL PULSE ---
if nav == "Global Pulse":
    st.header("📈 Market Momentum")
    
    # Logic: Filter data based on sidebar search
    filtered_df = data[data['Niche'].str.contains(search_query, case=False)] if search_query else data
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(filtered_df, x='Niche', y='Growth', color='Status', 
                     template="plotly_dark", title="Market Heatmap")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Labels")
        st.write(filtered_df[['Niche', 'Status']])

# --- MODULE 2: SCRIPT ARCHITECT ---
elif nav == "Script Architect":
    st.header("💎 AI Strategy Generator")
    # Autofill topic from Sidebar search
    topic = st.text_input("Topic to Analyze", value=search_query)
    
    if st.button("Generate Groq Strategy"):
        client = Groq(api_key=GROQ_API_KEY)
        with st.spinner("Analyzing..."):
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a world-class viral marketer."},
                        {"role": "user", "content": f"Create a viral script and SEO tags for: {topic}"}
                    ],
                    model="llama3-8b-8192",
                )
                st.markdown(chat_completion.choices[0].message.content)
            except Exception as e:
                st.error(f"Error: {e}")
