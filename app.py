import streamlit as st
import pandas as pd
import requests
import json
import random

# --- 1. THE PERMANENT GUEST LIST (Global Access) ---
# Add your users here. They can now log in from any device, anywhere.
MASTER_USER_DB = {
    "admin": "Director",
    "vip777": "Lead Strategist",
    "client01": "Executive Partner"
}

# --- 2. CONFIG & THEME ---
st.set_page_config(page_title="Executive Strategy Portal", layout="wide")

# --- 3. THE RELIABLE SEO ENGINE ---
@st.cache_data(ttl=3600)
def fetch_executive_data(keyword):
    API_KEY = "cfe3d0828971dc09543b2eaa2abc4b67d29d21a0" 
    url = "https://google.serper.dev/search"
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    payload = json.dumps({"q": keyword, "gl": "in", "hl": "en"})
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        res_data = response.json()
        
        # Priority 1: Related Searches
        seo = [r.get('query') for r in res_data.get('relatedSearches', [])]
        # Priority 2: Questions
        if not seo:
            seo = [q.get('question') for q in res_data.get('peopleAlsoAsk', [])]
        # Priority 3: Organic Context
        if not seo:
            seo = [o.get('title')[:40] for o in res_data.get('organic', [])[:4]]
            
        score = 50 + (len(seo) * 3) + random.randint(1, 10)
        return {
            "score": min(score, 100),
            "seo": seo if seo else ["Market Analysis", "Growth Trends", "Strategic Planning"],
            "status": "🔥 EXPLODING" if score > 78 else "🚀 RISING" if score > 58 else "⚖️ STABLE"
        }
    except:
        return {"score": 50, "seo": ["Data Syncing..."], "status": "⚖️ STABLE"}

# --- 4. PERSISTENT LOGIN SYSTEM ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🛡️ Executive Intelligence Dashboard")
    st.subheader("Multi-Device Access Enabled")
    
    # Using a form helps with "Enter" key submission on mobile/tablets
    with st.form("login_form"):
        input_key = st.text_input("Enter Director Access Key:", type="password").lower().strip()
        submit = st.form_submit_button("Authorize Access")
        
        if submit:
            if input_key in MASTER_USER_DB:
                st.session_state["authenticated"] = True
                st.session_state["identity"] = MASTER_USER_DB[input_key]
                st.rerun()
            else:
                st.error("Access Key Not Recognized. Contact Director for authorization.")
    st.stop()

# --- 5. THE DIRECTOR'S INTERFACE ---
st.sidebar.title(f"🫡 {st.session_state['identity']}")
st.sidebar.write("System Status: **Active**")

if st.sidebar.button("Logout & Clear Session"):
    st.session_state["authenticated"] = False
    st.rerun()

# Default tracking list (Professional & Clean)
if "my_categories" not in st.session_state:
    st.session_state["my_categories"] = ["Artificial Intelligence", "Digital Marketing"]

# TABS
t_global, t_search, t_compare, t_strategy = st.tabs([
    "🌍 Global Market Pulse", "🔍 Instant Insight", "📊 Comparison Board", "💡 Strategy Lab"
])

# --- TAB 1: GLOBAL PULSE ---
with t_global:
    st.subheader("🔥 High-Velocity Market Trends (India)")
    global_list = ["Generative AI", "EV Infrastructure", "Remote Work Culture", "Personal Finance"]
    cols = st.columns(4)
    for i, topic in enumerate(global_list):
        with cols[i]:
            g_data = fetch_executive_data(topic)
            st.metric(topic, f"{g_data['score']}%", delta=g_data['status'])
            if st.button("Track", key=f"track_{topic}"):
                if topic not in st.session_state["my_categories"]:
                    st.session_state["my_categories"].append(topic)
                    st.toast(f"Tracking {topic}")

# --- TAB 2: INSTANT SEARCH (SEO Fixed) ---
with t_search:
    st.subheader("On-Demand Strategic Analysis")
    query = st.text_input("Search Niche:", placeholder="e.g. Fintech Innovation")
    if query:
        data = fetch_executive_data(query)
        col_left, col_right = st.columns([1, 2])
        with col_left:
            st.metric("Market Velocity", f"{data['score']}%")
            st.write(f"**Verdict:** {data['status']}")
            st.markdown("### 🔑 SEO & Tags")
            # Using Code blocks ensures they always render properly
            for item in data['seo']:
                st.code(item)
            if st.button("Add to Executive Board"):
                if query not in st.session_state["my_categories"]:
                    st.session_state["my_categories"].append(query)
                    st.success("Board Updated")
        with col_right:
            st.bar_chart(pd.DataFrame({"Velocity": [data['score']]}, index=[query]))

# --- TAB 3: COMPARISON ---
with t_compare:
    st.subheader("Multi-Trend Comparison")
    if st.session_state["my_categories"]:
        # Deletion logic moved to a clean dropdown
        with st.expander("🗑️ Manage Tracked Keywords"):
            to_del = st.selectbox("Select to remove:", ["-- Select --"] + st.session_state["my_categories"])
            if st.button("Confirm Removal"):
                if to_del != "-- Select --":
                    st.session_state["my_categories"].remove(to_del)
                    st.rerun()

        comp_list = []
        for item in st.session_state["my_categories"]:
            d = fetch_executive_data(item)
            comp_list.append({"Trend": item, "Velocity": d['score'], "Status": d['status']})
        
        df = pd.DataFrame(comp_list).set_index("Trend")
        st.bar_chart(df['Velocity'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No trends currently tracked.")

# --- TAB 4: STRATEGY LAB ---
with t_strategy:
    if st.session_state["my_categories"]:
        target = st.selectbox("Select Focus Area:", st.session_state["my_categories"])
        t_data = fetch_executive_data(target)
        st.markdown(f"## 💡 Content Framework: {target}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🎥 Engagement Hooks")
            st.write(f"1. 'Why the data says {target} is the future...'")
            st.write(f"2. 'The one thing leaders get wrong about {target}.'")
        with c2:
            st.subheader("📈 SEO Deployment")
            st.write("Copy-paste these into meta-tags:")
            st.info(", ".join(t_data['seo']))
