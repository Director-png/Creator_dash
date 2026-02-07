import streamlit as st
import pandas as pd
import requests
import json
import datetime

# --- CONFIG ---
st.set_page_config(page_title="Creator Strategy Suite", layout="wide", page_icon="🔐")

# --- 1. MULTI-CLIENT DATABASE ---
# Format: "password": "Client Name"
USER_DATABASE = {
    "client_fashion_01": "Ananya Sharma",
    "client_tech_02": "Rahul Verma",
    "void_admin": "Deepak (Admin)"
}

# --- 2. AUTHENTICATION LOGIC ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["client_name"] = ""

    if not st.session_state["authenticated"]:
        st.title("🔒 Private Strategy Portal")
        st.write("Welcome. Please enter your unique access key to continue.")
        
        pwd_input = st.text_input("Access Key:", type="password")
        
        if st.button("Unlock Dashboard"):
            if pwd_input in USER_DATABASE:
                st.session_state["authenticated"] = True
                st.session_state["client_name"] = USER_DATABASE[pwd_input]
                st.rerun()
            else:
                st.error("❌ Invalid Key. Please contact your strategist for access.")
        return False
    return True

# --- 3. TREND ENGINE ---
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
        
        # Calculate density
        snippet_text = " ".join([obj.get('snippet', '').lower() for obj in organic])
        mention_count = snippet_text.count(keyword.lower())
        
        # Sensitivity Math
        score = 35 + (related * 6) + (questions * 4) + (mention_count * 1.5)
        return min(round(score), 100)
    except:
        return 50 

# --- MAIN APP EXECUTION ---
if check_password():
    # --- SIDEBAR ---
    st.sidebar.title("Navigation")
    st.sidebar.success(f"User: {st.session_state['client_name']}")
    
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

    st.sidebar.divider()
    st.sidebar.header("Trend Settings")
    keywords = st.sidebar.multiselect(
        "Focus Keywords", 
        ["Cotton Kurti", "Sunscreen", "Travel Vlogs", "Indo-Western", "Skincare Routine", "Home Decor"],
        default=["Cotton Kurti", "Sunscreen"]
    )

    # --- MAIN UI ---
    st.title("📈 Creator Intelligence Dashboard")
    st.write(f"Tailored market insights for **{st.session_state['client_name']}**")
    
    # --- 4. TREND PREDICTOR ---
    with st.expander("🔮 STRATEGIST'S WEEKLY FORECAST", expanded=True):
        st.subheader("Market Commentary")
        # Change this text weekly to give your clients fresh value
        st.info("""
        **Forecast:** Fashion search volume in India is shifting toward 'Indo-Western' fusion. 
        **Advice:** We recommend a 3-part Reel series focusing on 'Transition styling' to capitalize on this week's 15% spike.
        """)

    # --- 5. DATA VISUALIZATION ---
    if keywords:
        real_data = []
        with st.spinner('Syncing Live Google Trends...'):
            for kw in keywords:
                score = get_real_trends(kw)
                real_data.append({"Trend": kw, "Velocity": score})

        df = pd.DataFrame(real_data)
        
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Content Velocity Index")
            st.bar_chart(df.set_index('Trend'))

        with col2:
            st.subheader("Market Status")
            df['Status'] = df['Velocity'].apply(
                lambda x: "🔥 EXPLODING" if x > 75 else "🚀 RISING" if x > 55 else "STABLE"
            )
            st.dataframe(df.set_index('Trend'), use_container_width=True)

        st.divider()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        st.caption(f"Last Server Sync: {now} IST | Build v3.0 (Multi-User)")
    else:
        st.warning("Select keywords in the sidebar to populate the chart.")
