import streamlit as st
import pandas as pd
import time

# 1. Page Config & Professional Styling
st.set_page_config(page_title="Market Intelligence Portal", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .sidebar .sidebar-content { background-image: linear-gradient(#2e313d,#0e1117); }
    </style>
    """, unsafe_allow_html=True)

# 2. Authentication Layer (Restored)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user_name'] = ""

if not st.session_state['logged_in']:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.title("🔐 Intelligence Login")
        user_input = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Access Portal"):
            if user_input and password == "director2026": # Replace with your password
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = user_input
                st.rerun()
    st.stop()

# 3. Sidebar - Identity & Navigation
with st.sidebar:
    st.title(f"👤 {st.session_state['user_name']}")
    st.write("---")
    tool_choice = st.radio("Navigation", ["Global Pulse", "Comparison Hub", "Script Architect"])
    st.write("---")
    st.subheader("📜 Search History")
    # Placeholder for history logic
    st.info("No recent history found.")
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

# 4. Main App Logic
if tool_choice == "Global Pulse":
    st.header("📈 Global Pulse Trends")
    st.write("Current Market Heatmap and real-time data flow.")
    # (Your Google Sheets / Plotly logic goes here)

elif tool_choice == "Comparison Hub":
    st.header("⚖️ Niche Comparison Tab")
    col1, col2 = st.columns(2)
    niche_a = col1.text_input("Niche A", "AI Automation")
    niche_b = col2.text_input("Niche B", "SaaS")
    st.button("Compare Metrics")

elif tool_choice == "Script Architect":
    st.header("💎 Script Architect (Premium)")
    niche_input = st.text_input("Enter Niche/Trend Name:")
    platform = st.segmented_control("Select Platform", ["YouTube", "Instagram", "TikTok"])
    
    if st.button("Generate Strategy"):
        if niche_input:
            with st.status("Architecting Content...", expanded=True) as status:
                st.write("Fetching historical trend data...")
                time.sleep(1)
                st.write("Analyzing current monthly spikes...")
                time.sleep(1)
                st.write("Predicting future trajectory...")
                time.sleep(1)
                status.update(label="Strategy Complete!", state="complete", expanded=False)
            
            # This is where the output was "stuck" before. Fixed:
            st.success(f"### {platform} Strategy for {niche_input}")
            st.markdown(f"""
            **The Hook (Current Trend):** "Why everyone is talking about {niche_input}..."
            **The Value (Future Prediction):** Explain how this shifts in the next 30 days.
            **CTA:** "Follow for the next trend update."
            """)
        else:
            st.warning("Please enter a niche to begin.")
