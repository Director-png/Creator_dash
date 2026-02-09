import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq # Swapped from Google
import requests

# --- CONFIG & AUTH ---
st.set_page_config(page_title="Director Command Center", layout="wide")

# NEW IMPORT LOGIC
try:
    from groq import Groq
except ImportError:
    st.error("Groq library not found. Please check your requirements.txt and redeploy.")

# Replace with your Groq API Key
GROQ_API_KEY = "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"

# --- LOGIN OVERRIDE ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🛡️ Secure Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Access System"):
        if u == "Director" and p == "admin":
            st.session_state['logged_in'] = True
            st.rerun()
    st.stop()

# --- SIDEBAR: INSTANT SEARCH & SEO ---
with st.sidebar:
    st.header("🔍 Global Intelligence")
    search_query = st.text_input("Instant Search", placeholder="e.g. AI Fitness")
    
    if search_query:
        st.subheader("SEO Quick-Stack")
        st.code(f"Keywords: {search_query}, Viral, 2026, Growth")
        st.info(f"Hook: 'They don't want you to know this about {search_query}...'")
    
    nav = st.radio("Modules", ["Global Pulse", "Comparison Hub", "Script Architect"])

# --- DATA ENGINE ---
df = pd.DataFrame({
    'Niche': ['AI Agents', 'SaaS', 'Bio-Hacking', 'Fitness', 'E-com'],
    'Score': [98, 85, 40, 75, 60],
    'Status': ['🔥 Rising', '🔥 Rising', '📉 Dropping', '⚖️ Stable', '⚖️ Stable']
})

# --- MODULES ---
if nav == "Global Pulse":
    st.header("📈 Global Pulse Trends")
    display_df = df[df['Niche'].str.contains(search_query, case=False)] if search_query else df
    
    fig = px.bar(display_df, x='Niche', y='Score', color='Status', 
                 template="plotly_dark", color_discrete_map={'🔥 Rising': 'red', '⚖️ Stable': 'blue', '📉 Dropping': 'gray'})
    st.plotly_chart(fig, use_container_width=True)
    st.table(display_df)

elif nav == "Script Architect":
    st.header("💎 Groq-Powered Script Architect")
    topic = st.text_input("Script Topic", value=search_query)
    
    if st.button("Generate Strategy (Ultra-Fast)"):
        try:
            client = Groq(api_key=GROQ_API_KEY)
            completion = client.chat.completions.create(
                model="llama3-8b-8192", # Extremely fast and reliable
                messages=[
                    {"role": "system", "content": "You are a viral marketing strategist."},
                    {"role": "user", "content": f"Create a viral script for {topic} with 3 hooks and SEO keywords."}
                ]
            )
            st.markdown(completion.choices[0].message.content)
        except Exception as e:
            st.error(f"Groq Connection Error: {e}")

