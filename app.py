import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
import requests
import feedparser

# --- 1. CONFIG & CONNECTIONS ---
st.set_page_config(page_title="Director Portal", layout="wide")

# Market Data
MARKET_URL = "https://docs.google.com/spreadsheets/d/163haIuPIna3pEY9IDxncPM2kFFsuZ76HfKsULcMu1y4/export?format=csv"

# User Database (Form Responses)
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"

# Google Form Submission Link
FORM_POST_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfnNLb9O-szEzYfYEL85aENIimZFtMd5H3a7o6fX-_6ftU_HA/formResponse"

# --- 2. DATA LOADING FUNCTIONS ---
def load_market_data():
    try:
        df = pd.read_csv(MARKET_URL)
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

def load_user_db():
    try:
        df = pd.read_csv(USER_DB_URL)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# --- 3. SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

# --- 4. THE GATEKEEPER ---
if not st.session_state.logged_in:
    st.title("🛡️ Director's Intelligence Portal")
    t1, t2 = st.tabs(["🔑 Login", "📝 Register"])

    with t1:
        email_in = st.text_input("Email", key="login_email").lower().strip()
        pw_in = st.text_input("Password", type="password", key="login_pw").strip()
        
        if st.button("Access System", use_container_width=True):
            users = load_user_db()
            
            if email_in == "admin" and pw_in == "1234":
                st.session_state.logged_in = True
                st.session_state.user_name = "Master Director"
                st.session_state.user_email = "admin"
                st.rerun()
            
            elif not users.empty:
                email_col = [c for c in users.columns if 'email' in c][0]
                pw_col = [c for c in users.columns if 'password' in c][0]
                name_col = [c for c in users.columns if 'name' in c][0]
                
                match = users[(users[email_col] == email_in) & (users[pw_col].astype(str) == pw_in)]
                
                if not match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_name = match.iloc[0][name_col]
                    st.session_state.user_email = email_in
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
            else:
                st.error("Database connecting... Use admin login.")

    with t2:
        with st.form("reg_form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            niche = st.text_input("Niche (Focus Area)")
            pw = st.text_input("Set Password", type="password")
            
            if st.form_submit_button("Submit Registration"):
                payload = {
                    "entry.483203499": name,
                    "entry.1873870532": email,
                    "entry.1906780868": niche,
                    "entry.1396549807": pw
                }
                try:
                    requests.post(FORM_POST_URL, data=payload)
                    st.success("Registration transmitted! Please wait 60s for Google to sync.")
                    st.balloons()
                except:
                    st.error("Transmission failed.")
    st.stop()

# --- 5. DASHBOARD (Unlocked) ---
market_data = load_market_data()

with st.sidebar:
    st.title(f"Director: {st.session_state.user_name}")
    search_query = st.text_input("Global Intelligence Search", placeholder="e.g. AI, Fitness...", key="global_search")
    nav = st.radio("Modules", ["Global Pulse", "Script Architect"])
    
    st.divider()
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- MODULE: AUTONOMOUS GLOBAL PULSE (WITH IMAGES) ---
if nav == "Global Pulse":
    st.header("📈 Autonomous Market Intelligence")
    
    # 1. LIVE NEWS SOURCE
    RSS_URL = "https://techcrunch.com/feed/" 
    feed = feedparser.parse(RSS_URL)
    
    # Extract data for AI
    headlines = [entry.title for entry in feed.entries[:10]]
    headlines_str = " | ".join(headlines)

    # 2. THE LIVE FEED (Visual Cards)
    st.subheader("📡 Recent Intel")
    cols = st.columns(3)
    
    if feed.entries:
        for i, entry in enumerate(feed.entries[:3]):
            with cols[i]:
                # Try to find an image in the feed metadata
                img_url = "https://images.unsplash.com/photo-1518186239717-319049a9ec27?q=80&w=500&auto=format&fit=crop" # Default Placeholder
                if 'links' in entry:
                    for link in entry.links:
                        if 'image' in link.get('type', ''):
                            img_url = link.get('href')
                
                # If TechCrunch specific: they often hide images in 'media_content'
                try:
                    img_url = entry.media_content[0]['url']
                except:
                    pass

                # The "Authentic" Card Look
                st.image(img_url, use_container_width=True)
                st.markdown(f"**{entry.title}**")
                st.caption(f"📅 {entry.published[:16]}")
                st.markdown(f"[Read Full Intelligence]({entry.link})")
    
    st.divider()

    # 3. AI MARKET ANALYSIS (The "Brain") - Only runs once or on refresh
    if 'market_intelligence' not in st.session_state:
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            with st.spinner("AI is analyzing live market signals..."):
                analysis_prompt = f"Analyze: {headlines_str}. Identify top 5 niches. Format: Niche:Score. No chat."
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": analysis_prompt}]
                )
                raw_output = completion.choices[0].message.content.strip().split('\n')
                data_rows = [line.split(':') for line in raw_output if ":" in line and "Niche:" not in line]
                st.session_state.market_intelligence = pd.DataFrame(data_rows, columns=['Niche', 'Growth'])
                st.session_state.market_intelligence['Growth'] = pd.to_numeric(st.session_state.market_intelligence['Growth'])
        except Exception as e:
            st.error(f"Intelligence Bridge Error: {e}")

    # 4. THE VERTICAL AUTO-CHART
    st.subheader("📊 AI-Predicted Growth Velocity")
    if 'market_intelligence' in st.session_state and not st.session_state.market_intelligence.empty:
        fig = px.bar(
            st.session_state.market_intelligence, 
            x='Growth', y='Niche', orientation='h',
            color='Growth', color_continuous_scale='Viridis', template="plotly_dark"
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
        st.plotly_chart(fig, use_container_width=True)

    if st.button("🔄 Sync Live Intelligence"):
        if 'market_intelligence' in st.session_state:
            del st.session_state.market_intelligence
        st.rerun()            

# --- MODULE: SCRIPT ARCHITECT ---
elif nav == "Script Architect":
    st.header("💎 Script Architect")
    
    topic = st.text_input("Target Topic", value=search_query, placeholder="Enter your niche or video idea...", key="script_topic_input")
    
    format_type = st.radio(
        "Select Content Architecture:",
        ["📱 Short-Form (Reels/Shorts/TikTok)", "📺 Long-Form (YouTube/Masterclass)"],
        horizontal=True,
        key="format_selector"
    )
    
    if st.button("Generate Strategy", use_container_width=True):
        if topic:
            if "Short-Form" in format_type:
                system_prompt = "Generate a 60-second viral script. Focus on a 3-second visual hook, fast-paced value, and a high-energy CTA."
            else:
                system_prompt = "Generate a 10-minute video outline. Focus on an intro hook, storytelling arc, 3 deep-dive sections, and a long-term retention strategy."

            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                with st.spinner("Architecting your content..."):
                    completion = client.chat.completions.create(
                        model="llama-3.1-8b-instant", 
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Topic: {topic}"}
                        ]
                    )
                    st.markdown("---")
                    st.subheader(f"Strategy: {format_type}")
                    st.markdown(completion.choices[0].message.content)
            except Exception as e:
                st.error(f"AI Bridge Offline: {e}")
        else:
            st.warning("Please enter a topic to begin.")




