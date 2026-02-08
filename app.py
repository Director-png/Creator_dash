import streamlit as st
import pandas as pd
import requests
import json
import random

# --- 1. SETTINGS & THEME ---
st.set_page_config(
    page_title="Creator Intelligence Pro", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Custom CSS for a "Premium" Look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PERFORMANCE CACHING ---
@st.cache_data(ttl=600)
def get_insights(keyword):
    API_KEY = "cfe3d0828971dc09543b2eaa2abc4b67d29d21a0" 
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": keyword, "gl": "in", "hl": "en"}) 
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        data = response.json()
        related = [r.get('query') for r in data.get('relatedSearches', [])]
        if not related:
            related = [q.get('question') for q in data.get('peopleAlsoAsk', [])]
        score = 40 + (len(related) * 5) + random.randint(5, 15)
        return {
            "score": min(score, 100), 
            "related": related[:6],
            "status": "🔥 EXPLODING" if score > 75 else "🚀 RISING" if score > 55 else "⚖️ STABLE"
        }
    except Exception:
        return {"score": 50, "related": ["Viral Content", "SEO Optimization"], "status": "⚖️ STABLE"}

# --- 3. FIXING ACCESS DENIED ---
if "user_db" not in st.session_state:
    # Use lowercase keys for easier matching
    st.session_state["user_db"] = {"admin": "Deepak"}

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🛡️ Secure Creator Portal")
    
    # Header Image for Premium Feel
    st.image("https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80", caption="Market Intelligence at your fingertips")
    
    col1, col2 = st.columns(2)
    with col1:
        # We convert input to .lower() to ensure "Admin" and "admin" both work
        input_key = st.text_input("Enter Access Key:", type="password").lower().strip()
        
        if st.button("Unlock Dashboard"):
            if input_key in st.session_state["user_db"]:
                st.session_state["authenticated"] = True
                st.session_state["client_name"] = st.session_state["user_db"][input_key]
                st.rerun()
            else:
                st.error(f"Access Denied. '{input_key}' is not in our database.")
    st.stop()

# --- 4. THE MAIN DASHBOARD ---
st.sidebar.title(f"👤 {st.session_state['client_name']}")

# PREFERENCES
with st.sidebar.expander("🎨 Dashboard Settings"):
    st.write("UI optimized for High-Resolution displays.")
    if st.button("Reset Session"):
        st.session_state["my_categories"] = ["Cotton Kurti", "Sunscreen"]
        st.rerun()

if st.sidebar.button("Log Out"):
    st.session_state["authenticated"] = False
    st.rerun()

# --- APP TABS ---
tab_search, tab_compare, tab_global, tab_lab = st.tabs([
    "🔍 Search Engine", "📊 Market Comparison", "🌍 Global Trends", "💡 Content Strategy"
])

if "my_categories" not in st.session_state:
    st.session_state["my_categories"] = ["Cotton Kurti", "Sunscreen"]

with tab_search:
    st.subheader("Predictive Trend Analysis")
    query = st.text_input("Niche Topic:", placeholder="e.g., Organic Skincare")
    if query:
        data = get_insights(query)
        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Market Velocity", f"{data['score']}%")
            st.info(f"Verdict: **{data['status']}**")
            st.markdown("---")
            st.write("**Smart Tags:**")
            for tag in data['related']:
                st.code(f"#{tag.replace(' ', '')}")
            if st.button("Add to Strategy Board"):
                if query not in st.session_state["my_categories"]:
                    st.session_state["my_categories"].append(query)
                    st.toast(f"{query} added!")
        with c2:
            st.bar_chart(pd.DataFrame({"Velocity": [data['score']]}, index=[query]), color="#636EFA")

with tab_compare:
    st.subheader("Your Strategic Overview")
    if st.session_state["my_categories"]:
        # Sidebar-based deletion to keep the main view clean
        to_del = st.sidebar.selectbox("Prune Trackers:", ["-- Select --"] + st.session_state["my_categories"])
        if st.sidebar.button("Remove Selected"):
            if to_del != "-- Select --":
                st.session_state["my_categories"].remove(to_del)
                st.rerun()

        comp_data = []
        for p in st.session_state["my_categories"]:
            res = get_insights(p)
            comp_data.append({"Trend": p, "Velocity": res['score'], "Status": res['status']})
        
        df = pd.DataFrame(comp_data).set_index("Trend")
        st.bar_chart(df[['Velocity']], color="#00CC96")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Strategy board is empty.")

with tab_global:
    st.subheader("Real-Time India Market Pulse")
    trends = ["AI Avatars", "Sustainable Home", "Electric Vehicles", "Passive Income"]
    cols = st.columns(4)
    for i, t in enumerate(trends):
        with cols[i]:
            res = get_insights(t)
            st.metric(t, f"{res['score']}%")
            if st.button("Track", key=f"g_{t}"):
                if t not in st.session_state["my_categories"]:
                    st.session_state["my_categories"].append(t)
                    st.rerun()

with tab_lab:
    st.subheader("Content Creation Lab")
    if st.session_state["my_categories"]:
        choice = st.selectbox("Select a trend to build strategy:", st.session_state["my_categories"])
        data = get_insights(choice)
        st.markdown(f"### Strategy for **{choice}**")
        
        col_v, col_t = st.columns(2)
        with col_v:
            st.subheader("🎬 Video Production")
            st.write("- Start with: '3 Reasons why " + choice + " is taking over...'")
            st.write("- Transition: Show the " + str(data['score']) + "% growth stats.")
        with col_t:
            st.subheader("📝 Caption/SEO")
            st.write("Keywords: " + ", ".join(data['related']))
            
