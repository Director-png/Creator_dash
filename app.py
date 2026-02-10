import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
import requests
import feedparser

# --- 1. CONFIG & CONNECTIONS ---
st.set_page_config(page_title="VOID OS", page_icon="🌑", layout="wide")

MARKET_URL = "https://docs.google.com/spreadsheets/d/163haIuPIna3pEY9IDxncPM2kFFsuZ76HfKsULcMu1y4/export?format=csv"
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"
FORM_POST_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfnNLb9O-szEzYfYEL85aENIimZFtMd5H3a7o6fX-_6ftU_HA/formResponse"

# --- 2. DATA LOADING FUNCTIONS ---
def load_market_data():
    try:
        df = pd.read_csv(MARKET_URL)
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        # FIX: Ensure the values column is numeric for the Treemap
        df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1], errors='coerce').fillna(0)
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

# --- 3. SESSION STATE INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'user_role' not in st.session_state:
    st.session_state.user_role = "user"
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'metric_1_label' not in st.session_state:
    st.session_state.metric_1_label = "Market Volatility"
if 'metric_1_val' not in st.session_state:
    st.session_state.metric_1_val = "High"
if 'daily_directive' not in st.session_state:
    st.session_state.daily_directive = "1. Code VOID OS\n2. Draft 3 Scripts\n3. 1 Client Lead\n4. Word is Law"

# --- 4. THE GATEKEEPER (LOGIN & REGISTRATION) ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🛡️ DIRECTOR'S INTELLIGENCE PORTAL</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Login", "📝 Register"])

    with t1:
        col_l, col_mid, col_r = st.columns([1, 2, 1])
        with col_mid:
            email_in = st.text_input("Email", key="login_email").lower().strip()
            pw_in = st.text_input("Password", type="password", key="login_pw").strip()
            
            if st.button("Access System", use_container_width=True):
                users = load_user_db()
                if email_in == "admin" and pw_in == "1234":
                    st.session_state.logged_in = True
                    st.session_state.user_name = "Master Director"
                    st.session_state.user_role = "admin"
                    st.rerun()
                elif not users.empty:
                    match = users[(users.iloc[:, 2].astype(str).str.lower() == email_in) & (users.iloc[:, 4].astype(str) == pw_in)]
                    if not match.empty:
                        st.session_state.logged_in = True
                        st.session_state.user_name = match.iloc[0, 1]
                        st.session_state.user_email = email_in
                        niche_val = str(match.iloc[0, 3]).lower()
                        st.session_state.user_role = "admin" if "fitness" in niche_val or "admin" in niche_val else "user"
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
                else:
                    st.error("Database connecting... Use admin login.")

    with t2:
        col_l, col_mid, col_r = st.columns([1, 2, 1])
        with col_mid:
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
                        st.success("Registration transmitted! Wait 60s for sync.")
                    except:
                        st.error("Transmission failed.")
    st.stop()

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #00d4ff;'>🌑 VOID OS</h1>", unsafe_allow_html=True)
    user_display = st.session_state.get('user_name', 'Operator')
    st.markdown(f"<p style='text-align: center; color: #00ff41; font-family: monospace;'>● {user_display.upper()}</p>", unsafe_allow_html=True)
    
    nav_options = ["📊 Dashboard", "🌐 Global Pulse", "⚔️ Trend Duel", "💎 Script Architect"]
    if st.session_state.user_role == "admin":
        nav_options.append("💼 Client Pitcher")
    
    nav = st.radio("COMMAND CENTER", nav_options)
    
    st.divider()
    if st.button("🔓 Terminate Session", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- 6. MODULES ---

if nav == "📊 Dashboard":
    st.markdown("<h1 style='color: white;'>🌑 VOID COMMAND CENTER</h1>", unsafe_allow_html=True)
    with st.expander("🛠️ Customize Dashboard Layout"):
        col_edit1, col_edit2 = st.columns(2)
        st.session_state.metric_1_label = col_edit1.text_input("Metric 1 Label", st.session_state.metric_1_label)
        st.session_state.metric_1_val = col_edit1.text_input("Metric 1 Value", st.session_state.metric_1_val)
        st.session_state.daily_directive = col_edit2.text_area("Edit Daily Directive", st.session_state.daily_directive)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label=st.session_state.metric_1_label, value=st.session_state.metric_1_val)
    m2.metric(label="Scripts Ready", value="24", delta="+6")
    m3.metric(label="Agency Leads", value="3", delta="Target: 10")
    m4.metric(label="System Status", value="Operational")

    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader("🚀 Active VOID Roadmap")
        df_road = pd.DataFrame({
            "Phase": ["VOID Intelligence", "Script Architect", "Client Pitcher", "Agency Portal"],
            "Status": ["Stable", "Stable", "Online", "Planned"],
            "Priority": ["Completed", "Active", "High", "Critical"]
        })
        st.table(df_road)
    with col_right:
        st.subheader("💡 Daily Directive")
        st.info(st.session_state.daily_directive)
        st.progress(45)

