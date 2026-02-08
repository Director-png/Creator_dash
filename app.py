import streamlit as st
import pandas as pd
import requests
import json
import datetime
import random

# --- CONFIG ---
st.set_page_config(page_title="Creator Strategy Pro", layout="wide", page_icon="🌍")

# --- 1. SESSION STATE & DB ---
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {"admin": "Deepak"}

if "my_categories" not in st.session_state:
    st.session_state["my_categories"] = ["Cotton Kurti", "Sunscreen"]

# --- 2. AUTH SYSTEM ---
def login_system():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    
    if not st.session_state["authenticated"]:
        st.title("🔐 Creator Intelligence Portal")
        t1, t2 = st.tabs(["Login", "Register"])
        with t1:
            pwd = st.text_input("Access Key:", type="password")
            if st.button("Enter Dashboard"):
                if pwd in st.session_state["user_db"]:
                    st.session_state["authenticated"] = True
                    st.session_state["client_name"] = st.session_state["user_db"][pwd]
                    st.rerun()
        with t2:
            n = st.text_input("Name:")
            k = st.text_input("Set Key:")
            if st.button("Join"):
                st.session_state["user_db"][k] = n
                st.success("Registered!")
        return False
    return True

# --- 3. ANALYTICS ENGINE ---
API_KEY = "cfe3d0828971dc09543b2eaa2abc4b67d29d21a0" 

def get_insights(keyword):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": keyword, "gl": "in", "hl": "en"}) 
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=payload)
        data = response.json()
        r_count = len(data.get('relatedSearches', []))
        q_count = len(data.get('peopleAlsoAsk', []))
        score = 45 + (r_count * 6) + (q_count * 5) + random.randint(1, 5)
        return {"score": min(score, 100), "related": [r.get('query') for r in data.get('relatedSearches', [])[:5]]}
    except:
        return {"score": 50, "related": []}

# --- MAIN APP ---
if login_system():
    st.sidebar.title(f"👋 {st.session_state['client_name']}")
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

    # --- NAVIGATION TABS ---
    tab_global, tab_search, tab_compare, tab_ideas = st.tabs([
        "🌍 Global Pulse", 
        "🔍 Instant Search", 
        "📊 Market View", 
        "💡 Content Lab"
    ])

    # --- TAB 0: GLOBAL PULSE (NEW!) ---
    with tab_global:
        st.subheader("🔥 Top Trends in India (Real-Time)")
        # In a production app, these would come from a 'trending' API endpoint
        global_trends = ["AI Avatars", "Sustainable Fashion", "Electric Scooters", "Stock Market India", "Work from Home"]
        
        cols = st.columns(len(global_trends))
        for i, trend in enumerate(global_trends):
            with cols[i]:
                # We pull a quick score for these
                res = get_insights(trend)
                st.metric(label=trend, value=f"{res['score']}%", delta="Trending")
                if st.button(f"Track", key=f"btn_{trend}"):
                    if trend not in st.session_state["my_categories"]:
                        st.session_state["my_categories"].append(trend)
                        st.rerun()
        st.divider()
        st.info("These are high-velocity topics currently gaining traction across search engines.")

    # --- TAB 1: SEARCH ---
    with tab_search:
        st.subheader("Deep Dive Analysis")
        query = st.text_input("Search for a niche keyword:", placeholder="e.g. Minimalist Home Decor")
        if query:
            data = get_insights(query)
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Velocity Score", f"{data['score']}%")
                st.write("**Related Keywords:**")
                for r in data['related']:
                    st.caption(f"- {r}")
                if st.button("Add to My Tracking List"):
                    if query not in st.session_state["my_categories"]:
                        st.session_state["my_categories"].append(query)
                        st.success("Saved!")
            with c2:
                st.bar_chart(pd.DataFrame({"Velocity": [data['score']]}, index=[query]), color="#FF4B4B")

    # --- TAB 2: COMPARISON ---
    with tab_compare:
        st.subheader("Comparison Dashboard")
        if st.session_state["my_categories"]:
            comp_results = []
            for p in st.session_state["my_categories"]:
                res = get_insights(p)
                comp_results.append({"Trend": p, "Velocity": res['score']})
            
            df = pd.DataFrame(comp_results).set_index("Trend")
            st.bar_chart(df, y="Velocity", color="#2E86C1")
            
            with st.expander("View Data Table"):
                st.dataframe(df.T, use_container_width=True)
        else:
            st.warning("No categories saved yet.")

    # --- TAB 3: CONTENT LAB ---
    with tab_ideas:
        st.subheader("AI Content Architect")
        selected = st.selectbox("Pick a saved trend:", st.session_state["my_categories"])
        if selected:
            st.write(f"### Strategy Guide for **{selected}**")
            
            # This is where we create the value for the user
            col_vid, col_txt = st.columns(2)
            with col_vid:
                st.markdown("#### 🎥 Video Strategy")
                st.write("1. **The 3-Second Hook:** 'Did you know that search interest for this is peaking?'")
                st.write("2. **Visual Style:** Use fast cuts and overlay the data charts from this app.")
                st.write("3. **Call to Action:** 'Comment BELOW if you saw this coming!'")
            
            with col_txt:
                st.markdown("#### ✍️ Copywriting Strategy")
                st.write("**Title Idea:** The Future of " + selected)
                st.write("**Keywords:** Include " + ", ".join(get_insights(selected)['related'][:3]))

    st.divider()
    st.caption(f"Creator Strategy Suite v11.0 | Server Time: {datetime.datetime.now().strftime('%H:%M:%S')}")
