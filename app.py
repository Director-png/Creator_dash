import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# --- 1. CONFIG ---
st.set_page_config(page_title="Director Portal", layout="wide")

# Set this in Streamlit Secrets for security
API_KEY = st.secrets.get("GEMINI_KEY", "AIzaSyDPwcKpNTwJ-Gi2dyMMW-reTl01rm-61L4")
genai.configure(api_key=API_KEY)

# --- 2. THE ACCESS SYSTEM (Login) ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🛡️ Access Restricted")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Authenticate"):
        if u == "Director" and p == "admin": # Your Master Key
            st.session_state['auth'] = True
            st.rerun()
        else:
            st.error("Invalid Credentials")
    st.stop()

# --- 3. THE COMMAND CENTER (Post-Login) ---
with st.sidebar:
    st.header(f"Welcome, Director")
    # THE INSTANT SEARCH
    search_query = st.text_input("🔍 Instant Search", placeholder="e.g. AI Fitness")
    nav = st.radio("Intelligence Modules", ["Global Pulse", "Comparison Hub", "Script Architect"])

# --- 4. TABS & VISUALS ---
if nav == "Global Pulse":
    st.header("📈 Global Pulse Trends")
    
    # Mock Data for Charts (Replace with your Sheet Read URL later)
    df = pd.DataFrame({
        'Niche': ['AI Agents', 'SaaS', 'E-com', 'Bio-Hacking'],
        'Momentum': [95, 88, 62, 45],
        'Status': ['🔥 Rising', '🔥 Rising', '⚖️ Stable', '📉 Dropping']
    })
    
    # Filter based on Instant Search
    if search_query:
        df = df[df['Niche'].str.contains(search_query, case=False)]

    col1, col2 = st.columns([2, 1])
    with col1:
        # Professional Dark Chart
        fig = px.bar(df, x='Niche', y='Momentum', color='Status', 
                     template="plotly_dark", title="Market Heatmap")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Market Labels")
        st.write(df[['Niche', 'Status']])

elif nav == "Script Architect":
    st.header("💎 AI Script Strategy")
    topic = st.text_input("Target Topic", value=search_query)
    
    if st.button("Generate Strategy"):
        try:
            # Using the absolute latest stable model call
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"Viral script strategy for {topic}. Hooks, SEO, and Body.")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"AI Engine Offline: {e}")