elif nav == "🌐 Global Pulse":
    st.title("🌐 GLOBAL INTELLIGENCE PULSE")
    data = load_market_data()
    
    if not data.empty:
        # DEBUG: Uncomment the line below if the box is still black to see your data structure
        # st.write(data.head()) 

        try:
            # Ensure the second column (values) is definitely a float/int
            data.iloc[:, 1] = pd.to_numeric(data.iloc[:, 1], errors='coerce').fillna(0)
            
            # Use iloc for the path and values to avoid NameErrors if headers change
            fig = px.treemap(
                data.head(20), 
                path=[data.columns[0]], 
                values=data.columns[1],
                color=data.columns[1],
                color_continuous_scale='Viridis', # High visibility scale
                template="plotly_dark"
            )
            
            fig.update_layout(margin=dict(t=10, l=10, r=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Visualization Logic Error: {e}")
    else:
        st.warning("Connection established, but no data found in the source sheet.")

    # Rest of your News/Analysis columns remain untouched...
    
    col_news, col_analysis = st.columns([2, 1])
    with col_news:
        st.subheader("📰 Live Tech Intelligence")
        feed = feedparser.parse("https://techcrunch.com/category/artificial-intelligence/feed/")
        for entry in feed.entries[:6]:
            st.markdown(f"### {entry.title}")
            st.write(entry.summary[:250] + "...")
            st.markdown(f"[🔗 DEPLOY FULL INTEL]({entry.link})")
            st.divider()
    with col_analysis:
        st.subheader("⚡ AI Trend Analysis")
        st.info("**Trending Keywords:**\n- LangGraph\n- Sora Visuals\n- Local LLMs\n- Groq LPUs")
        st.image("https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400")

elif nav == "⚔️ Trend Duel":
    st.subheader("⚔️ KEYWORD DUEL")
    trend_data = {
        'Rank': ['#01', '#02', '#03', '#04', '#05', '#06'],
        'Keyword': ['AI Agents', 'Short-form SaaS', 'UGC Ads', 'Newsletter Alpha', 'Faceless YT', 'High-Ticket DM'],
        'Growth': [94, 82, 77, 65, 89, 72],
        'Saturation': [20, 45, 80, 30, 60, 50],
        'YT_Potential': [95, 80, 60, 85, 98, 40],
        'IG_Potential': [88, 92, 95, 70, 85, 90],
        'Monetization': ['High', 'Very High', 'Medium', 'High', 'Medium', 'Extreme']
    }
    df = pd.DataFrame(trend_data)
    
    col_search1, col_search2 = st.columns(2)
    kw1 = col_search1.selectbox("Select Primary Keyword", df['Keyword'].unique(), index=0)
    kw2 = col_search2.selectbox("Select Challenger Keyword", df['Keyword'].unique(), index=1)

    d1 = df[df['Keyword'] == kw1].iloc[0]
    d2 = df[df['Keyword'] == kw2].iloc[0]

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.bar(x=['Growth', 'Saturation', 'YT Pot.', 'IG Pot.'], y=[d1['Growth'], d1['Saturation'], d1['YT_Potential'], d1['IG_Potential']], color_discrete_sequence=['#00d4ff'], height=300), use_container_width=True)
    with c2:
        st.plotly_chart(px.bar(x=['Growth', 'Saturation', 'YT Pot.', 'IG Pot.'], y=[d2['Growth'], d2['Saturation'], d2['YT_Potential'], d2['IG_Potential']], color_discrete_sequence=['#ff4b4b'], height=300), use_container_width=True)
    
    # YOUR ORIGINAL TABLE
    st.table(df[df['Keyword'].isin([kw1, kw2])].set_index('Rank'))
    st.divider()
    st.subheader("📋 CURRENT MARKET TRENDS")
    st.dataframe(df.set_index('Rank'), use_container_width=True)

elif nav == "💼 Client Pitcher":
    st.markdown("<h1 style='color: #000080;'>💼 VOID CAPITAL: PITCH GENERATOR</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1.5])
    with c1:
        client_name = st.text_input("Business Name")
        # YOUR ORIGINAL NICHE COLUMN
        niche = st.selectbox("Niche", ["Real Estate", "E-commerce", "SaaS", "Local Business"])
        offer = st.text_area("What are you selling?")
        pitch_btn = st.button("🔥 Generate Power Pitch")
    with c2:
        if pitch_btn and client_name:
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                prompt = f"Write a cold DM for {client_name} in {niche}. Offer: {offer}. Tone: Minimalist."
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                st.markdown("### The Pitch")
                st.write(res.choices[0].message.content)
            except Exception as e:
                st.error(f"Sync Error: {e}")

elif nav == "💎 Script Architect":
    st.markdown("<h1 style='color: #000080;'>✍️ VOID SCRIPT ARCHITECT</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5], gap="large")
    with col1:
        st.subheader("🛠️ Configuration")
        topic_input = st.text_input("Enter Focus Topic", key="topic_input")
        platform_choice = st.selectbox("Target Platform", ["YouTube Shorts", "Instagram Reels", "Long-form"], key="plat_choice")
        # YOUR ORIGINAL SELECT SLIDER
        tone_choice = st.select_slider("Script Tone", options=["Aggressive", "Professional", "Storyteller"], key="tone_choice")
        generate_btn = st.button("🚀 Architect Script", type="primary")
    with col2:
        if generate_btn and topic_input:
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                prompt = f"Write a {platform_choice} script about {topic_input}. Tone: {tone_choice}."
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                st.markdown(res.choices[0].message.content)
            except Exception as e:
                st.error(f"Error: {e}")

