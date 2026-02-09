import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import requests

# --- 1. CONFIG & AUTH ---
st.set_page_config(page_title="Director Command Center", layout="wide")

# Use a sidebar login to keep the main area clean
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

with st.sidebar:
    st.title("🔐 Secure Access")
    if not st.session_state['auth']:
        user = st.text_input("Director ID")
        pw = st.text_input("Access Key", type="password")
        if st.button("Unlock System"):
            if user == "Director" and pw == "admin":
                st.session_state['auth'] = True
                st.rerun()
            else:
                st.error("Access Denied")
        st.stop()
    
    st.success("Authorized: Director")
    st.write("---")
    # INSTANT SEARCH IN SIDEBAR
    query = st.text_input("🔍 Instant Niche Search", placeholder="e.g. AI SaaS")
    nav = st.radio("Intelligence Modules", ["Global Pulse", "Comparison Hub", "Script Architect"])

# --- 2. DATA ENGINE (The "Rising/Stable" Logic) ---
data = pd.DataFrame({
    'Niche': ['AI Agents', 'Green Tech', 'SaaS', 'Bio-Hacking', 'Fitness'],
    'Score': [98, 75, 88, 55, 72],
    'Status': ['🔥 Rising', '⚖️ Stable', '🔥 Rising', '📉 Dropping', '⚖️ Stable']
})

# --- 3. TAB LOGIC ---
if nav == "Global Pulse":
    st.header("📈 Global Pulse Trends")
    
    # Filtering by Search Query
    view_df = data[data['Niche'].str.contains(query, case=False)] if query else data
    
    # Displaying Status Metrics
    m1, m2, m3 = st.columns(3)
    if not view_df.empty:
        m1.metric("Top Niche", view_df.iloc[0]['Niche'], view_df.iloc[0]['Status'])
    
    # The Chart
    fig = px.bar(view_df, x='Niche', y='Score', color='Status', 
                 color_discrete_map={'🔥 Rising': 'red', '⚖️ Stable': 'cyan', '📉 Dropping': 'gray'},
                 template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    st.table(view_df)

elif nav == "Script Architect":
    st.header("💎 AI Script Architect")
    topic = st.text_input("Topic", value=query)
    
    if st.button("Generate Strategy"):
        try:
            genai.configure(api_key="YOUR_ACTUAL_API_KEY") # Ensure this is correct
            # Stable Model Call
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"Viral script strategy for {topic}. Hooks and SEO.")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"System Offline: {e}")
            st.info("Check if requirements.txt is uploaded to GitHub.")
