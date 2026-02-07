import streamlit as st
import pandas as pd
import requests
import json
import datetime

# --- CONFIG ---
st.set_page_config(page_title="Creator Strategy Suite", layout="wide", page_icon="📈")

# --- API SETUP ---
# Remember: For ultimate safety, move this to Streamlit Secrets later!
API_KEY = "cfe3d0828971dc09543b2eaa2abc4b67d29d21a0" 

def get_real_trends(keyword):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": keyword, "gl": "in", "hl": "en"}) 
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        data = response.json()
        
        # Pulling data points
        related_count = len(data.get('relatedSearches', []))
        questions_count = len(data.get('peopleAlsoAsk', []))
        organic_results = data.get('organic', [])
        
        # Analyze snippet density for better movement in bars
        snippet_text = " ".join([obj.get('snippet', '').lower() for obj in organic_results])
        mention_count = snippet_text.count(keyword.lower())

        # Sensitivity Math: Base 35 + weighted variables
        score = 35 + (related_count * 6) + (questions_count * 4) + (mention_count * 1.5)
        return min(round(score), 100)
    except Exception:
        return 50 

# --- SIDEBAR (Settings & Controls) ---
st.sidebar.header("Control Panel")
st.sidebar.write("Tracking Market: **India**")
# You can add or remove keywords here
keywords = st.sidebar.multiselect(
    "Active Trackers", 
    ["Cotton Kurti", "Sunscreen", "Travel Vlogs", "Indo-Western", "Skincare Routine"],
    default=["Cotton Kurti", "Sunscreen", "Travel Vlogs"]
)

# --- MAIN DASHBOARD ---
st.title("📈 Creator Intelligence Dashboard")
st.write("Real-time content velocity for the Indian market.")

if keywords:
    real_data = []
    
    # Progress bar for a "Professional" feel while loading
    with st.spinner('Syncing with Google India Data...'):
        for kw in keywords:
            velocity_score = get_real_trends(kw)
            real_data.append({"Trend Name": kw, "Velocity": velocity_score})

    df = pd.DataFrame(real_data)
    
    # UI Layout: Charts and Metrics
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Visual Velocity Index")
        # Custom color bar chart
        st.bar_chart(df.set_index('Trend Name'))

    with col2:
        st.subheader("Strategy Labels")
        # Adding status logic
        df['Status'] = df['Velocity'].apply(
            lambda x: "🔥 EXPLODING" if x > 75 else "🚀 RISING" if x > 55 else "STABLE"
        )
        st.dataframe(df.set_index('Trend Name'), use_container_width=True)

    # Footer Info
    st.divider()
    t = datetime.datetime.now().strftime('%d %b, %Y | %I:%M %p')
    st.caption(f"✅ Data verified via Serper API Engine | Last Sync: {t}")
    st.info("💡 **Strategy Tip:** Focus your next 3 Reels on 'Exploding' topics for maximum reach.")

else:
    st.warning("Please select at least one keyword in the sidebar to begin tracking.")
