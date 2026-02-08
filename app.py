import streamlit as st
import pandas as pd
import requests
import json
import datetime
import random

# --- CONFIG ---
st.set_page_config(page_title="Creator Strategy Pro", layout="wide", page_icon="🎯")

# --- 1. SESSION STATE ---
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {"admin": "Deepak"}

if "my_categories" not in st.session_state:
    # Initialize with some defaults
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
        score = 40 + (r_count * 7) + (q_count * 5) + random.randint(1, 5)
        return {
            "score": min(score, 100), 
            "related": [r.get('query') for r in data.get('relatedSearches', [])[:5]],
            "status": "🔥 EXPLODING" if score > 75 else "🚀 RISING" if score > 55 else "⚖️ STABLE"
        }
    except:
        return {"score": 50, "related": [], "status": "⚖️ STABLE"}

# --- MAIN APP ---
if login_system():
    st.sidebar.title(f"👋 {st.session_state['client_name']}")
    
    # --- DELETE OPTION IN SIDEBAR ---
    st.sidebar.header("🗑️ Manage Trackers")
    if st.session_state["my_categories"]:
        item_to_delete = st.sidebar.selectbox("Select keyword to remove:", ["-- Select --"] + st.session_state["my_categories"])
        if st.sidebar.button("Remove from List"):
            if item_to_delete != "-- Select --":
                st.session_state["my_categories"].remove(item_to_delete)
                st.sidebar.success(f"Deleted {item_to_delete}")
                st.rerun()
    
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

    # --- NAVIGATION TABS ---
    tab_global, tab_search, tab_compare, tab_ideas = st.tabs([
        "🌍 Global Pulse", "🔍 Instant Search", "📊 Market View", "💡 Content Lab"
    ])

    # --- TAB 0: GLOBAL PULSE ---
    with tab_global:
        st.subheader("🔥 Top Trends in India")
        global_trends = ["AI Avatars", "Sustainable Fashion", "Electric Scooters", "Stock Market India"]
        cols = st.columns(len(global_trends))
        for i, trend in enumerate(global_trends):
            with cols[i]:
                res = get_insights(trend)
                st.metric(label=trend, value=f"{res['score']}%")
                st.caption(res['status'])
                if st.button("Track", key=f"global_{trend}"):
                    if trend not in st.session_state["my_categories"]:
                        st.session_state["my_categories"].append(trend)
                        st.rerun()

    # --- TAB 1: SEARCH (Restored Status) ---
    with tab_search:
        st.subheader("Deep Dive Analysis")
        query = st.text_input("Search for a keyword:", placeholder="e.g. Minimalist Home Decor")
        if query:
            data = get_insights(query)
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Velocity Score", f"{data['score']}%")
                # RESTORED STATUS TEXT
                st.subheader(f"Status: {data['status']}")
                
                st.write("**Related Keywords:**")
                for r in data['related']:
                    st.caption(f"- {r}")
                
                if st.button("Add to My List"):
                    if query not in st.session_state["my_categories"]:
                        st.session_state["my_categories"].append(query)
                        st.success("Saved!")
            with c2:
                st.bar_chart(pd.DataFrame({"Velocity": [data['score']]}, index=[query]), color="#FF4B4B")

    # --- TAB 2: COMPARISON (Vertical Bars) ---
    with tab_compare:
        st.subheader("Comparison Dashboard")
        if st.session_state["my_categories"]:
            comp_results = []
            for p in st.session_state["my_categories"]:
                res = get_insights(p)
                comp_results.append({"Trend": p, "Velocity": res['score'], "Status": res['status']})
            
            df = pd.DataFrame(comp_results).set_index("Trend")
            st.bar_chart(df[['Velocity']], color="#2E86C1")
            
            # Show table with the status labels included
            st.table(df)
        else:
            st.info("Tracking list is empty. Add keywords from 'Instant Search'.")

    # --- TAB 3: CONTENT LAB ---
    with tab_ideas:
        st.subheader("AI Content Architect")
        if st.session_state["my_categories"]:
            selected = st.selectbox("Pick a saved trend:", st.session_state["my_categories"])
            data = get_insights(selected)
            st.write(f"### Strategy for: **{selected}** ({data['status']})")
            
            c_vid, c_txt = st.columns(2)
            with c_vid:
                st.markdown("#### 🎥 Video Strategy")
                st.write("1. **The Hook:** 'Everyone is talking about " + selected + "...'")
                st.write(f"2. **The Logic:** Explain why it has a {data['score']}% growth score.")
            with c_txt:
                st.markdown("#### ✍️ Copywriting Tips")
                st.write(f"Target SEO Keywords: {', '.join(data['related'][:3])}")
        else:
            st.warning("Save some trends first to unlock the Content Lab!")

    st.caption(f"Creator Strategy Suite v12.0 | Build Optimized")
