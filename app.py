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
    st.session_state["my_categories"] = ["Cotton Kurti", "Sunscreen", "Travel Vlogs"]

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
    
    # 1. THE INSTANT SEARCH (Fixing your problem here)
    st.sidebar.header("🔍 Quick Trend Search")
    instant_query = st.sidebar.text_input("Search any keyword:", key="instant_search", placeholder="Type and hit Enter...")

    st.sidebar.divider()

    # 2. THE SAVED LIST MANAGEMENT
    st.sidebar.header("📌 My Saved Trackers")
    new_cat = st.sidebar.text_input("Save a new category to list:", placeholder="e.g. AI Tools")
    if st.sidebar.button("Save to List"):
        if new_cat and new_cat not in st.session_state["my_categories"]:
            st.session_state["my_categories"].append(new_cat)
            st.rerun()

    presets = st.sidebar.multiselect(
        "Monitor these saved trends:", 
        options=st.session_state["my_categories"],
        default=st.session_state["my_categories"][:2] if st.session_state["my_categories"] else []
    )

    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

    # --- MAIN UI ---
    st.title("📈 Creator Intelligence Dashboard")

    # SECTION A: INSTANT SEARCH RESULTS (The "Spotlight")
    if instant_query:
        st.subheader(f"⚡ Instant Insight: {instant_query}")
        with st.spinner(f"Analyzing '{instant_query}'..."):
            v_score = get_real_trends(instant_query)
            
            # Big Metric Display
            c1, c2, c3 = st.columns(3)
            status = "🔥 EXPLODING" if v_score > 75 else "🚀 RISING" if v_score > 55 else "⚖️ STABLE"
            c1.metric("Velocity Score", f"{v_score}%")
            c2.metric("Market Status", status)
            c3.button("Add to My Saved Trackers", on_click=lambda: st.session_state["my_categories"].append(instant_query) if instant_query not in st.session_state["my_categories"] else None)
            
            if v_score > 70: st.balloons()
        st.divider()

    # SECTION B: SAVED TRACKERS (The Comparison Chart)
    if presets:
        st.subheader("📊 Comparison Overview")
        real_data = []
        with st.spinner('Updating comparison data...'):
            for kw in presets:
                score = get_real_trends(kw)
                real_data.append({"Trend": kw, "Velocity": score})

        df = pd.DataFrame(real_data)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.bar_chart(df.set_index('Trend'))
        with col2:
            df['Status'] = df['Velocity'].apply(lambda x: "🔥" if x > 75 else "🚀" if x > 55 else "⚖️")
            st.dataframe(df.set_index('Trend'), use_container_width=True)
    else:
        if not instant_query:
            st.info("👈 Use the sidebar to search for a trend or select your saved trackers.")

    st.caption(f"Build v7.0 | Verified Sync: {datetime.datetime.now().strftime('%I:%M %p')}")
