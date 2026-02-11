import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
import requests
import feedparser
from bs4 import BeautifulSoup
from gspread_pandas import Spread # Ensure this is installed
from streamlit_lottie import st_lottie
import time

# --- ANIMATION UTILITY ---
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Lottie Animation Source (System Matrix style)
lottie_loading = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_fcfjwiyb.json")

# --- 1. CONFIG & CONNECTIONS ---
st.set_page_config(page_title="VOID OS", page_icon="🌑", layout="wide")

# --- 2. STARTING ANIMATION (SPLASH SCREEN) ---
if 'first_load' not in st.session_state:
    st.markdown("""
        <style>
        .stApp { background-color: #000000; }
        </style>
    """, unsafe_allow_html=True)
    
    empty_space = st.empty()
    with empty_space.container():
        st_lottie(lottie_loading, height=400, key="initial_load")
        st.markdown("<h1 style='text-align: center; color: #00d4ff; font-family: monospace;'>INITIALIZING VOID OS...</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #00ff41; font-family: monospace;'>DECRYPTING MARKET INTELLIGENCE LAYER</p>", unsafe_allow_html=True)
        time.sleep(3.0) # Cinematic delay
    
    empty_space.empty()
    st.session_state.first_load = True
    st.rerun()

# --- 3. GLOBAL CSS ANIMATIONS (Transitions & Glowing Effects) ---
# --- GLOBAL CSS & MATRIX ANIMATION ---
st.markdown("""
    <style>
    /* Matrix Rain Background (Only on Login) */
    .matrix-bg {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: black;
        overflow: hidden;
        z-index: -1;
    }
    
    /* Fade-In Page Transition */
    .stApp {
        animation: fadeInPage 1.5s ease-in-out;
    }
    @keyframes fadeInPage {
        0% { opacity: 0; filter: blur(5px); }
        100% { opacity: 1; filter: blur(0px); }
    }

    /* Glowing Metric pulse */
    [data-testid="stMetricValue"] {
        animation: neonPulse 2.5s infinite alternate;
        color: #00d4ff !important;
    }
    @keyframes neonPulse {
        from { text-shadow: 0 0 2px #00d4ff, 0 0 5px #00d4ff; }
        to { text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff; }
    }
    </style>
""", unsafe_allow_html=True)

# --- TYPEWRITER UTILITY ---
def typewriter_effect(text):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(full_text + "▌")
        time.sleep(0.005) # Speed of "decoding"
    container.markdown(full_text)

# --- 4. THE GATEKEEPER (With Matrix Aesthetic) ---
if not st.session_state.logged_in:
    # Adding the Matrix background div
    st.markdown('<div class="matrix-bg"></div>', unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: #00ff41; text-shadow: 0 0 10px #00ff41;'>🛡️ DIRECTOR'S INTELLIGENCE PORTAL</h1>", unsafe_allow_html=True)
    
    # ... keep your existing Login/Register Tabs logic here ...
# --- REST OF YOUR ORIGINAL FUNCTIONS ---
PULSE_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuN3zcXZqn9RMnPs7vNEa7vI9xr1Y2VVVlZLUcEwUVqsVqtLMadz1L_Ap4XK_WPA1nnFdpqGr8B_uS/pub?output=csv"

def load_market_pulse_data():
    try:
        df = pd.read_csv(PULSE_CSV_URL)
        df.columns = [str(c).strip().lower() for c in df.columns]
        mapping = {
            'niche name': 'Niche',
            'score': 'Score',
            'news snipett': 'Reason',
            'growth': 'Growth'
        }
        df = df.rename(columns=mapping)
        if 'Niche' not in df.columns:
            st.error(f"Mapping failed. Available: {list(df.columns)}")
            return pd.DataFrame()
        df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0)
        return df.dropna(subset=['Niche'])
    except Exception as e:
        st.error(f"VOID Sync Error: {e}")
        return pd.DataFrame()

def load_market_data():
    try:
        df = pd.read_csv(MARKET_URL)
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        df.iloc[:, 1] = df.iloc[:, 1].astype(str).replace(r'[%\$,]', '', regex=True)
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

def get_intel_image(entry):
    try:
        if 'media_content' in entry: return entry.media_content[0]['url']
    except: pass
    try:
        if 'summary' in entry:
            soup = BeautifulSoup(entry.summary, 'html.parser')
            img = soup.find('img')
            if img and img.get('src'): return img['src']
    except: pass
    return f"https://picsum.photos/seed/{len(entry.title)}/400/250"

