import streamlit as st
import pandas as pd
import requests
import json
import datetime

# --- CONFIG ---
st.set_page_config(page_title="Creator Strategy Suite", layout="wide", page_icon="⚡")

# --- 1. USER & CATEGORY DATABASE ---
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {"void_admin": "Deepak (Admin)"}

if "my_categories" not in st.session_state:
    st.session_state["my_categories"] = ["Cotton Kurti", "Sunscreen"]

# --- 2. AUTH SYSTEM ---
def login_system():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["client_name"] = ""

    if not st.session_state["authenticated"]:
        st.title("🔐 Creator Intelligence Portal")
        tab1, tab2 = st.tabs(["Login", "Create Account"])
        with tab1:
            pwd_input = st.text_input("Access Key:", type="password", key="l_pwd")
            if st.button("Unlock Dashboard"):
                if pwd_input in st.session_state["user_db"]:
                    st.session_state["authenticated"] = True
                    st.session_state["client_name"] = st.session_state["user_db"][pwd_input]
                    st.rerun()
                else:
                    st.error("Key not found.")
        with tab2:
            new_name = st.text_input("Your Name:")
            new_key = st.text_input("Choose Access Key:", type="password")
            if st.button("Register & Login"):
                if new_key and new_name:
                    st.session_state["user_db"][new_key] = new_name
                    st.session_state["authenticated"] = True
                    st.session_state["client_name"] = new_name
                    st.rerun()
        return False
    return True

# --- 3. ANALYTICS ENGINE ---
API_KEY = "cfe3d0828971dc09543b2eaa2abc4b67d29d21a0" 

def get_real_trends(keyword):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": keyword, "gl": "in", "hl": "en"}) 
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=payload)
        data = response.json()
        related = len(data.get('relatedSearches', []))
        questions = len(data.get('peopleAlsoAsk', []))
        organic = data.get('organic', [])
        snippet_text = " ".join([obj.get('snippet', '').lower() for obj in organic])
        mention_count = snippet_text.count(keyword.lower())
        score = 35 + (related * 6) + (questions * 4) + (mention_count * 1.5)
        return min(round(score), 100)
    except:
        return 50 

# --- MAIN APP ---
if login_system():
    # --- SIDEBAR ---
    st.sidebar.title(f"👋 {st.session_state['client_name']}")
    
    st.sidebar.header("🔍 Quick Trend Search")
    instant_query = st.sidebar.text_input("Search any keyword:", key="instant_search", placeholder="Type & hit Enter...")

    st.sidebar.divider()

    st.sidebar.header("📌 My Saved Trackers")
    new_cat = st.sidebar.text_input("Save a category to list:", placeholder="e.g. AI Tools")
    if st.sidebar.button("Save to List"):
        if new_cat and new_cat not in st.session_state["my_categories"]:
            st.session_state["my_categories"].append(new_cat)
            st.rerun()

    presets = st.sidebar.multiselect(
        "Monitor these trends:", 
        options=st.session_state["my_categories"],
        default=st.session_state["my_categories"]
    )

    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

    # --- MAIN UI ---
    st.title("📈 Creator Intelligence Dashboard")

    # --- SECTION A: INSTANT SEARCH VISUALS (THE FIX) ---
    if instant_query:
        st.markdown(f"### ⚡ Analysis for: **{instant_query.upper()}**")
        with st.spinner(f"Fetching live data for {instant_query}..."):
            v_score = get_real_trends(instant_query)
            
            # Create a mini dataframe just for this search to show a chart
            instant_df = pd.DataFrame({"Trend": [instant_query], "Velocity": [v_score]})
            
            col_chart, col_stats = st.columns([2, 1])
            
            with col_chart:
                # This bar chart will now appear instantly
                st.bar_chart(instant_df.set_index("Trend"), color="#FF4B4B")
            
            with col_stats:
                status = "🔥 EXPLODING" if v_score > 75 else "🚀 RISING" if v_score > 55 else "⚖️ STABLE"
                st.metric("Velocity Score", f"{v_score}%")
                st.subheader(f"Status: {status}")
                
                if st.button(f"➕ Save '{instant_query}'"):
                    if instant_query not in st.session_state["my_categories"]:
                        st.session_state["my_categories"].append(instant_query)
                        st.rerun()

            if v_score > 70: 
                st.balloons()
        st.divider()
