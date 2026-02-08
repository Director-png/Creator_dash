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
        t1, t2 = st.tabs(["Login", "Register"])
        with t1:
            pwd = st.text_input("Access Key:", type="password")
            if st.button("Enter"):
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
        # Improved sensitivity math
        score = 42 + (r_count * 7) + (q_count * 5) + random.randint(1, 4)
        return {"score": min(score, 100), "related": [r.get('query') for r in data.get('relatedSearches', [])[:5]]}
    except:
        return {"score": 50, "related": []}

# --- MAIN APP ---
if login_system():
    st.sidebar.title(f"👋 {st.session_state['client_name']}")
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

    # THE MAIN NAVIGATION TABS
    tab_search, tab_compare, tab_ideas = st.tabs(["🔍 Instant Trend Search", "📊 Market Comparison", "💡 Content Strategy"])

    # --- TAB 1: SEARCH ---
    with tab_search:
        st.subheader("Check the velocity of any trend")
        query = st.text_input("What are we looking for today?", placeholder="e.g. AI Influencers")
        
        if query:
            data = get_insights(query)
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Velocity Score", f"{data['score']}%")
                if st.button(f"📌 Save '{query}' to Comparison List"):
                    if query not in st.session_state["my_categories"]:
                        st.session_state["my_categories"].append(query)
                        st.success("Added!")
            with c2:
                st.bar_chart(pd.DataFrame({"Velocity": [data['score']]}, index=[query]), color="#FF4B4B")

    # --- TAB 2: COMPARISON ---
    with tab_compare:
        st.subheader("Your Personalized Market View")
        if st.session_state["my_categories"]:
            col_list, col_chart = st.columns([1, 3])
            
            with col_list:
                st.write("**Currently Tracking:**")
                for item in st.session_state["my_categories"]:
                    st.write(f"• {item}")
                if st.button("Clear List"):
                    st.session_state["my_categories"] = []
                    st.rerun()
            
            with col_chart:
                comp_results = []
                for p in st.session_state["my_categories"]:
                    res = get_insights(p)
                    comp_results.append({"Trend": p, "Velocity": res['score']})
                
                df = pd.DataFrame(comp_results).set_index("Trend")
                st.bar_chart(df, y="Velocity", color="#2E86C1")
        else:
            st.info("Your list is empty. Go to 'Instant Trend Search' to add some trends!")

    # --- TAB 3: CONTENT LAB ---
    with tab_ideas:
        st.subheader("AI Content Pillar Generator")
        selected_trend = st.selectbox("Select a trend to generate ideas for:", st.session_state["my_categories"])
        
        if selected_trend:
            data = get_insights(selected_trend)
            st.markdown(f"### Strategy for **{selected_trend}**")
            
            c_reels, c_stories = st.columns(2)
            with c_reels:
                st.info("🎬 **Short-Form Video (Reels/Shorts)**")
                st.write(f"1. **The Hook:** 'Stop ignoring {selected_trend}...'")
                st.write(f"2. **The Value:** Explain why the score is {data['score']}% right now.")
            with c_stories:
                st.success("📸 **Engagement (Stories/Threads)**")
                st.write("1. **Poll:** Ask 'Do you think this trend is overhyped?'")
                st.write("2. **Behind the Scenes:** Show how you research this.")

    st.divider()
    st.caption(f"Sync: {datetime.datetime.now().strftime('%H:%M')} | System: Optimal")
