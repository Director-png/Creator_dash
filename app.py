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
        data = response.json()
        
        # --- NEW SENSITIVITY LOGIC ---
        related_count = len(data.get('relatedSearches', []))
        questions_count = len(data.get('peopleAlsoAsk', []))
        organic_results = data.get('organic', [])
        
        # Let's count how many times the keyword appears in the top snippets
        # This shows how "dense" the topic is right now
        snippet_text = " ".join([obj.get('snippet', '').lower() for obj in organic_results])
        mention_count = snippet_text.count(keyword.lower())

        # New Score Formula
        # Base 30 + Related(x5) + Questions(x5) + Mentions(x2)
        score = 30 + (related_count * 5) + (questions_count * 5) + (mention_count * 2)
        
        return min(score, 100)
    except Exception as e:
        return 50 

# --- DASHBOARD LOGIC ---
keywords = ["Cotton Kurti", "Sunscreen", "Travel Vlogs"]
real_data = []

# Optional: Add a checkbox to see the raw data (Great for debugging!)
show_debug = st.checkbox("Show Debug Info")

for kw in keywords:
    score = get_real_trends(kw)
    real_data.append({"Trend Name": kw, "Velocity": score})
    if show_debug:
        st.write(f"Debug: {kw} calculated score is {score}")

df = pd.DataFrame(real_data)

# --- UI ---
st.subheader("Real-Time Trends: India Market")
st.bar_chart(df.set_index('Trend Name'))

# Adding a nice status column for the table
df['Status'] = df['Velocity'].apply(lambda x: "🔥 Hot" if x > 70 else "🚀 Rising" if x > 50 else "Stable")
st.table(df)
import datetime
st.caption(f"Last sync with Google India: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.info("💡 **Pro-Tip:** Keywords with a velocity over 70 are perfect for immediate Reel content.")

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



