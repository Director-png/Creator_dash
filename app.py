import streamlit as st
import pandas as pd
import requests
import json

# --- CONFIG ---
st.set_page_config(page_title="Creator Strategy Suite", layout="wide")
# Tip: Move this to Streamlit Secrets later for safety!
API_KEY = "cfe3d0828971dc09543b2eaa2abc4b67d29d21a0" 

st.title("📈 Live Market Pulse (India)")

def get_real_trends(keyword):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": keyword, "gl": "in", "hl": "en"}) 
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status() # This will catch if the API key is bad
        data = response.json()
        
        related = len(data.get('relatedSearches', []))
        questions = len(data.get('peopleAlsoAsk', []))
        organic = len(data.get('organic', []))
        
        score = 40 + (related * 5) + (questions * 3) + (organic * 1)
        return min(score, 100)
    except Exception as e:
        # This will show the actual error on your website so we can fix it!
        st.error(f"Error fetching {keyword}: {e}")
        return 50
# --- DASHBOARD LOGIC ---
# These are the keywords your client cares about
keywords = ["Cotton Kurti", "Sunscreen", "Travel Vlogs"]
real_data = []

for kw in keywords:
    # We call the function and get the score directly
    velocity_score = get_real_trends(kw)
    real_data.append({"Trend Name": kw, "Velocity": velocity_score})

df = pd.DataFrame(real_data)

# --- UI ---
st.subheader("Real-Time Trends: India Market")
st.bar_chart(df.set_index('Trend Name'))

# Adding a nice status column for the table
df['Status'] = df['Velocity'].apply(lambda x: "🔥 Hot" if x > 70 else "🚀 Rising" if x > 50 else "Stable")
st.table(df)

st.info("💡 **Pro-Tip:** Keywords with a velocity over 70 are perfect for immediate Reel content.")

