import streamlit as st
import pandas as pd
import requests
import json
import datetime

# --- CONFIG ---
st.set_page_config(page_title="Creator Strategy Suite", layout="wide", page_icon="🎯")

# --- 1. USER & CATEGORY DATABASE ---
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {"void_admin": "Deepak (Admin)"}

# Initialize personal categories if not exists
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
    # --- SIDEBAR: PERSONALIZATION ---
    st.sidebar.title(f"👋 {st.session_state['client_name']}")
    
    # Feature: Manage Quick Searches
    st.sidebar.subheader("🛠 My Categories")
    new_cat = st.sidebar.text_input("Add new quick category:", placeholder="e.g. AI Tools")
    if st.sidebar.button("Add to Quick Select"):
        if new_cat and new_cat not in st.session_state["my_categories"]:
            st.session_state["my_categories"].append(new_cat)
            st.sidebar.success(f"Added {new_cat}!")
            st.rerun()

    if st.sidebar.button("Clear My Categories"):
        st.session_state["my_categories"] = []
        st.rerun()

    st.sidebar.divider()
    
    # Feature: Select from the custom list
    st.sidebar.subheader("🚀 Active Trackers")
    presets = st.sidebar.multiselect(
        "Enable for Dashboard:", 
        options=st.session_state["my_categories"],
        default=st.session_state["my_categories"][:2] if st.session_state["my_categories"] else []
    )

    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

    # --- MAIN UI ---
    st.title("📈 Creator Intelligence Dashboard")
    
    with st.expander("🔮 STRATEGIST'S WEEKLY FORECAST", expanded=True):
        st.info(f"Welcome back {st.session_state['client_name']}! Your personalized trackers are ready.")

    if presets:
        real_data = []
        with st.spinner('Updating your personalized data...'):
            for kw in presets:
                score = get_real_trends(kw)
                real_data.append({"Trend": kw, "Velocity": score})

        df = pd.DataFrame(real_data)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Personalized Velocity Index")
            st.bar_chart(df.set_index('Trend'))
        with col2:
            st.subheader("Live Status")
            df['Status'] = df['Velocity'].apply(
                lambda x: "🔥 EXPLODING" if x > 75 else "🚀 RISING" if x > 55 else "STABLE"
            )
            st.dataframe(df.set_index('Trend'), use_container_width=True)

        st.divider()
        st.caption(f"Last Sync: {datetime.datetime.now().strftime('%I:%M %p')} | Build v6.0 (Custom Presets)")
    else:
        st.warning("Your Quick Select list is empty. Add some categories in the sidebar!")
