import streamlit as st
import pandas as pd
import requests
import json
import datetime

# --- CONFIG ---
st.set_page_config(page_title="Creator Strategy Pro", layout="wide", page_icon="💎")

# --- 1. THE DATABASE (Simulated Permanent Memory) ---
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {"void_admin": "Deepak (Admin)"}

if "my_categories" not in st.session_state:
    st.session_state["my_categories"] = ["Cotton Kurti", "Sunscreen"]

# --- 2. AUTH SYSTEM ---
def login_system():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    
    if not st.session_state["authenticated"]:
        st.title("🔐 Creator Strategy Portal")
        t1, t2 = st.tabs(["Login", "Register"])
        with t1:
            pwd = st.text_input("Access Key:", type="password")
            if st.button("Enter Dashboard"):
                if pwd in st.session_state["user_db"]:
                    st.session_state["authenticated"] = True
                    st.session_state["client_name"] = st.session_state["user_db"][pwd]
                    st.rerun()
        with t2:
            n = st.text_input("Full Name:")
            k = st.text_input("Create Key:", type="password")
            if st.button("Sign Up"):
                st.session_state["user_db"][k] = n
                st.success("Account Created! Now go to Login.")
        return False
    return True

# --- 3. THE SMART ENGINE ---
API_KEY = "cfe3d0828971dc09543b2eaa2abc4b67d29d21a0" 

def get_deep_insights(keyword):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": keyword, "gl": "in", "hl": "en"}) 
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=payload)
        data = response.json()
        
        # Calculate Velocity
        related = data.get('relatedSearches', [])
        questions = data.get('peopleAlsoAsk', [])
        score = 35 + (len(related) * 6) + (len(questions) * 4)
        
        return {
            "score": min(score, 100),
            "related": [r.get('query') for r in related[:5]],
            "questions": [q.get('question') for q in questions[:3]]
        }
    except:
        return {"score": 50, "related": [], "questions": []}

# --- MAIN APP ---
if login_system():
    st.sidebar.title(f"💎 {st.session_state['client_name']}")
    
    # SEARCH BAR
    st.sidebar.header("🔍 Trend Research")
    query = st.sidebar.text_input("Enter Keyword:", placeholder="e.g. Vegan Leather")
    
    st.sidebar.divider()
    
    # TRACKER MANAGEMENT
    st.sidebar.header("📌 My Trackers")
    presets = st.sidebar.multiselect("Active Views:", st.session_state["my_categories"], default=st.session_state["my_categories"])
    
    new_tag = st.sidebar.text_input("Add New Tracker:")
    if st.sidebar.button("Save Tracker"):
        if new_tag: st.session_state["my_categories"].append(new_tag); st.rerun()

    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False; st.rerun()

    # --- UI LAYOUT ---
    st.title("🚀 Market Intelligence Dashboard")
    
    if query:
        data = get_deep_insights(query)
        st.subheader(f"Analysis: {query.upper()}")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Trend Velocity", f"{data['score']}%")
        m2.metric("Market Competition", "Medium" if data['score'] < 80 else "High")
        m3.metric("Demand Status", "🔥 EXPLODING" if data['score'] > 75 else "⚖️ STEADY")
        
        # RELATED TRENDS (Option 1)
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("**Related Keywords to target:**")
            for item in data['related']:
                st.write(f"- {item}")
        
        # CONTENT PILLARS (Option 3)
        with col_b:
            st.success("**🎯 Suggested Content Pillars:**")
            if data['score'] > 70:
                st.write("1. **The 'Why Now' Reel:** Explain the sudden spike in this trend.")
                st.write("2. **Comparison Video:** This vs. the old alternative.")
                st.write("3. **Beginner's Guide:** How to start with this in 2026.")
            else:
                st.write("1. **Educational Carousel:** Why this is a timeless staple.")
                st.write("2. **Mistakes to Avoid:** Common errors people make here.")

        # VISUAL CHART
        st.bar_chart(pd.DataFrame({"Score": [data['score']]}, index=[query]))
        st.divider()

    # COMPARISON SECTION
    if presets:
        st.subheader("📊 Comparison Tracking")
        comp_list = []
        for p in presets:
            d = get_deep_insights(p)
            comp_list.append({"Trend": p, "Velocity": d['score']})
        
        df = pd.DataFrame(comp_list)
        st.line_chart(df.set_index('Trend'))
        st.table(df)

    st.caption(f"Build v8.0 | Strategist: {st.session_state['client_name']}")
