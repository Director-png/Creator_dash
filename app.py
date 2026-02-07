import streamlit as st
import pandas as pd
import requests
import json

# --- CONFIG ---
st.set_page_config(page_title="Creator Strategy Suite", layout="wide")
API_KEY = "cfe3d0828971dc09543b2eaa2abc4b67d29d21a0" # <--- PASTE YOUR KEY HERE

st.title("📈 Live Market Pulse (India)")

def get_real_trends(keyword):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": keyword, "gl": "in", "hl": "en"}) 
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        data = response.json()
        
        # Calculate score based on total data points found
        related = len(data.get('relatedSearches', []))
        questions = len(data.get('peopleAlsoAsk', []))
        organic = len(data.get('organic', []))
        
        # New Formula: Base 40 + (Weights for different data points)
        # This ensures the bars aren't all the same height.
        score = 40 + (related * 5) + (questions * 3) + (organic * 1)
       # --- DASHBOARD LOGIC ---
keywords = ["Cotton Kurti", "Sunscreen", "Travel Vlogs"]
real_data = []

for kw in keywords:
    # Now get_real_trends(kw) returns the final score (e.g., 75)
    score = get_real_trends(kw) 
    real_data.append({"Trend Name": kw, "Velocity": score})

df = pd.DataFrame(real_data) 
        # Cap it at 100
        return min(score, 100)
    except:
        return 50 # Fallback if API fails
    
    response = requests.post(url, headers=headers, data=payload)
    # This pulls 'related searches' which is a great proxy for trending velocity
    data = response.json()
    return data.get('relatedSearches', [])



# --- UI ---
st.subheader("Real-Time Trends: India Market")
st.bar_chart(df.set_index('Trend Name'))
st.table(df)


