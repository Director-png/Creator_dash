import streamlit as st
import pandas as pd
import requests
import json
import datetime
import random

# --- CONFIG ---
st.set_page_config(page_title="Creator Strategy Pro", layout="wide", page_icon="🚀")

# --- 1. SESSION STATE ---
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
        pwd = st.text_input("Access Key:", type="password")
        if st.button("Enter Dashboard"):
            if pwd in st.session_state["user_db"]:
                st.session_state["authenticated"] = True
                st.session_state["client_name"] = st.session_state["user_db"][pwd]
                st.rerun()
        return False
    return True

# --- 3. REFINED SEO ENGINE ---
API_KEY = "cfe3d0828971dc09543b2eaa2abc4b67d29d21a0" 

def get_insights(keyword):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": keyword, "gl": "in", "hl": "en"}) 
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        data = response.json()
        
        # 1. Try to get Related Searches
        related = [r.get('query') for r in data.get('relatedSearches', [])]
        
        # 2. If Related is empty, pull from "People Also Ask" questions
        if not related:
            related = [q.get('question') for q in data.get('peopleAlsoAsk', [])]
            
        # 3. If STILL empty, pull from Organic Titles (Final Backup)
        if not related:
            related = [o.get('title')[:30] + "..." for o in data.get('organic', [])[:5]]

        score = 40 + (len(related) * 5) + random.randint(5, 15)
        
        return {
            "score": min(score, 100), 
            "related": related[:6], # Return top 6 keywords
            "status": "🔥 EXPLODING" if score > 75 else "🚀 RISING" if score > 55 else "⚖️ STABLE"
        }
    except Exception as e:
        return {"score": 50, "related": ["Market Trend", "Analysis", "Growth"], "status": "⚖️ STABLE"}

# --- MAIN APP ---
if login_system():
    st.sidebar.title(f"👋 {st.session_state['client_name']}")
    
    # DELETE MANAGEMENT
    st.sidebar.header("🗑️ Manage Trackers")
    if st.session_state["my_categories"]:
        to_del = st.sidebar.selectbox("Remove a keyword:", ["-- Select --"] + st.session_state["my_categories"])
        if st.sidebar.button("Confirm Delete"):
            if to_del != "-- Select --":
                st.session_state["my_categories"].remove(to_del)
                st.rerun()

    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

    # TABS
    tab_global, tab_search, tab_compare, tab_ideas = st.tabs([
        "🌍 Global Pulse", "🔍 Instant Search", "📊 Market View", "💡 Content Lab"
    ])

    # --- TAB 1: INSTANT SEARCH ---
    with tab_search:
        st.subheader("Deep Dive Analysis")
        query = st.text_input("Search for a keyword:", placeholder="Type and hit Enter...")
        
        if query:
            with st.spinner("Mining SEO Data..."):
                data = get_insights(query)
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.metric("Velocity Score", f"{data['score']}%")
                    st.subheader(f"Status: {data['status']}")
                    
                    st.markdown("### 🔑 SEO Keywords")
                    if data['related']:
                        for r in data['related']:
                            st.code(f"#{r.replace(' ', '')}") # Displayed as copyable hashtags
                    else:
                        st.warning("No specific keywords found for this niche.")
                    
                    if st.button("📌 Add to Tracking List"):
                        if query not in st.session_state["my_categories"]:
                            st.session_state["my_categories"].append(query)
                            st.success("Added!")

                with c2:
                    st.bar_chart(pd.DataFrame({"Velocity": [data['score']]}, index=[query]), color="#FF4B4B")

    # --- TAB 2: MARKET VIEW ---
    with tab_compare:
        st.subheader("Your Comparison Dashboard")
        if st.session_state["my_categories"]:
            comp_data = []
            for p in st.session_state["my_categories"]:
                res = get_insights(p)
                comp_data.append({"Trend": p, "Velocity": res['score'], "Status": res['status']})
            
            df = pd.DataFrame(comp_data).set_index("Trend")
            st.bar_chart(df[['Velocity']], color="#2E86C1")
            st.table(df)
        else:
            st.info("List is empty.")

    # --- TAB 3: CONTENT LAB ---
    with tab_ideas:
        st.subheader("Content Strategy Generator")
        if st.session_state["my_categories"]:
            selected = st.selectbox("Choose a trend:", st.session_state["my_categories"])
            data = get_insights(selected)
            
            st.markdown(f"## 💎 Strategy for **{selected}**")
            col_a, col_b = st.columns(2)
            with col_a:
                st.success("🎬 **Viral Hook Ideas**")
                st.write(f"- 'I found the secret to {selected}...'")
                st.write(f"- 'Stop doing this if you like {selected}.'")
            with col_b:
                st.info("🏷️ **SEO Meta Tags**")
                # This ensures the Content Lab also shows the keywords
                st.write(", ".join(data['related']))
        else:
            st.warning("Add keywords first.")

    # --- TAB 0: GLOBAL ---
    with tab_global:
        st.subheader("🔥 Trending Right Now")
        trends = ["AI Video", "Digital Nomad Life", "Skincare Routine", "Crypto News India"]
        cols = st.columns
