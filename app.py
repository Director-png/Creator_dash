import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq 

# --- CONFIG ---
st.set_page_config(page_title="Director Command Center", layout="wide")

# Replace with your key from console.groq.com
GROQ_API_KEY = "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"

# --- SIDEBAR & SEARCH ---
with st.sidebar:
    st.title("👤 Director Dashboard")
    search_query = st.text_input("🔍 Instant Search", placeholder="e.g. AI Fitness")
    nav = st.radio("Intelligence Modules", ["Global Pulse", "Comparison Hub", "Script Architect"])

# --- TAB: GLOBAL PULSE ---
if nav == "Global Pulse":
    st.header("📈 Global Pulse Trends")
    # This data is currently "local" - we can link it to your Google Sheet next
    df = pd.DataFrame({
        'Niche': ['AI Agents', 'SaaS', 'Bio-Hacking', 'E-com'],
        'Momentum': [95, 88, 45, 60],
        'Status': ['🔥 Rising', '🔥 Rising', '📉 Dropping', '⚖️ Stable']
    })
    
    # Instant Search logic
    if search_query:
        df = df[df['Niche'].str.contains(search_query, case=False)]

    fig = px.bar(df, x='Niche', y='Momentum', color='Status', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# --- TAB: SCRIPT ARCHITECT ---
elif nav == "Script Architect":
    st.header("💎 AI Script Architect (Groq)")
    topic = st.text_input("Content Topic", value=search_query)
    
    if st.button("Generate Strategy"):
        if not GROQ_API_KEY:
            st.error("Please add your Groq API Key to the code.")
        else:
            try:
                client = Groq(api_key=GROQ_API_KEY)
                # Using llama3-8b for maximum speed
                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": f"Create a viral script for {topic}."}]
                )
                st.markdown(completion.choices[0].message.content)
            except Exception as e:
                st.error(f"System Error: {e}")
