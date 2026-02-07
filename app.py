import streamlit as st
import pandas as pd
import requests
import json
import datetime

# --- CONFIG ---
st.set_page_config(page_title="Creator Strategy Suite", layout="wide", page_icon="🚀")

# --- 1. USER DATABASE ---
# We start with your Master Admin key.
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {
        "void_admin": "Deepak (Admin)",
        "creator_test": "Beta Tester"
    }

# --- 2. AUTHENTICATION & REGISTRATION ---
def login_system():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["client_name"] = ""

    if not st.session_state["authenticated"]:
        st.title("🔐 Creator Intelligence Portal")
        
        tab1, tab2 = st.tabs(["Login", "Create Account"])
        
        with tab1:
            st.subheader("Existing User")
            pwd_input = st.text_input("Enter your Access Key:", type="password", key="login_pwd")
            if st.button("Unlock Dashboard"):
                if pwd_input in st.session_state["user_db"]:
                    st.session_state["authenticated"] = True
                    st.session_state["client_name"] = st.session_state["user_db"][pwd_input]
                    st.rerun()
                else:
                    st.error("Key not found. Please register first.")
        
        with tab2:
            st.subheader("New Joiner")
            new_name = st.text_input("Your Name/Brand Name:")
            new_key = st.text_input("Choose your unique Access Key:", type="password", help="This is what you will use to log in.")
            
            if st.button("Register & Login"):
                if new_key and new_name:
                    if new_key in st.session_state["user_db"]:
                        st.error("This key is already taken! Try another one.")
                    else:
                        st.session_state["user_db"][new_key] = new_name
                        st.session_state["authenticated"] = True
                        st.session_state["client_name"] = new_name
                        st.success("Account Created!")
                        st.rerun()
                else:
                    st.warning("Please fill in both fields.")
        return False
    return True

# --- 3. THE ANALYTICS ENGINE ---
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

# --- MAIN APP EXECUTION ---
if login_system():
    # --- SIDEBAR ---
    st.sidebar.title("Navigation")
    st.sidebar.success(f"Welcome, {st.session_state['client_name']}!")
    
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

    st.sidebar.divider()
    st.sidebar.header("🔍 Custom Research")
    user_search = st.sidebar.text_input("Analyze new trend:", placeholder="e.g. Linen Pants")
    
    presets = st.sidebar.multiselect(
        "Quick Select", 
        ["Cotton Kurti", "Sunscreen", "Travel Vlogs", "Indo-Western", "Skincare", "Home Decor"],
        default=["Cotton Kurti", "Sunscreen"]
    )

    active_keywords = presets.copy()
    if user_search:
        active_keywords.append(user_search)

    # --- MAIN UI ---
    st.title("📈 Creator Intelligence Dashboard")
    
    with st.expander("🔮 STRATEGIST'S WEEKLY FORECAST", expanded=True):
        st.info(f"Hey {st.session_state['client_name']}, based on current data, we recommend focusing on 'Transition Reels' this week.")

    if active_keywords:
        real_data = []
        with st.spinner('Calculating market velocity...'):
            for kw in active_keywords:
                score = get_real_trends(kw)
                real_data.append({"Trend": kw, "Velocity": score})

        df = pd.DataFrame(real_data)
        
        if user_search:
            search_score = df[df['Trend'] == user_search]['Velocity'].values[0]
            if search_score > 70:
                st.balloons()
                st.success(f"🔥 **Hot Opportunity!** '{user_search}' is peaking.")
            else:
                st.warning(f"⚖️ **Steady.** '{user_search}' has consistent volume.")

        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Velocity Index")
            st.bar_chart(df.set_index('Trend'))
        with col2:
            st.subheader("Status Labels")
            df['Status'] = df['Velocity'].apply(
                lambda x: "🔥 EXPLODING" if x > 75 else "🚀 RISING" if x > 55 else "STABLE"
            )
            st.dataframe(df.set_index('Trend'), use_container_width=True)

        st.divider()
        now = datetime.datetime.now().strftime('%d %b, %Y | %I:%M %p')
        st.caption(f"Sync: {now} IST | Build v5.0 (User Self-Service)")