MARKET_URL = "https://docs.google.com/spreadsheets/d/163haIuPIna3pEY9IDxncPM2kFFsuZ76HfKsULcMu1y4/export?format=csv"
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"
FORM_POST_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfnNLb9O-szEzYfYEL85aENIimZFtMd5H3a7o6fX-_6ftU_HA/formResponse"

# --- 3. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_role' not in st.session_state: st.session_state.user_role = "user"
if 'user_email' not in st.session_state: st.session_state.user_email = ""
if 'metric_1_label' not in st.session_state: st.session_state.metric_1_label = "Market Volatility"
if 'metric_1_val' not in st.session_state: st.session_state.metric_1_val = "High"
if 'daily_directive' not in st.session_state: st.session_state.daily_directive = "1. Code VOID OS\n2. Draft 3 Scripts\n3. 1 Client Lead\n4. Word is Law"

# --- 4. THE GATEKEEPER ---
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
                        st.session_state.user_role = "admin" if any(x in niche_val for x in ["fitness", "admin"]) else "user"
                        st.rerun()
                    else: st.error("Invalid credentials.")
                else: st.error("Database connecting... Use admin login.")
    with t2:
        col_l, col_mid, col_r = st.columns([1, 2, 1])
        with col_mid:
            with st.form("reg_form"):
                name = st.text_input("Name")
                email = st.text_input("Email")
                niche = st.text_input("Niche (Focus Area)")
                pw = st.text_input("Set Password", type="password")
                if st.form_submit_button("Submit Registration"):
                    payload = {"entry.483203499": name, "entry.1873870532": email, "entry.1906780868": niche, "entry.1396549807": pw}
                    try:
                        requests.post(FORM_POST_URL, data=payload)
                        st.success("Registration transmitted!")
                    except: st.error("Transmission failed.")
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #00d4ff;'>🌑 VOID OS</h1>", unsafe_allow_html=True)
    user_display = st.session_state.get('user_name', 'Operator')
    st.markdown(f"<p style='text-align: center; color: #00ff41; font-family: monospace;'>● {user_display.upper()}</p>", unsafe_allow_html=True)
    nav_options = ["📊 Dashboard", "🌐 Global Pulse", "⚔️ Trend Duel", "💎 Script Architect"]
    if st.session_state.user_role == "admin": nav_options.append("💼 Client Pitcher")
    nav = st.radio("COMMAND CENTER", nav_options)
    st.divider()
    if st.button("🔓 Terminate Session", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- 6. MODULES ---
if nav == "📊 Dashboard":
    st.markdown("<h1 style='color: white;'>🌑 VOID COMMAND CENTER</h1>", unsafe_allow_html=True)
    with st.expander("🛠️ Customize Layout"):
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
        df_road = pd.DataFrame({"Phase": ["VOID Intelligence", "Script Architect", "Client Pitcher", "Agency Portal"],
                                "Status": ["Stable", "Stable", "Online", "Planned"],
                                "Priority": ["Completed", "Active", "High", "Critical"]})
        st.table(df_road)
    with col_right:
        st.subheader("💡 Daily Directive")
        st.info(st.session_state.daily_directive)
        st.progress(45)

elif nav == "🌐 Global Pulse":
    st.title("🌐 GLOBAL INTELLIGENCE PULSE")
    data = load_market_data()
    
    if not data.empty:
        st.subheader("🔥 TOP MARKET OPPORTUNITIES")
        top_movers = data.sort_values(by=data.columns[1], ascending=False).head(3)
        cols = st.columns(3)
        for i, (index, row) in enumerate(top_movers.iterrows()):
            with cols[i]:
                st.metric(label=row.iloc[0], value=f"{row.iloc[1]}%", delta="High Heat")
                st.caption(f"**Why:** {row.iloc[2]}")
        st.divider()

        chart_data = data.sort_values(by=data.columns[1], ascending=False).head(10)
        fig = px.bar(chart_data, x=chart_data.columns[1], y=chart_data.columns[0], orientation='h',
                     color=chart_data.columns[1],
                     color_continuous_scale=[[0, '#ADD8E6'], [0.5, '#0000FF'], [1, '#000080']],
                     template="plotly_dark")
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, coloraxis_showscale=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    col_news, col_analysis = st.columns([2, 1])
    with col_news:
        st.subheader("📰 Live Tech Intelligence")
        feed = feedparser.parse("https://techcrunch.com/category/artificial-intelligence/feed/")
        for entry in feed.entries[:6]:
            c_img, c_txt = st.columns([1, 2.5])
            with c_img:
                st.image(get_intel_image(entry), use_container_width=True)
            with c_txt:
                st.markdown(f"**[{entry.title.upper()}]({entry.link})**")
                st.write(BeautifulSoup(entry.summary, "html.parser").text[:120] + "...")
            st.divider()
    with col_analysis:
        st.subheader("⚡ AI Trend Analysis")
        st.info("**Trending Keywords:**\n- LangGraph\n- Sora Visuals\n- Local LLMs\n- Groq LPUs")
        st.image("https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400")

elif nav == "⚔️ Trend Duel":
    st.title("⚔️ COMPETITIVE INTELLIGENCE MATRIX")
    pulse_df = load_market_pulse_data()
    
    if pulse_df.empty:
        st.warning("VOID Sheet is empty. Please run the Apps Script.")
    else:
        st.subheader("🌑 VOID Market Pulse Integration")
        niche_list = pulse_df['Niche'].unique().tolist()
        selected_niches = st.multiselect(
            "Select Niches to Compare",
            options=niche_list,
            default=niche_list[:5] if len(niche_list) > 5 else niche_list
        )
        comparison_df = pulse_df[pulse_df['Niche'].isin(selected_niches)]
        if not comparison_df.empty:
            st.bar_chart(data=comparison_df, x='Niche', y='Score')
            st.dataframe(comparison_df)

elif nav == "💼 Client Pitcher":
    st.markdown("<h1 style='color: #00d4ff;'>💼 VOID CAPITAL: PITCH GENERATOR</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1.5])
    with c1:
        client_name = st.text_input("Lead Name / Handle")
        niche_category = st.selectbox("Category Type", [
            "Personal Brand (Fitness/Mindset)", 
            "B2B Technical (AI/SaaS)",
            "Fashion & Luxury (Apparel/E-com)",
            "Hospitality (Restaurants/Cafes)",
            "Local Business (Real Estate/Gyms)"
        ])
        offer = st.text_area("What's the unique value proposition?")
        pitch_btn = st.button("🔥 Generate VOID Pitch", type="primary")

    with c2:
        if pitch_btn and client_name:
            with st.spinner("🌑 ACCESSING VOID COGNITION..."):
                try:
                    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    system_prompt = "You are a world-class high-ticket closer."
                    if "Fashion" in niche_category:
                        style = "Focus on aesthetic edge, viral trend-jacking, and scarcity. Tone: Sophisticated."
                    elif "Hospitality" in niche_category:
                        style = "Focus on floor-traffic and automated bookings. Tone: High-energy."
                    elif "Personal Brand" in niche_category:
                        style = "Focus on community and transformation. Tone: Relatable but elite."
                    else:
                        style = "Focus on ROI and efficiency. Tone: Cold and calculated."
                    
                    full_prompt = f"Write a pitch for {client_name}. Style: {style}. Offer: {offer}"
                    res = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": full_prompt}]
                    )
                    # Instead of st.success(res.choices[0].message.content)
                    typewriter_effect(res.choices[0].message.content)
                except Exception as e:
                    st.error(f"Sync Error: {e}")
                        
elif nav == "💎 Script Architect":
    st.markdown("<h1 style='color: #00ff41;'>✍️ VOID SCRIPT ARCHITECT</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5], gap="large")
    with col1:
        topic_input = st.text_input("Enter Focus Topic")
        platform_choice = st.selectbox("Target Platform", ["YouTube Shorts", "Instagram Reels", "Long-form"])
        tone_choice = st.select_slider("Script Tone", options=["Aggressive", "Professional", "Storyteller"])
        generate_btn = st.button("🚀 Architect Script", type="primary")
    with col2:
        if generate_btn and topic_input:
            with st.spinner("🌑 COMPILING SCRIPT DATA..."):
                try:
                    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    prompt = f"Write a {platform_choice} script about {topic_input}. Tone: {tone_choice}."
                    res = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                    # Instead of st.markdown(res.choices[0].message.content)
                    typewriter_effect(res.choices[0].message.content)
                except Exception as e: st.error(f"Error: {e}")

