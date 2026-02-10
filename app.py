import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
import feedparser

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="VOID OS", page_icon="🌑", layout="wide")

# Database Links
MARKET_URL = "https://docs.google.com/spreadsheets/d/163haIuPIna3pEY9IDxncPM2kFFsuZ76HfKsULcMu1y4/export?format=csv"
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"

# --- 2. DATA ENGINES ---
@st.cache_data(ttl=600)
def load_data(url, clean=False):
    try:
        df = pd.read_csv(url)
        if clean:
            df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except: return pd.DataFrame()

# --- 3. SESSION AUTH ---
for key, val in {"logged_in": False, "user_role": "user", "user_name": "Operator"}.items():
    if key not in st.session_state: st.session_state[key] = val

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🛡️ DIRECTOR'S PORTAL</h1>", unsafe_allow_html=True)
    email_in = st.text_input("Email").lower().strip()
    pw_in = st.text_input("Password", type="password")
    
    if st.button("ACCESS SYSTEM", use_container_width=True):
        if email_in in ["admin", "director@void.com"] and pw_in in ["1234", "VOID_2026"]:
            st.session_state.update({"logged_in": True, "user_role": "admin", "user_name": "The Director"})
            st.rerun()
        else:
            users = load_data(USER_DB_URL, clean=True)
            if not users.empty:
                # Auth Logic: Col 2=Email, Col 4=Password
                match = users[(users.iloc[:, 2].astype(str).str.lower() == email_in) & (users.iloc[:, 4].astype(str) == pw_in)]
                if not match.empty:
                    st.session_state.update({"logged_in": True, "user_name": match.iloc[0, 1], "user_role": "user"})
                    st.rerun()
            else: st.error("System Offline.")
    st.stop()

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🌑 VOID OS")
    st.caption(f"CONNECTED: {st.session_state.user_name.upper()}")
    nav = st.radio("MODULES", ["Dashboard", "Global Pulse", "Script Architect"] + (["Pitch Vault"] if st.session_state.user_role == "admin" else []))
    if st.button("TERMINATE"):
        st.session_state.logged_in = False
        st.rerun()

# --- 5. INTERFACE MODULES ---
if nav == "Dashboard":
    st.header("🌑 SYSTEM OVERVIEW")
    data = load_data(MARKET_URL)
    if not data.empty:
        # FIXED: Line-break protection applied
        fig = px.bar(data.head(8), x=data.columns[1], y=data.columns[0], orientation='h', template="plotly_dark")
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

elif nav == "Global Pulse":
    st.header("🌐 GLOBAL INTELLIGENCE")
    feed = feedparser.parse("https://techcrunch.com/category/artificial-intelligence/feed/")
    for entry in feed.entries[:3]:
        st.subheader(entry.title)
        st.write(entry.summary[:150] + "...")
        st.markdown(f"[Intel Link]({entry.link})")
        st.divider()

elif nav == "Script Architect":
    st.header("💎 SCRIPT ARCHITECT")
    topic = st.text_input("Core Topic")
    if st.button("Generate") and topic:
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            chat = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":f"Short script: {topic}"}])
            st.write(chat.choices[0].message.content)
        except Exception as e: st.error(f"Error: {e}")
