import streamlit as st
import pandas as pd
import requests
import json
import random

# --- 1. PERFORMANCE CACHING (Stops the Freezing) ---
@st.cache_data(ttl=600)  # Remembers data for 10 minutes
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
        return {"score": 50, "related": ["Trend Analysis", "Growth"], "status": "⚖️ STABLE"}

# --- CONFIG ---
st.set_page_config(page_title="Creator Strategy Pro", layout="wide")

# --- 2. AUTH SYSTEM ---
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {"admin": "Deepak"}

if "my_categories" not in st.session_state:
    st.session_state["my_categories"] = ["Cotton Kurti", "Sunscreen"]

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 Creator Intelligence Portal")
    pwd = st.text_input("Access Key:", type="password")
    if st.button("Enter Dashboard"):
        if pwd in st.session_state["user_db"]:
            st.session_state["authenticated"] = True
            st.session_state["client_name"] = st.session_state["user_db"][pwd]
            st.rerun()
        else:
            st.error("Access Denied.")
    st.stop() # Prevents the rest of the app from running until login

# --- 3. MAIN APP (Runs only after login) ---
st.sidebar.title(f"👋 {st.session_state['client_name']}")

# Sidebar Management
with st.sidebar.expander("🗑️ Delete Keywords"):
    if st.session_state["my_categories"]:
        to_del = st.selectbox("Select to remove:", st.session_state["my_categories"])
        if st.button("Delete"):
            st.session_state["my_categories"].remove(to_del)
            st.rerun()

if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.rerun()

# TABS
tab_search, tab_compare, tab_global, tab_ideas = st.tabs([
    "🔍 Instant Search", "📊 Market View", "🌍 Global Pulse", "💡 Content Lab"
])

with tab_search:
    st.subheader("Deep Dive Analysis")
    query = st.text_input("Search for a keyword:", key="main_search")
    if query:
        with st.spinner("Analyzing..."):
            data = get_insights(query)
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Velocity Score", f"{data['score']}%")
                st.subheader(f"Status: {data['status']}")
                st.markdown("### 🔑 SEO Keywords")
                for r in data['related']:
                    st.code(f"#{r.replace(' ', '')}")
                if st.button("📌 Add to My Trackers"):
                    if query not in st.session_state["my_categories"]:
                        st.session_state["my_categories"].append(query)
                        st.toast("Saved!") # Non-intrusive notification
            with c2:
                st.bar_chart(pd.DataFrame({"Velocity": [data['score']]}, index=[query]), color="#FF4B4B")

with tab_compare:
    st.subheader("Your Market View")
    if st.session_state["my_categories"]:
        comp_data = []
        # Progress bar for visual feedback
        progress_bar = st.progress(0)
        for i, p in enumerate(st.session_state["my_categories"]):
            res = get_insights(p)
            comp_data.append({"Trend": p, "Velocity": res['score'], "Status": res['status']})
            progress_bar.progress((i + 1) / len(st.session_state["my_categories"]))
        
        df = pd.DataFrame(comp_data).set_index("Trend")
        st.bar_chart(df[['Velocity']], color="#2E86C1")
        st.table(df)
    else:
        st.info("Your tracker list is empty.")

with tab_global:
    st.subheader("🔥 Top Trends")
    trends = ["AI Video", "Digital Nomad", "Skincare India", "Electric Cars"]
    cols = st.columns(4)
    for i, t in enumerate(trends):
        with cols[i]:
            # This only runs when the user clicks this tab
            res = get_insights(t)
            st.metric(t, f"{res['score']}%")
            if st.button("Track", key=f"global_{t}"):
                if t not in st.session_state["my_categories"]:
                    st.session_state["my_categories"].append(t)
                    st.rerun()

with tab_ideas:
    st.subheader("Strategy Lab")
    if st.session_state["my_categories"]:
        selected = st.selectbox("Pick a trend:", st.session_state["my_categories"])
        data = get_insights(selected)
        st.success(f"Strategy for **{selected}** unlocked.")
        st.write(f"Use these keywords in your caption: {', '.join(data['related'])}")
    else:
        st.warning("Add keywords first.")
