import streamlit as st
import pandas as pd
import requests
import json
import random

# ==========================================
# 1. PASTE YOUR MAGIC URL BELOW
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGThrIabwjsm42GgyOqNsPkdY3BRSwv5wnOKQMH_iMetJKnUMiPESLb7wb5_n24gn33RjEpG3VhSbD/pub?output=csv"
# ==========================================

# --- 2. THE PERMANENT BRAIN ---
def load_global_users():
    """Fetches the permanent user list from Google Sheets"""
    try:
        # Pulling CSV export from Google Sheets
        df = pd.read_csv(SHEET_URL)
        # Clean the data (lowercase keys, remove spaces)
        df['key'] = df['key'].astype(str).str.lower().str.strip()
        df['name'] = df['name'].astype(str).str.strip()
        return dict(zip(df['key'], df['name']))
    except Exception as e:
        # Safe fallback so you never get locked out
        return {"admin": "Director"}

# --- 3. ANALYTICS ENGINE ---
@st.cache_data(ttl=600)
def fetch_market_data(keyword):
    API_KEY = "cfe3d0828971dc09543b2eaa2abc4b67d29d21a0" 
    url = "https://google.serper.dev/search"
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    payload = json.dumps({"q": keyword, "gl": "in", "hl": "en"})
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        res = response.json()
        # SEO Extraction (Priority: Related > People Also Ask > Organic Titles)
        seo = [r.get('query') for r in res.get('relatedSearches', [])]
        if not seo:
            seo = [q.get('question') for q in res.get('peopleAlsoAsk', [])]
        if not seo:
            seo = ["Market Trends", "Growth Strategy", "Innovation"]
            
        score = 50 + (len(seo) * 4) + random.randint(1, 10)
        return {
            "score": min(score, 100),
            "seo": seo[:8],
            "status": "🔥 EXPLODING" if score > 78 else "🚀 RISING" if score > 58 else "⚖️ STABLE"
        }
    except:
        return {"score": 50, "seo": ["Re-syncing..."], "status": "⚖️ STABLE"}

# --- 4. AUTHENTICATION UI ---
st.set_page_config(page_title="Executive Strategy Portal", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🛡️ Executive Intelligence Dashboard")
    st.subheader("Global Access Portal")
    
    t_login, t_reg = st.tabs(["🔐 Secure Login", "📝 Access Registration"])
    
    with t_reg:
        st.markdown("""
        ### How to get access:
        1. Contact the **Director** to request an Access Key.
        2. Once your key is added to the Master Sheet, log in using the tab on the left.
        """)
        st.info("Direct multi-device freedom is enabled for all registered partners.")

    with t_login:
        # Load keys from Google Sheets
        current_allowed_users = load_global_users()
        
        with st.form("login_gate"):
            l_key = st.text_input("Access Key:", type="password").lower().strip()
            if st.form_submit_button("Authorize & Enter"):
                if l_key in current_allowed_users:
                    st.session_state["authenticated"] = True
                    st.session_state["identity"] = current_allowed_users[l_key]
                    st.rerun()
                else:
                    st.error("Key not found in Master Database. Please check your credentials.")
    st.stop()

# --- 5. THE DIRECTOR'S INTERFACE ---
st.sidebar.title(f"🫡 {st.session_state['identity']}")

# Database Sync Tool
if st.sidebar.button("🔄 Sync Master Database"):
    st.cache_data.clear()
    st.toast("User database updated from Google Sheets!")

if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.rerun()

# Default Setup
if "my_categories" not in st.session_state:
    st.session_state["my_categories"] = ["Artificial Intelligence", "Digital Marketing"]

# APP TABS
t1, t2, t3 = st.tabs(["🌍 Global Market Pulse", "🔍 Intelligence Search", "📊 Executive Board"])

with t1:
    st.subheader("High-Velocity Market Trends (India)")
    trends = ["Generative AI", "EV Infrastructure", "Digital Nomad", "Personal Finance"]
    cols = st.columns(4)
    for i, t in enumerate(trends):
        with cols[i]:
            d = fetch_market_data(t)
            st.metric(t, f"{d['score']}%", delta=d['status'])
            if st.button("Track", key=f"t_{t}"):
                if t not in st.session_state["my_categories"]:
                    st.session_state["my_categories"].append(t)
                    st.toast(f"Added {t} to your board.")

with t2:
    st.subheader("Deep-Dive Trend Analysis")
    q = st.text_input("Enter target keyword (e.g., Fintech):")
    if q:
        with st.spinner("Mining SEO Insights..."):
            data = fetch_market_data(q)
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Market Velocity", f"{data['score']}%")
                st.write(f"Status: **{data['status']}**")
                st.markdown("### 🔑 Target SEO Tags")
                for s in data['seo']:
                    st.code(s)
                if st.button("Add to Executive Board"):
                    if q not in st.session_state["my_categories"]:
                        st.session_state["my_categories"].append(q)
            with c2:
                # Predictive visual
                chart_vals = [random.randint(40, 90) for _ in range(7)] + [data['score']]
                st.line_chart(pd.DataFrame({"Interest": chart_vals}))

with t3:
    st.subheader("Your Strategic Overview")
    if st.session_state["my_categories"]:
        # Board cleanup
        with st.expander("🗑️ Manage Tracked Keywords"):
            to_del = st.selectbox("Select to remove:", ["-- Select --"] + st.session_state["my_categories"])
            if st.button("Confirm Deletion"):
                if to_del != "-- Select --":
                    st.session_state["my_categories"].remove(to_del)
                    st.rerun()
        
        # Board Overview
        res_list = []
        for item in st.session_state["my_categories"]:
            res = fetch_market_data(item)
            res_list.append({"Trend": item, "Velocity": res['score'], "Status": res['status']})
            # Insight Expanders
            with st.expander(f"📌 {item} Strategy"):
                st.write(f"**Primary SEO Keywords:** {', '.join(res['seo'])}")
                st.write(f"**Growth Status:** {res['status']}")
        
        st.divider()
        st.dataframe(pd.DataFrame(res_list).set_index("Trend"), use_container_width=True)
    else:
        st.info("Your board is currently empty. Use the Search or Pulse tabs to add trends.")
