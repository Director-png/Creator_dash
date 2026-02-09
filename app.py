import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. THE FIX FOR THE IMPORT ERROR ---
try:
    from groq import Groq
except ImportError:
    st.error("🚨 System Error: Please ensure your file is NOT named 'groq.py'. Rename it to 'main_app.py'.")
    st.stop()

# --- 2. CONFIG & AUTH ---
st.set_page_config(page_title="Director Portal", layout="wide")

# Replace this with your key from https://console.groq.com/keys
GROQ_KEY = "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" 

if 'auth' not in st.session_state:
    st.session_state['auth'] = False

# --- 3. LOGIN GATE ---
if not st.session_state['auth']:
    st.title("🛡️ Director's Entrance")
    user = st.text_input("Username")
    passw = st.text_input("Password", type="password")
    if st.button("Unlock System"):
        if user == "Director" and passw == "void2026":
            st.session_state['auth'] = True
            st.rerun()
        else:
            st.error("Access Denied.")
    st.stop()

# --- 4. SIDEBAR (Instant Search) ---
with st.sidebar:
    st.header("🔍 Intelligence Hub")
    query = st.text_input("Instant Search", placeholder="Search niche...")
    nav = st.radio("Navigate", ["Global Pulse", "Script Architect"])
    if st.button("Logout"):
        st.session_state['auth'] = False
        st.rerun()

# --- 5. DATASET ---
df = pd.DataFrame({
    'Niche': ['AI Agents', 'SaaS', 'Fitness', 'E-com'],
    'Score': [95, 88, 72, 60],
    'Status': ['🔥 Rising', '🔥 Rising', '⚖️ Stable', '📉 Dropping']
})

# --- 6. MODULES ---
if nav == "Global Pulse":
    st.header("📈 Global Pulse Trends")
    # Instant filtering logic
    view_df = df[df['Niche'].str.contains(query, case=False)] if query else df
    
    fig = px.bar(view_df, x='Niche', y='Score', color='Status', 
                 template="plotly_dark", barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    st.table(view_df)

elif nav == "Script Architect":
    st.header("💎 Groq Script Architect")
    topic = st.text_input("Video Topic", value=query)
    
    if st.button("Generate Strategy"):
        if GROQ_KEY == "YOUR_GROQ_API_KEY":
            st.warning("Please insert your actual Groq API Key.")
        else:
            with st.spinner("Groq is thinking..."):
                try:
                    client = Groq(api_key=GROQ_KEY)
                    chat = client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": f"Write a viral script for {topic}."}]
                    )
                    st.markdown(chat.choices[0].message.content)
                except Exception as e:
                    st.error(f"API Connection Failed: {e}")
