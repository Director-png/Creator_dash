import streamlit as st
import pandas as pd
import requests
import json
import datetime

# --- CONFIG ---
st.set_page_config(page_title="Creator Strategy Suite", layout="wide", page_icon="🚀")

# --- 1. MULTI-CLIENT DATABASE ---
USER_DATABASE = {
    "client_fashion_01": "Ananya Sharma",
    "client_tech_02": "Rahul Verma",
    "void_admin": "Director (Admin)"
}

# --- 2. AUTHENTICATION LOGIC ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["client_name"] = ""

    if not st.session_state["authenticated"]:
        st.title("🔒 Private Strategy Portal")
        st.write("Welcome. Please enter your unique access key.")
        
        pwd_input = st.text_input("Access Key:", type="password")
        
        if st.button("Unlock Dashboard"):
            if pwd_input in USER_DATABASE:
                st.session_state["authenticated"] = True
                st.session_state["client_name"] = USER_DATABASE[pwd_input]
                st.rerun()
            else:
                st.error("❌ Invalid Key. Access Denied.")
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
        
        # Calculate snippet density for movement
        snippet_text = " ".join([obj.get('snippet', '').lower() for obj in organic])
        mention_count = snippet_text.count(keyword.lower())
        
        # Sensitivity Math: Base 35 + weighted points
        score = 35 + (related * 6) + (questions * 4) + (mention_count * 1.5)
        return min(round(score), 100)
    except:
        return 50 

# --- MAIN APP EXECUTION ---
if check_password():
    # --- SIDEBAR & SEARCH ---
    st.sidebar.title("Navigation")
    st.sidebar.success(f"User: {st.session_state['client_name']}")
    
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

    st.sidebar.divider()
    
    st.sidebar.header("🔍 Custom Research")
    user_search = st.sidebar.text_input("Analyze new trend:", placeholder="e.g. Linen Pants")
    
    st.sidebar.header("Preset Trackers")
    presets = st.sidebar.multiselect(
        "Quick Select", 
        ["Cotton Kurti", "Sunscreen", "Travel Vlogs", "Indo-Western", "Skincare", "Home Decor"],
        default=["Cotton Kurti", "Sunscreen"]
    )

    # Merge presets with manual search
    active_keywords = presets.copy()
    if user_search:
        active_keywords.append(user_search)

    # --- MAIN UI ---
    st.title("📈 Creator Intelligence Dashboard")
    st.write(f"Tailored insights for **{st.session_state['client_name']}**")
    
    # Strategy Section
    with st.expander("🔮 STRATEGIST'S WEEKLY FORECAST", expanded=True):
        st.info("**Advice:** High interaction on 'Indo-Western' fusion. Use trending Bollywood audio for 20% better reach.")

    # Data Processing
    if active_keywords:
        real_data = []
        with st.spinner('Analyzing market velocity...'):
            for kw in active_keywords:
                score = get_real_trends(kw)
                real_data.append({"Trend": kw, "Velocity": score})

        df = pd.DataFrame(real_data)
        
        # Feedback for custom search
        if user_search:
            search_score = df[df['Trend'] == user_search]['Velocity'].values[0]
            if search_score > 70:
                st.balloons()
                st.success(f"🔥 **Hot Opportunity!** '{user_search}' has massive search density right now.")
            else:
                st.warning(f"⚖️ **Steady.** '{user_search}' is consistent, but not viral yet.")

        # Visuals
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
        now = datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p')
        st.caption(f"Live Server Sync: {now} IST | Build v4.5 (Research Mode)")
    else:
        st.warning("Please select or search a keyword to begin.")

