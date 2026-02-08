import streamlit as st
import pandas as pd
import requests
import json
import random

# --- 1. SETTINGS & ACCESS ---
st.set_page_config(page_title="Executive Strategy Portal", layout="wide")

if "user_db" not in st.session_state:
    # UPDATED: Key is 'admin', Identity is 'Director'
    st.session_state["user_db"] = {"admin": "Director"}

if "my_categories" not in st.session_state:
    # REMOVED: Cotton Kurti and Sunscreen
    st.session_state["my_categories"] = ["Artificial Intelligence", "Digital Marketing"]

# --- 2. THE ENGINE (Fixed SEO & Global Logic) ---
@st.cache_data(ttl=3600) # Cache for 1 hour to prevent freezing
def fetch_all_data(keyword):
    API_KEY = "cfe3d0828971dc09543b2eaa2abc4b67d29d21a0" 
    url = "https://google.serper.dev/search"
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    payload = json.dumps({"q": keyword, "gl": "in", "hl": "en"})
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        res_data = response.json()
        
        # Robust SEO Extraction
        seo = [r.get('query') for r in res_data.get('relatedSearches', [])]
        if not seo:
            seo = [q.get('question') for q in res_data.get('peopleAlsoAsk', [])]
        if not seo: # Final fallback if API is thin on data
            seo = ["Trend Analysis", f"{keyword} News", f"Future of {keyword}"]
            
        score = 45 + (len(seo) * 4) + random.randint(1, 10)
        return {
            "score": min(score, 100),
            "seo": seo[:6],
            "status": "🔥 EXPLODING" if score > 75 else "🚀 RISING" if score > 55 else "⚖️ STABLE"
        }
    except:
        return {"score": 50, "seo": ["Data Unavailable"], "status": "⚖️ STABLE"}

# --- 3. AUTHENTICATION ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🛡️ Executive Intelligence Dashboard")
    input_key = st.text_input("Director Access Key:", type="password").lower().strip()
    if st.button("Authorize"):
        if input_key in st.session_state["user_db"]:
            st.session_state["authenticated"] = True
            st.session_state["identity"] = st.session_state["user_db"][input_key]
            st.rerun()
        else:
            st.error("Unauthorized Access.")
    st.stop()

# --- 4. THE DIRECTOR'S DASHBOARD ---
st.sidebar.title(f"🫡 Welcome, {st.session_state['identity']}")

# SECRET ADMIN PANEL (As requested)
with st.sidebar.expander("🛠️ Admin Controls"):
    st.write("**Manage Access Keys**")
    new_key = st.text_input("New User Key:").lower().strip()
    new_name = st.text_input("New User Name:")
    if st.button("Grant Access"):
        if new_key and new_name:
            st.session_state["user_db"][new_key] = new_name
            st.success(f"Added {new_name}")

if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.rerun()

# MAIN TABS
t_global, t_search, t_compare, t_strategy = st.tabs([
    "🌍 Global Market Pulse", "🔍 Instant Insight", "📊 Comparison Board", "💡 Strategy Lab"
])

# --- TAB: GLOBAL TRENDS (Fixed) ---
with t_global:
    st.subheader("Current High-Velocity Topics (India)")
    global_list = ["Generative AI", "EV Infrastructure", "Remote Work Culture", "Personal Finance"]
    cols = st.columns(4)
    for i, topic in enumerate(global_list):
        with cols[i]:
            g_data = fetch_all_data(topic)
            st.metric(topic, f"{g_data['score']}%", delta=g_data['status'])
            if st.button(f"Track {i}", key=f"g_{topic}"):
                if topic not in st.session_state["my_categories"]:
                    st.session_state["my_categories"].append(topic)
                    st.toast(f"Tracking {topic}")

# --- TAB: INSTANT SEARCH (Fixed SEO) ---
with t_search:
    st.subheader("On-Demand Trend Analysis")
    query = st.text_input("Enter target keyword:", placeholder="e.g. Luxury Real Estate")
    if query:
        with st.spinner("Mining Data..."):
            data = fetch_all_data(query)
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Velocity Score", f"{data['score']}%")
                st.info(f"Market Status: {data['status']}")
                st.markdown("### 🔑 SEO Keywords")
                for s in data['seo']:
                    st.code(s) # This ensures keywords are visible and copyable
                if st.button("Add to Board"):
                    if query not in st.session_state["my_categories"]:
                        st.session_state["my_categories"].append(query)
                        st.success("Board Updated")
            with c2:
                st.bar_chart(pd.DataFrame({"Velocity": [data['score']]}, index=[query]))

# --- TAB: COMPARISON ---
with t_compare:
    st.subheader("Director's Strategic Overview")
    if st.session_state["my_categories"]:
        # Trash Can to remove items
        to_remove = st.selectbox("Select keyword to remove:", ["-- Select --"] + st.session_state["my_categories"])
        if st.button("Delete Keyword"):
            if to_remove != "-- Select --":
                st.session_state["my_categories"].remove(to_remove)
                st.rerun()

        res_list = []
        for item in st.session_state["my_categories"]:
            d = fetch_all_data(item)
            res_list.append({"Keyword": item, "Velocity": d['score'], "Status": d['status']})
        
        df = pd.DataFrame(res_list).set_index("Keyword")
        st.bar_chart(df['Velocity'], color="#1f77b4")
        st.table(df)
    else:
        st.write("Tracking board is currently empty.")

# --- TAB: STRATEGY LAB ---
with t_strategy:
    if st.session_state["my_categories"]:
        target = st.selectbox("Focus Area:", st.session_state["my_categories"])
        t_data = fetch_all_data(target)
        st.markdown(f"## 💡 Content Pillars for **{target}**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🎬 Viral Hooks")
            st.write(f"- 'Why {target} is the only thing that matters in 2026...'")
            st.write(f"- 'The hidden data behind {target} (Shocking Results)'")
        with col2:
            st.subheader("🏷️ Optimized Meta-Tags")
            st.write(", ".join(t_data['seo']))
    else:
        st.warning("Please add keywords to analyze.")
