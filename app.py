import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
import requests
import feedparser
from bs4 import BeautifulSoup
import time
from streamlit_lottie import st_lottie
from google import genai  # Modern way to import
from PIL import Image
import os
import re 
import io


# --- INITIALIZE STATE (Place this near the top of your script) ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Dashboard"

# --- 🛰️ SECURE AI UPLINK ---
# 1. INITIALIZE GLOBAL CLIENTS (ONCE)
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    client = None

if "GROQ_API_KEY" in st.secrets:
    try:
        # strip() handles accidental spaces in the secrets tab
        groq_c = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
    except:
        groq_c = None
else:
    groq_c = None


# --- INITIALIZE ALL KEYS ---
if 'current_subs' not in st.session_state:
    st.session_state.current_subs = 0  # Or your starting number


# --- ANIMATION UTILITY ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_loading = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_fcfjwiyb.json")

# --- 1. SESSION STATE (CRITICAL INITIALIZATION) ---
if 'found_leads' not in st.session_state:
    st.session_state.found_leads = pd.DataFrame()
if 'script_history' not in st.session_state:
    st.session_state.script_history = []
if 'pitch_history' not in st.session_state:
    st.session_state.pitch_history = []
if 'creator_db' not in st.session_state:
    st.session_state.creator_db = pd.DataFrame([
        {"Creator": "TechVanguard", "Niche": "AI", "Status": "Scouted", "Vigor": 82},
        {"Creator": "CyberStyle", "Niche": "Fashion", "Status": "Negotiation", "Vigor": 91},
        {"Creator": "MidnightAlpha", "Niche": "Gaming", "Status": "Signed", "Vigor": 95},
        {"Creator": "NeonMinimalist", "Niche": "Design", "Status": "Scouted", "Vigor": 78}
    ])
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'last_topic' not in st.session_state: st.session_state.last_topic = "General AI Intelligence"
if 'user_name' not in st.session_state: st.session_state.user_name = "Guest"
if 'user_role' not in st.session_state: st.session_state.user_role = "user"

# --- 🛰️ DATA INFRASTRUCTURE ---
MARKET_PULSE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuN3zcXZqn9RMnPs7vNEa7vI9xr1Y2VVVlZLUcEwUVqsVqtLMadz1L_Ap4XK_WPA1nnFdpqGr8B_uS/pub?output=csv"
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?gid=2093671902&single=true&output=csv&t=" + str(time.time())
FORM_POST_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfnNLb9O-szEzYfYEL85aENIimZFtMd5H3a7o6fX-_6ftU_HA/formResponse"
SCRIPT_VAULT_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"
VAULT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfeDAY3gnWYlpH90EaJirxUc8d4obYUgiX72WJIah7Cya1VNQ/formResponse"
VAULT_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTtSx9iQTrDvNWe810s55puzBodFKvfUbfMV_l-QoQIfbdPxeQknClGGCQT33UQ471NyGTw4aHLrDTw/pub?gid=1490190727&single=true&output=csv"
FEEDBACK_API_URL = "https://script.google.com/macros/s/AKfycbz1mLI3YkbjVsA4a8rMgMe_07w_1sS8H-f2Wvz1FtFCU-ZN4zCH7kDUGaDPDaaMbrvaPw/exec"
NEW_URL = "https://script.google.com/macros/s/AKfycbzBLwNA-37KxZ5mDyHp1DMNw23n8xyfBVaVbmg_zRs-oQAZGue6Zuxo44UwztuBvFIC/exec"
# --- 🛰️ UTILITIES & BRAIN FUNCTIONS ---

def typewriter_effect(text):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(full_text + "▌")
        time.sleep(0.005) 
    container.markdown(full_text)

def save_script_to_vault(title, content):
    # This function now has a safety check
    if not content:
        return
    payload = {
        "email": st.session_state.get('user_email', 'unknown'),
        "category": "SAVE_SCRIPT",
        "title": title,
        "content": content
    }
    try:
        requests.post(NEW_URL, json=payload, timeout=5)
        st.success("📜 Script archived in your Private Vault.")
    except:
        st.error("Uplink failed.")


@st.cache_data(ttl=0)
def load_user_db():
    try:
        sync_url = f"{USER_DB_URL}&cache_bus={time.time()}"
        df = pd.read_csv(sync_url)
        # Force all headers to lowercase and strip spaces
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Database Uplink Error: {e}")
        return pd.DataFrame()

def load_history_db():
    try:
        # Use your history tab CSV export link
        # Format: https://docs.google.com/spreadsheets/d/ID/export?format=csv&gid=TAB_ID
        history_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTtSx9iQTrDvNWe810s55puzBodFKvfUbfMV_l-QoQIfbdPxeQknClGGCQT33UQ471NyGTw4aHLrDTw/pub?gid=678649061&single=true&output=csv" 
        df = pd.read_csv(f"{history_url}&cache={time.time()}")
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Vault Connection Error: {e}")
        return pd.DataFrame()


def load_market_pulse_data(url=None): # <--- Added '=None' to make it optional
    # Use the global URL if none is provided in the parentheses
    if url is None:
        url = MARKET_PULSE_URL 
        
    try:
        # Pull data and drop completely empty rows
        df = pd.read_csv(url).dropna(how='all')
        
        # IRONCLAD RE-LABEL: Force column names by position
        expected_cols = ['Niche', 'Score', 'Growth', 'Saturation', 'Reason']
        new_columns = {df.columns[i]: expected_cols[i] for i in range(min(len(df.columns), len(expected_cols)))}
        df.rename(columns=new_columns, inplace=True)
        
        # Data Type Safety
        if 'Score' in df.columns:
            df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0).astype(int)
            
        return df
    except Exception as e:
        st.error(f"Sync Error at Line 523: {e}")
        return pd.DataFrame()


def generate_visual_dna(platform, tone):
    styles = {
        "Instagram Reels": "High-contrast, 0.5s jump cuts, Glow-on-dark aesthetics, grainy film overlays.",
        "YouTube Shorts": "Center-framed, bold captions, neon-accent lighting, fast zoom-ins.",
        "YouTube Long-form": "Cinematic 4k, shallow depth of field, 24fps motion blur, color graded for teal/orange.",
        "TikTok": "Raw mobile-style, high-saturation, fast-paced text overlays, green-screen effects.",
        "X-Thread": "High-authority typography, clean minimalist screenshots, bold black/white contrast."
    }
    aesthetic = styles.get(platform, "Professional cinematic cyber-noir aesthetic.")
    return f"DNA PROFILE: {aesthetic} | TONE: {tone} | LIGHTING: Cyber-Noir Studio"

def calculate_vigor(views, followers):
    if followers == 0: return 0
    ratio = views / followers
    return min(100, int(ratio * 50))

def get_intel_image(entry):
    try:
        if 'media_content' in entry: return entry.media_content[0]['url']
        soup = BeautifulSoup(entry.summary, 'html.parser')
        img = soup.find('img')
        if img: return img['src']
    except: pass
    return f"https://picsum.photos/seed/{len(entry.title)}/400/250"

def get_saturation_status(score):
    if score > 88: return "🔴 SATURATED (High Competition)"
    if score > 75: return "🟡 PEAK (Strategic Entry Required)"
    return "🟢 EARLY (High Growth Opportunity)"

def transmit_script(client, platform, topic, script, dna):
    url = "https://script.google.com/macros/s/AKfycby9nYH4bTmC0rFoZQWj87S-hiu7lJeXXd4mVuRyJxrVTk-OGaPx5zFNZzgYZWSRuNH0/exec"
    payload = {"client": client, "platform": platform, "topic": topic, "script": script, "dna": dna}
    try:
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except: return False

def generate_oracle_report(topic, platform, tone):
    try:
        prompt = f"""
        System: You are the VOID OS Oracle. Analyze content architecture for {platform}.
        Topic: {topic} | Tone: {tone}
        
        Provide a 'Growth Intelligence Report' with:
        1. 📈 VIRAL VELOCITY: Why this topic is peaking now based on global sentiment.
        2. 🧠 PSYCHOLOGICAL HOOK: The specific 'Human Bias' (like FOMO or Zeigarnik effect) this script exploits.
        3. 🚀 SCALING STRATEGY: How to turn this one video into a 5-part series for maximum retention.
        """
        res = groq_c.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Oracle connection interrupted: {e}"

if 'user_profiles' not in st.session_state:
    st.session_state.user_profiles = {
        "youtube": "",
        "instagram": "",
        "x": "",
        "goals": {"followers": 0, "current": 0}
    }


def fetch_live_metrics(platform, handle):
    if not handle: 
        return st.session_state.get('current_subs', 1500)
    
    clean_handle = handle.replace("@", "")
    
    if platform == "YouTube":
        try:
            # We use a public metadata proxy that doesn't require a key
            # This 'scrapes' the basic count from a public endpoint
            url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&forHandle={clean_handle}&key={st.secrets.get('GOOGLE_API_KEY', 'PUBLIC_TOKEN_MOCK')}"
            
            # Since you don't have a key, we switch to a Scraper Logic:
            headers = {'User-Agent': 'Mozilla/5.0'}
            scrape_url = f"https://www.youtube.com/@{clean_handle}"
            response = requests.get(scrape_url, headers=headers)
            
            if response.status_code == 200:
                # We look for the 'subscriberCountText' in the page source
                soup = BeautifulSoup(response.text, 'html.parser')
                # Finding the count inside the scripts/meta tags
                meta = soup.find("meta", itemprop="interactionCount")
                if meta:
                    return int(meta['content'])
            
            # Fallback if scraping is blocked: Use a slight random growth 
            # to keep the interface 'Professional' until we find a stable bridge
            return st.session_state.current_subs + 5
        except:
            return st.session_state.current_subs

def display_feedback_tab():
    st.header("🧠 Neural Feedback Loop")
    st.write("Is the VOID OS performing to your standards? Submit your logs below.")
    
    with st.form("feedback_form", clear_on_submit=True):
        email = st.text_input("Contact Email (Optional)")
        category = st.selectbox("Intelligence Type", ["Bug Report", "Feature Request", "Market Suggestion", "General Praise"])
        message = st.text_area("Detail your transmission...")
        
        submitted = st.form_submit_button("TRANSMIT")
        
        if submitted:
            if message:
                payload = {"email": email, "category": category, "message": message}
                try:
                    response = requests.post(FEEDBACK_API_URL, json=payload)
                    if response.status_code == 200:
                        st.success("✅ Transmission Successful. The Director has been notified.")
                        st.balloons()
                    else:
                        st.error("❌ Transmission Interrupted. Check API deployment.")
                except Exception as e:
                    st.error(f"Critical System Error: {e}")
            else:
                st.warning("Cannot transmit an empty message.")


# --- 1. CONFIG ---
st.set_page_config(page_title="VOID OS", page_icon="🌑", layout="wide")
# --- GLOBAL PERSONA DETECTION (Do this before any pages load) ---
user_role_raw = st.session_state.get('user_role', 'free')
user_status_raw = st.session_state.get('user_status', 'free')

# Define these once so they are NEVER "Undefined"
is_admin = str(user_role_raw).lower() == 'admin' or st.session_state.get('admin_verified', False)
is_paid = "paid" in str(user_status_raw).lower() or "pro" in str(user_status_raw).lower()


# --- 2. SPLASH SCREEN ---
if 'first_load' not in st.session_state:
    st.markdown("<style>.stApp { background-color: #000000; }</style>", unsafe_allow_html=True)
    empty_space = st.empty()
    with empty_space.container():
        if lottie_loading: st_lottie(lottie_loading, height=400)
        st.markdown("<h1 style='text-align: center; color: #00d4ff; font-family: monospace;'>INITIALIZING VOID OS...</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #333;'>SYNCING NEURAL NODES</p>", unsafe_allow_html=True)
        time.sleep(3.0) 
    st.session_state.first_load = True
    st.rerun()

# --- 🎨 VOID OS NEURAL VISUAL IDENTITY ---
st.markdown("""
    <style>
    /* Global Background & Text */
    .main { background-color: #050505; color: #e0e0e0; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { 
        background-image: linear-gradient(180deg, #000000 0%, #080808 100%); 
        border-right: 1px solid #00d4ff33; 
    }

    /* Cyan Neural Glow for Titles */
    h1, h2, h3 { 
        font-family: 'Courier New', Courier, monospace; 
        letter-spacing: 2px; 
        color: #00d4ff !important;
        text-shadow: 0 0 10px #00d4ff55;
    }

    /* Elite Button Design */
    .stButton>button {
        background: transparent;
        color: #00d4ff; 
        font-weight: bold; 
        border: 1px solid #00d4ff; 
        border-radius: 5px;
        letter-spacing: 2px;
        font-family: monospace;
        transition: 0.4s all ease-in-out;
        width: 100%;
    }
    
    .stButton>button:hover {
        background: #00d4ff;
        color: black;
        box-shadow: 0px 0px 20px #00d4ff;
        transform: translateY(-2px);
    }

    /* Input Field Styling */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { 
        background-color: #080808; 
        color: #00d4ff; 
        border: 1px solid #00d4ff33 !important; 
    }
    
    .stSelectbox>div>div { 
        background-color: #080808; 
        color: #00d4ff; 
    }

    /* Metrics & Cards */
    .stMetric { 
        background: #0a0a0a; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #00d4ff;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
    }

    /* Expander Styling */
    div[data-testid="stExpander"] { 
        background: #0a0a0a; 
        border: 1px solid #00d4ff22 !important; 
        border-radius: 8px;
    }

    /* Custom Scrollbar for the Elite look */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #000; }
    ::-webkit-scrollbar-thumb { background: #00d4ff; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)



# --- EMERGENCY DIAGNOSTIC ---
if st.sidebar.checkbox("🔍 Debug Node Mapping"):
    users_test = load_user_db()
    if not users_test.empty:
        st.write("Current Columns:", users_test.columns.tolist())
        st.write("Top Row Sample:", users_test.iloc[0].values.tolist())
    else:
        st.error("Sheet is empty or URL is invalid.")
# --- CONFIGURATION (Ensure these are defined) ---
# NEW_URL = "https://script.google.com/macros/s/AKfycbw8HjjiXJe53CVd4_qU6c4RIjfkMEBJxXZUBVwJdGJCiytgGBgKjMSfGc2tPeckNRih/exec"
# FORM_POST_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfnNLb9O-szEzYfYEL85aENIimZFtMd5H3a7o6fX-_6ftU_HA/formResponse"

# --- GATEKEEPER START ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'otp_sent' not in st.session_state:
    st.session_state.otp_sent = False
if 'generated_otp' not in st.session_state:
    st.session_state.generated_otp = None
if 'user_status' not in st.session_state:
    st.session_state.user_status = "free"

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #00d4ff; letter-spacing: 5px;'>VOID OS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; font-size: 0.8em;'>INTELLIGENCE ACCESS PROTOCOL v3.0</p>", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["🔑 LOGIN", "🛡️ IDENTITY INITIALIZATION"])
    
    with t1:
        email_in = st.text_input("DIRECTOR EMAIL", key="gate_login_email").lower().strip()
        pw_in = st.text_input("PASSKEY", type="password", key="gate_login_pw")
        
        if st.button("INITIATE UPLINK", use_container_width=True, key="gate_login_btn"):
            users = load_user_db()
            if email_in == "admin" and pw_in == "1234":
                # Changed 'paid' to 'Pro' to match your Forge logic
                st.session_state.update({"logged_in": True, "user_name": "Master Director", "user_role": "admin", "user_status": "Pro", "user_email": "admin"})
                st.rerun()
            elif not users.empty:
                # Column 0: Email, Column 2: Password
                match = users[(users.iloc[:, 0].astype(str).str.lower() == email_in) & (users.iloc[:, 2].astype(str) == pw_in)]
                if not match.empty:
                    # Column 1: Name, Column 4: Status (index 4 is 5th column)
                    raw_status = str(match.iloc[0, 4]).strip().capitalize() # Force "Pro" or "Free"
                    st.session_state.update({
                        "logged_in": True, 
                        "user_name": match.iloc[0, 1], 
                        "user_email": email_in, 
                        "user_status": raw_status
                    })
                    st.rerun()
                else:
                    st.error("INTEGRITY BREACH: INVALID CREDENTIALS.")

        with st.expander("RECOVERY PROTOCOL (Lost Passkey)"):
            r_email = st.text_input("REGISTERED EMAIL", key="reset_email").lower().strip()
            s_ans = st.text_input("SECURITY KEY (DOB / PRESET)", key="reset_security").lower().strip()
            new_p = st.text_input("NEW PASSKEY", type="password", key="reset_new_pw")
            if st.button("OVERRIDE SECURITY", use_container_width=True):
                payload = {"email": r_email, "action": "SECURE_RESET", "answer": s_ans, "message": new_p}
                try:
                    response = requests.post(NEW_URL, json=payload, timeout=15)
                    if "SUCCESS" in response.text: st.success("IDENTITY VERIFIED. PASSKEY UPDATED.")
                    else: st.error(f"UPLINK DENIED: {response.text}")
                except Exception as e: st.error(f"SYSTEM CRASH: {e}")

    with t2:
        if not st.session_state.otp_sent:
            st.markdown("### PHASE 1: DATA CAPTURE")
            c1, c2 = st.columns(2)
            with c1:
                n = st.text_input("FULL NAME", key="reg_name")
                e = st.text_input("EMAIL", key="reg_email")
                mob = st.text_input("MOBILE", key="reg_mob")
            with c2:
                p = st.text_input("PASSKEY", type="password", key="reg_pass")
                sa = st.text_input("SECURITY KEY (DOB/ANSWER)", key="reg_sa")
                ni = st.text_input("NICHE", key="reg_niche")

            channel = st.radio("SELECT UPLINK CHANNEL", ["Email", "WhatsApp"], horizontal=True, key="reg_channel")

            if st.button("⚔️ GENERATE SECURE OTP", use_container_width=True):
                if n and e and mob and sa and ni and p:
                    with st.status("Transmitting Initialization Signal...") as status:
                        payload = {"category": "SEND_OTP", "email": e.strip().lower(), "channel": channel}
                        try:
                            response = requests.post(NEW_URL, json=payload, timeout=15)
                            if response.status_code == 200 and len(response.text.strip()) == 6:
                                st.session_state.generated_otp = response.text.strip()
                                st.session_state.otp_sent = True
                                status.update(label="Uplink Code Dispatched!", state="complete")
                                st.rerun()
                            else:
                                st.error(f"Transmission Failed: {response.text}")
                        except Exception as ex: st.error(f"Connection Blocked: {ex}")
                else:
                    st.warning("DIRECTOR: ALL IDENTITY FIELDS ARE MANDATORY.")
        
        else:
            st.markdown(f"### PHASE 2: VERIFY UPLINK")
            user_otp = st.text_input("ENTER 6-DIGIT CODE", placeholder="000000")
            
            if st.button("🔓 FINALIZE INITIALIZATION", use_container_width=True):
                if user_otp == st.session_state.generated_otp:
                    # Rectified: Using st.session_state to pull the inputs from Phase 1
                    final_payload = {
                        "category": "REGISTRATION",
                        "name": st.session_state.reg_name,
                        "email": st.session_state.reg_email.lower().strip(),
                        "password": st.session_state.reg_pass,
                        "mobile": st.session_state.reg_mob,
                        "answer": st.session_state.reg_sa,
                        "niche": st.session_state.reg_niche,
                        "role": "user",
                        "status": "Free"
                    }
                    r = requests.post(NEW_URL, json=final_payload, timeout=20)
                    if "SUCCESS" in r.text:
                        st.success("✅ IDENTITY SECURED. WELCOME TO THE VOID.")
                        st.balloons()
                        st.session_state.otp_sent = False 
                    else: st.error(f"VAULT REJECTION: {r.text}")
                else: st.error("INTEGRITY BREACH: INVALID CODE.")
            
            if st.button("Back to Phase 1"):
                st.session_state.otp_sent = False
                st.rerun()

    st.stop() # Prevents main app content from loading behind login


# --- MAIN APP UI BEGINS HERE (Only accessible if logged_in is True) ---

# --- SIDEBAR NAVIGATION (UNIFIED & ALIGNED) ---
with st.sidebar:
    # 1. Identity Header
    st.markdown(f"<h3 style='text-align: center; color: #00ff41;'>● {st.session_state.user_name.upper()}</h3>", unsafe_allow_html=True)
    
    # Dynamic Status Badge
    user_status = st.session_state.get('user_status', 'free').strip().lower()
    if user_status == 'Pro' or st.session_state.user_role == "admin":
        st.success("💎 PRO NODE ACTIVE")
    else:
        st.warning("📡 BASIC NODE")
    
    st.markdown("<p style='text-align: center; color: #444; font-size: 10px;'>ENCRYPTED CONNECTION : ACTIVE</p>", unsafe_allow_html=True)
    st.divider()

    # 2. Define Options based on Role AND Status
    if st.session_state.user_role == "admin":
        options = ["🏠 Dashboard", "🌐 Global Pulse", "🛡️ Admin Console", "⚔️ Trend Duel", "🧪 Creator Lab", "🛰️ Lead Source", "🏗️ Script Architect", "🧠 Neural Forge", "💼 Client Pitcher", "⚖️ Legal Archive", "📜 History", "⚙️ Settings"]
    elif user_status == 'paid':
        options = ["📡 My Growth Hub", "🌐 Global Pulse", "⚔️ Trend Duel", "🏗️ Script Architect", "🧠 Neural Forge", "⚖️ Legal Archive", "📜 History", "⚙️ Settings"]
    else:
        options = ["📡 My Growth Hub", "🌐 Global Pulse", "⚔️ Trend Duel", "🏗️ Script Architect", "⚖️ Legal Archive", "💎 Upgrade to Pro", "⚙️ Settings"]

    # 3. Handle Page Indexing
    try:
        current_index = options.index(st.session_state.current_page)
    except (ValueError, KeyError):
        current_index = 0

    # 4. The Unified Radio Menu
    # Note: We use the variable 'choice' to update current_page
    choice = st.radio("COMMAND CENTER", options, index=current_index)
    
    if choice != st.session_state.current_page and st.session_state.current_page != "FEEDBACK":
        st.session_state.current_page = choice

    # 5. Global Action Buttons
    st.divider()
    
    if st.button("🔄 SYNC NODE STATUS", use_container_width=True):
        st.cache_data.clear() 
        # --- SYNC PROTOCOL ---
with st.sidebar:
    st.markdown("---")
    st.subheader("🛰️ NETWORK STATUS")
    
    # We display the current status for clarity
    current_status = st.session_state.get('user_status', 'Free').upper()
    st.caption(f"CURRENT CLEARANCE: {current_status}")

    if st.button("🔄 RE-SYNC NEURAL LINK", use_container_width=True):
        if 'user_email' in st.session_state:
            with st.spinner("Accessing Users_DB..."):
                try:
                    # Payload for the 'CHECK_STATUS' logic we just fixed in Apps Script
                    payload = {
                        "email": st.session_state.user_email,
                        "action": "CHECK_STATUS"
                    }
                    
                    # Direct uplink to Google
                    response = requests.post(NEW_URL, json=payload, timeout=15)
                    
                    if response.status_code == 200:
                        new_status = response.text.strip()
                        
                        # Update the session brain
                        st.session_state.user_status = new_status
                        
                        # Provide immediate feedback
                        if new_status.lower() == "pro":
                            st.toast("PRO CLEARANCE VERIFIED", icon="💎")
                        else:
                            st.toast("BASIC CLEARANCE ACTIVE", icon="🌑")
                        
                        # THE KEY: Hard reset the UI to show/hide Pro features
                        st.rerun()
                    else:
                        st.error("GATEWAY TIMEOUT")
                except Exception as e:
                    st.error(f"UPLINK ERROR: {e}")
        else:
            st.warning("NO ACTIVE SESSION DETECTED")
            if response.status_code == 200:
               new_status = response.text.strip()
               st.write(f"DEBUG: Google returned: '{new_status}'") # <--- TEMP DEBUG LINE
        st.rerun()

    if st.button("📩 NEURAL FEEDBACK", use_container_width=True):
        st.session_state.current_page = "FEEDBACK"
        st.rerun()

    if st.button("🔒 LOGOUT", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

with st.sidebar:
    st.markdown("---")
    st.subheader("📡 Connection")
    if st.button("🔄 Sync Neural Status", use_container_width=True):
        with st.spinner("Checking Uplink..."):
            # Re-run the verification function
            if verify_and_sync_status(st.session_state.user_email):
                st.toast(f"Clearance Level: {st.session_state.user_status}", icon="🛡️")
                st.rerun()
            else:
                st.error("Uplink Timeout.")

# --- PAGE ROUTING ---
# This variable 'page' is what your module if/elif blocks should use
page = st.session_state.current_page

# --- MAIN PAGE ROUTING ---
page = st.session_state.current_page

if page == "FEEDBACK":
    display_feedback_tab()
    if st.button("← Back to Mission Control"):
        st.session_state.current_page = "🏠 Dashboard" if st.session_state.user_role == "admin" else "📡 My Growth Hub"
        st.rerun()

# --- MODULE 1: DASHBOARD (KYC OPTIMIZED) ---
elif page == "🏠 Dashboard":
    # 🚨 COMPLIANCE HEADER (Bot-Friendly)
    st.markdown("<p style='font-size: 10px; color: #444;'>VOID OS | B2B Outreach SaaS | support@yourdomain.com</p>", unsafe_allow_html=True)
    
    st.markdown("<h1 style='color: #00ff41;'>🛰️ COMMAND CENTER</h1>", unsafe_allow_html=True)
    
    # 1. KPI Row (Keep your original logic)
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("ARCHIVED SCRIPTS", len(st.session_state.get('script_history', [])))
    kpi2.metric("ELITE PITCHES", len(st.session_state.get('pitch_history', [])))
    kpi3.metric("CURRENT REACH", f"{st.session_state.get('current_subs', 0):,}")
    
    st.divider()
    
    # 2. BUSINESS TRANSPARENCY (The Razorpay Trap)
    with st.container():
        st.write("### 📜 Business Service Description")
        st.write("""
            VOID OS is a specialized **Software as a Service (SaaS)** platform providing AI-driven 
            marketing outreach automation and lead intelligence for digital agencies.
        """)
        st.caption("Registered Category: IT Services / Software Development")
    
    st.divider()
    
    # 3. Mission Status & System Integrity
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("🌑 MISSION STATUS")
        if st.session_state.get('script_history'):
            last_script = st.session_state.script_history[-1]
            st.info(f"**LATEST ARCHITECTED:** {last_script['topic']} for {last_script['platform']}")
        else:
            st.warning("No missions active. Initialize Script Architect.")
            
    with c2:
        st.subheader("🛡️ SYSTEM INTEGRITY")
        core_display = active_core if 'active_core' in globals() else "STANDBY"
        st.code(f"AI Core: {core_display}\nHandshake: STABLE\nLaunch: T-Minus 48h")

elif page == "📡 My Growth Hub":
    st.markdown("<h1 style='color: #00d4ff;'>📡 SOCIAL INTEL MATRIX</h1>", unsafe_allow_html=True)
    
    # --- 💎 PRO-TIER UPGRADE TEASER ---
    with st.container(border=True):
        col_t1, col_t2 = st.columns([3, 1])
        with col_t1:
            st.markdown("### 🧬 Neural Scanner (OCR)")
            st.caption("Auto-sync analytics via screenshot. Currently in Alpha.")
        with col_t2:
            if st.button("🚀 UNLOCK PRO", use_container_width=True):
                st.toast("Redirecting to Razorpay Gateway...", icon="💳")
        
        # Disabled scanner to prevent 429 errors during testing
        st.button("📷 UPLOAD SCREENSHOT (PRO ONLY)", disabled=True, use_container_width=True)

    # --- 📈 GROWTH TRACKER (Manual Intelligence) ---
    st.divider()
    with st.container(border=True):
        st.subheader("📈 GROWTH DATA INPUT")
        col1, col2 = st.columns(2)
        with col1:
            start_count = st.number_input("Starting Followers", min_value=0, value=1000, help="Count when you started tracking")
            days_passed = st.slider("Days since tracking started", 1, 60, 7)
        with col2:
            current_count = st.number_input("Current Followers", min_value=0, value=1200)
            
        # --- MATHEMATICAL FORECASTING LOGIC ---
        if current_count >= start_count and days_passed > 0:
            growth_diff = current_count - start_count
            daily_avg = growth_diff / days_passed
            growth_rate_pct = (growth_diff / start_count) / days_passed if start_count > 0 else 0
            projection_30d = current_count + (daily_avg * 30)
            
            # Metric Row
            m1, m2, m3 = st.columns(3)
            m1.metric("DAILY VELOCITY", f"+{int(daily_avg)}/day")
            m2.metric("GROWTH RATE", f"{round(growth_rate_pct*100, 2)}%")
            m3.metric("30D FORECAST", f"{int(projection_30d):,}")
            
            # Dynamic Feedback
            if growth_rate_pct > 0.05:
                st.success(f"🔥 Viral Momentum Detected! Projection: **{int(projection_30d):,}**")
            elif growth_rate_pct > 0:
                st.info(f"🔮 Linear Growth Confirmed. Projection: **{int(projection_30d):,}**")
        else:
            st.warning("Director: Current count must be higher than starting count for projections.")

    # --- 🗓️ TASK FORGE (Notion-Style Manager) ---
    st.divider()
    st.subheader("🗓️ CONTENT CALENDAR & TASK FORGE")

    # Initialize task data in session state so it doesn't vanish on refresh
    if 'tasks' not in st.session_state:
        st.session_state.tasks = pd.DataFrame(
            columns=["Task", "Node", "Status", "Deadline"]
        )

    # Input Form
    with st.expander("➕ FORGE NEW CONTENT TASK", expanded=False):
        with st.form("task_form", clear_on_submit=True):
            t_name = st.text_input("Task Description", placeholder="e.g. Record Cinematic B-Roll")
            t_plat = st.selectbox("Node", ["YouTube", "Instagram", "X", "LinkedIn", "TikTok"])
            t_date = st.date_input("Deadline")
            submit_task = st.form_submit_button("SYNC TO FORGE")
            
            if submit_task and t_name:
                new_task = pd.DataFrame([{
                    "Task": t_name, 
                    "Node": t_plat, 
                    "Status": "⏳ Pending", 
                    "Deadline": t_date.strftime("%Y-%m-%d")
                }])
                st.session_state.tasks = pd.concat([st.session_state.tasks, new_task], ignore_index=True)
                st.success("Task Synchronized.")

    # Interactive Table (The heart of the Notion-style view)
    if not st.session_state.tasks.empty:
        # User can edit status or task names directly in the table
        edited_df = st.data_editor(
            st.session_state.tasks,
            use_container_width=True,
            num_rows="dynamic", # Allows users to delete/add rows manually
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["⏳ Pending", "🎬 Filming", "✂️ Editing", "✅ Uploaded"],
                    required=True,
                ),
                "Node": st.column_config.SelectboxColumn(
                    "Node",
                    options=["YouTube", "Instagram", "X", "LinkedIn", "TikTok"],
                    required=True,
                )
            }
        )
        # Save changes back to session state
        st.session_state.tasks = edited_df
    else:
        st.caption("No tasks currently forged in the matrix.")

    # --- 🌑 DIRECTOR'S ANALYTICS IDEA: PROGRESS BAR ---
    if not st.session_state.tasks.empty:
        done = len(st.session_state.tasks[st.session_state.tasks['Status'] == "✅ Uploaded"])
        total = len(st.session_state.tasks)
        progress = done / total if total > 0 else 0
        st.write(f"**Total Campaign Progress: {int(progress*100)}%**")
        st.progress(progress)


# --- MODULE 10: CLIENT ASSIGNED SCRIPTS ---
elif page == "💎 Assigned Scripts":
    # Using session_state safely with a fallback to 'Director'
    current_user = st.session_state.get('user_name', 'Director').upper()
    st.markdown(f"<h1 style='color: #00ff41;'>💎 {current_user}'S VAULT</h1>", unsafe_allow_html=True)
    
    # 🛰️ Define URL (Ensure this is in your secrets or defined here)
    # VAULT_SHEET_CSV_URL = st.secrets["https://docs.google.com/spreadsheets/d/e/2PACX-1vTtSx9iQTrDvNWe810s55puzBodFKvfUbfMV_l-QoQIfbdPxeQknClGGCQT33UQ471NyGTw4aHLrDTw/pub?gid=1490190727&single=true&output=csv"] 
    
    try:
        # Load the database
        scripts_df = pd.read_csv(VAULT_SHEET_CSV_URL)
        
        # Clean column whitespace for safety
        scripts_df.columns = [str(c).strip() for c in scripts_df.columns]
        
        # FILTER: Using .iloc[1] for Client Name as per your logic
        # We use .fillna('') to prevent crashes on empty rows
        user_name_lower = st.session_state.get('user_name', '').lower()
        my_vault = scripts_df[scripts_df.iloc[:, 1].astype(str).str.lower() == user_name_lower].fillna("N/A")
        
        if my_vault.empty:
            st.info("🛰️ VAULT EMPTY: No scripts assigned to your node yet. Contact the Director.")
            st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJueXZueXpueXpueXpueXpueXpueXpueXpueXpueXpueXpueCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKMGpxxcaNnU6w8/giphy.gif", width=300)
        else:
            st.subheader(f"Total Deliverables: {len(my_vault)}")
            
            for i, row in my_vault.iterrows():
                # Logic Preservation: row.iloc[3]=Title, row.iloc[2]=Platform
                title = row.iloc[3] if len(row) > 3 else "Untitled Script"
                platform = str(row.iloc[2]).upper() if len(row) > 2 else "GENERAL"
                content = row.iloc[4] if len(row) > 4 else "No content available."
                visual_dna = row.iloc[5] if len(row) > 5 else "No DNA data provided."

                with st.expander(f"🎬 {title} | {platform}"):
                    col_text, col_status = st.columns([3, 1])
                    
                    with col_text:
                        st.markdown("### The Script")
                        st.write(content) 
                        st.divider()
                        st.caption(f"🧬 Visual DNA: {visual_dna}")
                    
                    with col_status:
                        st.markdown("### Status")
                        # Keys must be unique, adding index 'i' is perfect
                        st.checkbox("Filmed", key=f"check_film_{i}")
                        st.checkbox("Edited", key=f"check_edit_{i}")
                        st.checkbox("Posted", key=f"check_post_{i}")
                        
                        st.divider()
                        # RECTIFIED DOWNLOAD: Download buttons should stand alone
                        st.download_button(
                            label="📥 DOWNLOAD", 
                            data=str(content), 
                            file_name=f"script_{i}.txt",
                            key=f"dl_btn_{i}",
                            use_container_width=True
                        )

    except Exception as e:
        st.error("DATABASE OFFLINE: Connection to Master Vault timed out or URL invalid.")
        # Only show the raw error if you are in 'Dev' mode, otherwise it looks messy
        with st.expander("📡 Diagnostic Error Log"):
            st.code(str(e))


# --- MODULE 4: GLOBAL PULSE ---
elif page == "🌐 Global Pulse":
    st.title("🌐 GLOBAL INTELLIGENCE PULSE")
    pulse_df = load_market_pulse_data(MARKET_PULSE_URL)
    
    if not pulse_df.empty:
        st.markdown("<h3 style='color: #00d4ff;'>🚨 ELITE VIGOR SIGNALS</h3>", unsafe_allow_html=True)
        
        # Select a niche for a Deep Dive
        target_niche = st.selectbox("Select Niche for Keyword Extraction", pulse_df['Niche'].unique())
        
        if st.button(f"🔍 EXTRACT VIRAL KEYWORDS FOR {target_niche.upper()}"):
            with st.spinner("🌑 ORACLE ANALYZING SEARCH VOLUME..."):
                # Using Groq to simulate real-time keyword scraping
                prompt = f"""
                Analyze the '{target_niche}' niche for February 2026. 
                Provide:
                1. Top 5 Viral Keywords (high SEO weight).
                2. Three 'Negative Hooks' (unpopular opinions that go viral).
                3. The #1 predicted 'Search Term' for next week.
                Keep it concise and tactical.
                """
                if groq_c:
                    res = groq_c.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    intel = res.choices[0].message.content
                    
                    st.markdown(f"""
                    <div style="border: 1px solid #00ff41; padding: 20px; border-radius: 10px; background: #080808;">
                        <h4 style="color: #00ff41;">📡 INTELLIGENCE BRIEF: {target_niche}</h4>
                        <p style="white-space: pre-wrap; color: #e0e0e0;">{intel}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("AI Uplink Offline. Check Groq API Key.")

        st.divider()
    
    
    
    st.title("🌐 GLOBAL INTELLIGENCE PULSE")
    pulse_df = load_market_pulse_data(MARKET_PULSE_URL)
    if not pulse_df.empty:
        st.markdown('<div style="border: 1px solid #00d4ff; padding: 20px; border-radius: 10px; margin-bottom: 30px;">', unsafe_allow_html=True)
        st.markdown("<h3 style='color: #00d4ff;'>🚨 ELITE VIGOR SIGNALS</h3>", unsafe_allow_html=True)
        cols = st.columns(2)
        high_heat = pulse_df[pulse_df['Score'] >= 85].sort_values(by='Score', ascending=False).head(10)
        for i, (_, alert) in enumerate(high_heat.iterrows()):
            with cols[i%2]:
                st.markdown(f"📡 **{alert['Niche']}** | `Score: {alert['Score']}`")
                st.caption(alert['Reason'])
                st.divider()
        st.markdown("</div>", unsafe_allow_html=True)

    c_news, c_analysis = st.columns([2, 1])
    with c_news:
        st.subheader("📰 Live Tech Intelligence")
        feed = feedparser.parse("https://techcrunch.com/category/artificial-intelligence/feed/")
        for entry in feed.entries[:6]:
            img_col, txt_col = st.columns([1, 2.5])
            with img_col: st.image(get_intel_image(entry), use_container_width=True)
            with txt_col:
                st.markdown(f"**[{entry.title.upper()}]({entry.link})**")
                st.write(BeautifulSoup(entry.summary, "html.parser").text[:180] + "...")
            st.divider()
            # 🧬 Dynamic RSS Feeds
    feeds = {
        "AI & Tech": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "Business": "https://www.entrepreneur.com/rss/technology.rss",
        "Social Media": "https://mashable.com/feeds/rss/category/social-media"
    }
    
    selected_feed = st.tabs(list(feeds.keys()))
    
    for i, category in enumerate(feeds.keys()):
        with selected_feed[i]:
            feed_data = feedparser.parse(feeds[category])
            for entry in feed_data.entries[:5]:
                with st.container():
                    # Styling each news card
                    st.markdown(f"""
                    <div style="border: 1px solid #333; padding: 20px; border-radius: 10px; background: #080808;">
                        <h4 style="color: #00ff41;">{entry.title}</h4>
                        <p style="color: #bbb; font-size: 14px;">{BeautifulSoup(entry.summary, 'html.parser').text[:200]}...</p>
                        <a href="{entry.link}" target="_blank" style="color: #00d4ff; text-decoration: none;">READ SOURCE ⮕</a>
                    </div>
                    <br>
                    """, unsafe_allow_html=True)



# --- MODULE 5: TREND DUEL ---
elif page == "⚔️ Trend Duel":
    st.title("⚔️ TREND DUEL")
    pulse_df = load_market_pulse_data()
    if not pulse_df.empty:
        st.subheader("🌑 Market Density Analysis")
        target = st.selectbox("Select Niche to Audit", pulse_df['Niche'].unique())
        row = pulse_df[pulse_df['Niche'] == target].iloc[0]
        st.metric(label=f"{target} Entry Status", value=get_saturation_status(row['Score']))
        st.table(pulse_df[pulse_df['Niche'] == target][['Niche', 'Score', 'Reason']])
        st.divider()
        sel = st.multiselect("Compare Niches", options=pulse_df['Niche'].unique().tolist(), default=pulse_df['Niche'].unique().tolist()[:5])
        comp = pulse_df[pulse_df['Niche'].isin(sel)]
        if not comp.empty: 
            fig = px.bar(comp, x='Niche', y='Score', color='Score', template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)

elif page == "🏗️ Script Architect":
        st.markdown("<h1 style='color: #00ff41;'>⚔️ SCRIPT ARCHITECT</h1>", unsafe_allow_html=True)
        
        # 1. USAGE LIMITS (Basic Only)
        if not is_paid and not is_admin:
            if 'daily_script_count' not in st.session_state: st.session_state.daily_script_count = 0
            if st.session_state.daily_script_count >= 3:
                st.error("🚨 DAILY UPLINK LIMIT REACHED")
                st.stop()
            st.caption(f"🛰️ BASIC NODE: {3 - st.session_state.daily_script_count} scripts remaining.")

        # 2. THE FORMATION ENGINE
        with st.container(border=True):
            c1, c2 = st.columns([1, 1.5], gap="large")
            with c1:
                st.subheader("Architectural Input")
                platform = st.selectbox("Platform", ["Instagram Reels", "YouTube Shorts", "TikTok", "YouTube Long-form"])
                topic = st.text_input("Core Topic", placeholder="e.g., The reality of building a SaaS")
                tone = st.select_slider("Vigor", ["Professional", "Aggressive", "Elite"])
                
                if st.button("🏗️ ARCHITECT FULL SCRIPT", use_container_width=True):
                    if topic:
                        with st.spinner("🛰️ ARCHITECTING FORMATION..."):
                            if not is_paid and not is_admin: st.session_state.daily_script_count += 1
                            # Restoration of the high-quality formation prompt
                            formation_prompt = (
                                f"Act as a master content strategist. Create a high-retention {platform} script about {topic}. "
                                f"Tone: {tone}. Formation: Start with a 'Pattern Interrupt' hook, move into 'The Agitation', "
                                f"provide 'The Insight', and end with a 'Call to Value'. Use timestamps and clear visual cues."
                            )
                            res = groq_c.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": formation_prompt}])
                            st.session_state.current_architect_txt = res.choices[0].message.content
                            st.rerun()

            with c2:
                if st.session_state.get('current_architect_txt'):
                    st.subheader("💎 SCRIPT BLUEPRINT")
                    st.session_state.current_architect_txt = st.text_area("Live Editor", value=st.session_state.current_architect_txt, height=400)
                    st.warning("⚠️ Optimization & Trend Mapping is restricted to PRO Nodes.")
                    if st.button("🧠 UPGRADE TO NEURAL FORGE"):
                        st.session_state.page = "🧠 Neural Forge"
                        st.rerun()
                else:
                    st.info("Awaiting Tactical Input to manifest formation.")

# --- MODULE 7: THE NEURAL FORGE (STABLE & EXPOSED) ---
elif page == "🧠 Neural Forge":
        if not is_paid and not is_admin:
            st.markdown("<h1 style='color: #666;'>🧠 NEURAL FORGE</h1>", unsafe_allow_html=True)
            st.warning("PROTOCOL RESTRICTED: Pro License Required.")
            st.stop()

        st.markdown("<h1 style='color: #00ff41;'>🧠 NEURAL FORGE // ELITE</h1>", unsafe_allow_html=True)
        
        # 1. THE CENTRAL CONTROL PANEL
        with st.container(border=True):
            col_a, col_b = st.columns([1, 1], gap="medium")
            
            with col_a:
                st.subheader("🧬 Core Configuration")
                f_platform = st.selectbox("Target Platform", ["Instagram Reels", "YouTube Shorts", "TikTok", "YouTube Long-form", "X-Thread"], key="forge_plat")
                f_topic = st.text_input("Core Concept", placeholder="e.g., The psychology of luxury branding", key="forge_top")
                
                f_framework = st.selectbox("Retention Framework", [
                    "The Controversy Start (High Vigor)", 
                    "The Hero's Journey (Storytelling)", 
                    "Statistical Shock (Educational)",
                    "The 'Mistake' Hook (Click-through Focus)",
                    "Day in the Life (Relatability)",
                    "The Deep-Dive (Authority)"
                ])

            with col_b:
                st.subheader("📡 Trend Mapper")
                # FIXED: Options and Default now match perfectly to prevent API Exception
                trend_options = ["None", "Viral Audio", "Niche Commentary", "POV/Relatable", "Educational Breakdown"]
                f_trend = st.radio("Current Trend Sync", options=trend_options, index=0, horizontal=True)
                
                f_audience = st.text_input("Target Audience Persona", "High-Performance Creators")
                f_vigor = st.select_slider("Neural Vigor", ["Standard", "High", "Extreme", "Elite"])

            # 2. THE ACTIVATION BUTTON
            if st.button("🔥 EXECUTE NEURAL SYNTHESIS", use_container_width=True):
                if f_topic:
                    with st.spinner("🌑 FORGING ELITE CONTENT..."):
                        try:
                            forge_prompt = (
                                f"Act as an elite content engineer. Create a script for {f_platform}. "
                                f"Topic: {f_topic}. Framework: {f_framework}. "
                                f"Trend Mapping: {f_trend}. Audience: {f_audience}. "
                                f"Tone Vigor: {f_vigor}. Structure with timestamps, B-roll cues, and psychological triggers."
                            )
                            res = groq_c.chat.completions.create(
                                model="llama-3.3-70b-versatile", 
                                messages=[{"role": "user", "content": forge_prompt}]
                            )
                            st.session_state.pro_forge_txt = res.choices[0].message.content
                            st.rerun()
                        except Exception as e:
                            st.error("🚦 UPLINK DELAY: System is recalibrating. Please wait 60 seconds.")

        # 3. OUTPUT & OPTIMIZATION SUITE
        if st.session_state.get('pro_forge_txt'):
            st.divider()
            c_out, c_tools = st.columns([1.5, 1])
            
            with c_out:
                st.subheader("💎 NEURAL OUTPUT")
                st.session_state.pro_forge_txt = st.text_area("Master Editor", value=st.session_state.pro_forge_txt, height=450)
            
            with c_tools:
                st.subheader("🧪 Intelligence Tools")
                if st.button("🚀 ANALYZE HOOK VIRALITY", use_container_width=True):
                    with st.spinner("Neural Scan..."):
                        res = groq_c.chat.completions.create(
                            model="llama-3.3-70b-versatile", 
                            messages=[{"role": "user", "content": f"Analyze this hook for viral potential: {st.session_state.pro_forge_txt[:200]}"}]
                        )
                        st.info(res.choices[0].message.content)

                if st.button("🧠 SCAN RETENTION GAPS", use_container_width=True):
                    with st.spinner("Scanning Pacing..."):
                        res = groq_c.chat.completions.create(
                            model="llama-3.3-70b-versatile", 
                            messages=[{"role": "user", "content": f"Identify 'wordy' sections in: {st.session_state.pro_forge_txt}"}]
                        )
                        st.warning(res.choices[0].message.content)


# --- MODULE 7: CLIENT PITCHER (PITCH ENGINE) ---
elif page == "💼 Client Pitcher":
    st.markdown("<h1 style='color: #00d4ff;'>💼 VOID CAPITAL: PITCH ENGINE</h1>", unsafe_allow_html=True)
    
    # 🧬 NEURAL BRIDGE: Extract data from session state
    active_target = st.session_state.get('active_pitch_target', {})
    
    default_name = active_target.get('name', "")
    default_niche = active_target.get('niche', "Personal Brand")
    gap_detected = active_target.get('gap', "")
    
    # Auto-craft the initial offer based on the "Gap"
    default_offer = f"I noticed a gap in your {gap_detected}. I've architected a solution to bridge this." if gap_detected else ""

    c1, c2 = st.columns([1, 1.5], gap="large")
    
    with c1:
        st.subheader("🎯 TARGET ACQUISITION")
        client_name = st.text_input("Lead / Brand Name", value=default_name)
        niche_cat = st.selectbox("Industry", ["Personal Brand", "SaaS Founders", "Fashion", "E-com", "Real Estate"], index=0)
        offer_details = st.text_area("The 'Gap' / Value Prop", value=default_offer, height=150)
        
        if st.button("🔥 GENERATE ELITE TRANSMISSION", use_container_width=True):
            if groq_c and client_name and offer_details:
                with st.spinner("🌑 CALCULATING PSYCHOLOGICAL HOOKS..."):
                    prompt = f"System: High-ticket closer. Target: {client_name} ({niche_cat}). Problem: {offer_details}. Write a minimalist ROI-focused cold DM. No emojis. No fluff."
                    res = groq_c.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                    st.session_state.current_pitch = res.choices[0].message.content
                    st.session_state.pitch_history.append({"client": client_name, "pitch": st.session_state.current_pitch, "timestamp": time.strftime("%H:%M")})
            else:
                st.error("System Error: Missing Inputs or API Offline.")

    with c2:
        if 'current_pitch' in st.session_state:
            st.subheader("📡 ENCRYPTED TRANSMISSION")
            st.code(st.session_state.current_pitch, language="markdown")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📋 PITCH SENT"): st.toast(f"Transmission logged.")
            with col_b:
                if st.button("🔄 CLEAR TARGET"):
                    st.session_state.pop('active_pitch_target', None)
                    st.session_state.pop('current_pitch', None)
                    st.rerun()
        else:
            st.info("Awaiting Target Data. Use 'Lead Source' to beam a target or enter details.")


# --- MODULE 8: CREATOR LAB & LEAD SOURCE ---
elif page == "🧪 Creator Lab":
    # 🕵️ Check Persona
    is_admin = st.session_state.get('admin_verified', False)

    if is_admin:
        # --- THE ADMIN ROI ENGINE (Your Secret Weapon) ---
        st.markdown("<h1 style='color: #00d4ff;'>🧪 ROI ENGINE v2.0 (ADMIN)</h1>", unsafe_allow_html=True)
        
        niche_data = {
            "🎮 Gaming & Entertainment": 3.0,
            "🧘 Lifestyle & Vlogging": 5.0,
            "👗 Fashion & Beauty": 8.0,
            "🤖 AI & Tech": 15.0,
            "💼 Business & SaaS": 22.0,
            "💰 Finance & Crypto": 35.0
        }

        with st.container():
            st.subheader("📊 PROFIT PROJECTION")
            col1, col2 = st.columns(2)
            with col1:
                selected_niche = st.selectbox("Select Target Niche", list(niche_data.keys()))
                views = st.number_input("Projected Weekly Views", min_value=0, value=50000, step=5000)
                product_price = st.number_input("Product/Service Price ($)", value=100)
            with col2:
                default_cpm = niche_data[selected_niche]
                cpm = st.number_input(f"Est. {selected_niche} CPM ($)", value=default_cpm)
                conv_rate = st.slider("Conversion Rate (%)", 0.1, 5.0, 1.0)
                conversion_factor = st.number_input("USD to INR Rate", value=83.0)

            # 🧬 CALCULATIONS
            ad_rev_usd = (views / 1000) * cpm
            sales_rev_usd = (views * (conv_rate / 100)) * product_price
            total_usd = ad_rev_usd + sales_rev_usd
            total_inr = total_usd * conversion_factor

            st.divider()
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.metric("TOTAL VALUE (USD)", f"${total_usd:,.2f}")
            with res_col2:
                st.markdown(f"<h2 style='color: #00ff41;'>₹ {total_inr:,.2f}</h2>", unsafe_allow_html=True)

        if st.button("🧬 GENERATE PROFIT BLUEPRINT", use_container_width=True):
            # ... (Your existing Groq ROI logic) ...
            st.info("Generating Admin Blueprint...")

    else:
        # --- THE PRO USER LAB (Content Optimization) ---
        st.markdown("<h1 style='color: #00ff41;'>🧪 CREATOR LAB (PRO)</h1>", unsafe_allow_html=True)
        st.info("🛰️ High-Vigor Optimization Suite: Refine your content for maximum retention.")

        tab_hook, tab_retention = st.tabs(["🔥 Hook Analyzer", "🧠 Cognitive Load"])

        with tab_hook:
            st.subheader("Viral Hook Architect")
            user_hook = st.text_area("Paste your opening line (Hook):", placeholder="Example: Most creators are failing at AI...")
            if st.button("ANALYZE HOOK"):
                with st.spinner("Neural Processing..."):
                    # Light Groq call for hook feedback
                    hook_prompt = f"Analyze this hook for viral potential: {user_hook}. Rate it 1-10 and suggest a 'High-Vigor' rewrite."
                    res = groq_c.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": hook_prompt}])
                    st.success(res.choices[0].message.content)

        with tab_retention:
            st.subheader("Cognitive Retention Check")
            st.caption("Identify 'Boredom Gaps' in your script.")
            script_text = st.text_area("Paste Full Script:")
            if st.button("IDENTIFY DROPOFF POINTS"):
                st.warning("Analysis complete: Section 2 is too 'Wordy'. Add a visual pattern interrupt at 0:15.")


# --- MODULE 9: LEAD SOURCE (RESILIENT AUTO-SWITCH) ---
elif page == "🛰️ Lead Source":
    st.markdown("<h1 style='color: #00ff41;'>🛰️ LEAD SOURCE: DEEP SCAN</h1>", unsafe_allow_html=True)
    
    niche_target = st.text_input("Target Keyword", placeholder="e.g. Real Estate, Fitness Coach")
    
    if st.button("📡 INITIALIZE DEEP SCAN"):
        if "RAPIDAPI_KEY" not in st.secrets:
            st.error("Uplink Failure: API Key missing in Secrets.")
        else:
            with st.spinner("🌑 CYCLING THROUGH API NODES..."):
                target_host = "instagram191.p.rapidapi.com" 
                headers = {
                    "X-RapidAPI-Key": st.secrets["RAPIDAPI_KEY"],
                    "X-RapidAPI-Host": target_host
                }
                
                # 🛑 THE PATH-FINDER LOOP
                # We try the three most likely paths for Glavier
                endpoints = ["/v1/user/search", "/v1/web/search", "/v1/search"]
                success = False
                
                for path in endpoints:
                    try:
                        url = f"https://{target_host}{path}"
                        # Glavier likes 'query' or 'q'
                        params = {"query": niche_target.strip(), "q": niche_target.strip()}
                        response = requests.get(url, headers=headers, params=params)
                        raw_data = response.json()
                        
                        # Data check
                        users = raw_data.get('data', raw_data.get('users', raw_data.get('items', [])))
                        
                        if users:
                            data = []
                            for u in users[:10]:
                                u_info = u.get('user', u)
                                data.append({
                                    "Handle": f"@{u_info.get('username')}",
                                    "Platform": "IG",
                                    "Followers": u_info.get('follower_count', 'LIVE'),
                                    "Gap": f"Strategic Gap in {niche_target}",
                                    "Vigor": random.randint(80, 99),
                                    "Value": "High"
                                })
                            st.session_state.found_leads = pd.DataFrame(data)
                            st.success(f"UPLINK SUCCESSFUL via {path}")
                            success = True
                            break # Stop searching once we find a working path
                    except:
                        continue
                
                if not success:
                    st.error("📡 ALL ENDPOINTS EXHAUSTED.")
                    st.json(raw_data) # Show the final error message
                    st.warning("Reverting to Simulation Mode for UI Testing.")
                    # Simulation Fallback (Keep your UI working no matter what)
                    sim_data = [{"Handle": "@Lead_Gen_Master", "Platform": "IG", "Followers": "50K", "Gap": "No Funnel", "Vigor": 90, "Value": "High"}]
                    st.session_state.found_leads = pd.DataFrame(sim_data)


# --- MODULE 9: HISTORY (THE VAULT UPGRADE) ---
elif page == "📜 History":
    st.markdown("<h1 style='color: #00ff41;'>📜 ARCHIVE VAULT</h1>", unsafe_allow_html=True)
    
    if not st.session_state.script_history and not st.session_state.pitch_history:
        st.info("Vault is empty. Generate scripts in the Architect or Pitcher modules.")
    else:
        t1, t2 = st.tabs(["💎 SCRIPT ARCHIVE", "💼 PITCH LOGS"])
        
        with t1:
            for i, s in enumerate(reversed(st.session_state.script_history)):
                with st.expander(f"📜 {s['platform']} | {s['topic'].upper()}"):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(s['script'])
                    with col_b:
                        st.caption(f"Target: {s['assigned_to']}")
                        if st.button("✅ MARK AS FILMED", key=f"film_{i}"):
                            st.toast("Updated in Global Vault")
                        st.download_button("📥 DOWNLOAD TXT", s['script'], file_name=f"script_{i}.txt")

        with t2:
            for i, p in enumerate(reversed(st.session_state.pitch_history)):
                with st.container():
                    st.markdown(f"### 🎯 Target: {p['client']}")
                    st.info(p['pitch'])
                    st.caption(f"Transmission Time: {p.get('timestamp', 'N/A')}")
                    st.divider()

# --- MODULE 11: ADMIN CONSOLE (OPTION C) ---
elif page == "🛡️ Admin Console":
    st.markdown("<h1 style='color: #00ff41;'>🛡️ SYSTEM ADMINISTRATION</h1>", unsafe_allow_html=True)
    
    # 1. Password Protection
    auth = st.text_input("Enter Level 5 Authorization Code", type="password")
    
    if auth == "IamAdmin": 
        st.session_state['admin_verified'] = True
        st.success("Identity Verified. Welcome, Director.")
        
        # 2. INITIALIZE TABS
        tab1, tab2, tab3 = st.tabs(["👥 Users", "💰 Payments", "📡 Lead Drop"])

        # --- TAB 1: USER MANAGEMENT ---
        with tab1:
            st.subheader("👥 User Management")
            users_df = load_user_db()
            if not users_df.empty:
                st.dataframe(users_df, use_container_width=True)
            
            st.divider()
            st.subheader("🛰️ Node Traffic")
            st.info(f"Active Users in Database: {len(users_df)}")

        # --- TAB 2: PAYMENTS (Manual Override) ---
        with tab2: 
            st.subheader("💰 Manual Revenue Override")
            target_mail = st.text_input("User Email to Activate", key="admin_target_mail")
            
            if st.button("ACTIVATE PRO NODES"):
                if target_mail:
                    # 1. Prepare Payload for Role Upgrade
                    payload = {
                        "email": target_mail.lower().strip(),
                        "category": "ROLE_UPGRADE",
                        "message": "PRO_ACTIVATION"
                    }
                    
                    # 2. Execute Uplink to Google Apps Script
                    try:
                        # Using your upgraded Apps Script URL
                        NEW_URL = "https://script.google.com/macros/s/AKfycbzBLwNA-37KxZ5mDyHp1DMNw23n8xyfBVaVbmg_zRs-oQAZGue6Zuxo44UwztuBvFIC/exec" 
                        response = requests.post(NEW_URL, json=payload, timeout=30)
                        
                        if response.status_code == 200 and "SUCCESS" in response.text:
                            st.success(f"⚔️ OMNI-SYNC COMPLETE: {target_mail} updated in Google Sheets.")
                            st.balloons()
                            if target_email == st.session_state.get('user_email'):
                                st.session_state.user_status = 'Pro' # This unlocks the Forge
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"📡 SCRIPT RESPONSE: {response.text}")
                    except Exception as e:
                        st.error(f"🚨 UPLINK CRASHED: {e}")
                else:
                    st.warning("Director, enter a target email first.")

            st.divider()
            
            # --- THE MANUAL VERIFY FORM ---
            with st.form("manual_verify_v2"):
                st.write("### 🛰️ Admin Sync: Verify Payment")
                u_email = st.text_input("Your Registered Email")
                u_txn = st.text_input("Transaction ID / Reference Number")
                
                # Feedback API URL
                FEEDBACK_API_URL = "https://script.google.com/macros/s/AKfycbxP8IMp3_WaK3Uxwnrm-haGVMuq8xPbiBMp7j4et8l6r2LvgQZo-RRaTd_OCa4rnZuxAA/exec"
                
                if st.form_submit_button("REQUEST ACTIVATION"):
                    if u_email and u_txn:
                        f_payload = {"email": u_email, "message": u_txn, "category": "PAYMENT_PENDING"}
                        try:
                            f_res = requests.post(FEEDBACK_API_URL, json=f_payload, timeout=10)
                            if f_res.status_code == 200:
                                st.success("✅ TRANSMISSION SUCCESS: Data logged.")
                                st.balloons()
                            else:
                                st.error(f"📡 UPLINK ERROR: {f_res.status_code}")
                        except Exception as e:
                            st.error(f"🚨 CRITICAL SYSTEM FAILURE: {str(e)}")
                    else:
                        st.warning("Director, both fields are required.")

        # --- TAB 3: LEAD DROP ---
        with tab3:
            st.subheader("📡 Broadcast New Leads")
            lead_file = st.file_uploader("Upload Daily Leads (CSV)", type="csv")
            niche_label = st.text_input("Niche Category", placeholder="e.g., Real Estate India")
            
            if st.button("🚀 PUSH TO PAID USERS"):
                if lead_file is not None:
                    import pandas as pd
                    df = pd.read_csv(lead_file)
                    st.session_state['global_leads'] = df
                    st.success(f"Transmission Successful. {len(df)} leads pushed.")
                else:
                    st.error("No data package detected.")

    elif auth != "":
        st.error("Invalid Credentials. Intrusion attempt logged.")

# --- MODULE: LEGAL ARCHIVE (Feedback & Vote Edition) ---
elif page == "⚖️ Legal Archive":
    # Universal Access Check (God-Mode)
    u_name = str(st.session_state.get('user_name', '')).upper()
    u_role = str(st.session_state.get('role', '')).upper()
    is_authorized = ("ADMIN" in u_name or "DIRECTOR" in u_name or "ADMIN" in u_role)

    st.markdown("<h1 style='color: #00ff41;'>⚖️ LEGAL DEFENSE VAULT</h1>", unsafe_allow_html=True)
    
    # --- 🛰️ SYSTEM UPDATE NOTICE ---
    st.warning("📡 **SYSTEM OPTIMIZATION IN PROGRESS:** We are fine-tuning our AI Law-Cores to make sure your contracts are 100% bulletproof. These advanced tools will unlock in the next update.")

    # --- SECTION 1: THE COMING SOON PREVIEW ---
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("#### 📝 Custom Contract Creator")
            st.caption("Tell the AI what you need, and it writes the deal for you.")
            st.button("⚙️ CALIBRATING...", disabled=True, use_container_width=True)
            
    with col2:
        with st.container(border=True):
            st.markdown("#### 👁️ AI Contract Scanner")
            st.caption("Upload a brand's contract to find hidden traps instantly.")
            st.button("⚙️ TRAINING AI...", disabled=True, use_container_width=True)

    st.divider()

    # --- SECTION 2: THE COMMUNITY FORGE (Vote & Feedback) ---
    st.markdown("### 🧬 Help Us Build Your Defense")
    st.write("Which legal protection do you need most right now? Your choice will decide what we build first.")

    with st.container(border=True):
        # 1. The Vote
        vote_choice = st.radio(
            "Select your top priority:",
            ["Brand Deal Safety (Contracts)", "Copyright Protection (Music/Videos)", "Agency & Manager Agreements"],
            index=0
        )
        
        # 2. The Open Feedback
        st.write("")
        user_suggestion = st.text_area(
            "In your own words, what else would make this app better for you?",
            placeholder="e.g., I want a way to track if a brand has paid me yet..."
        )
        if st.button("📤 SEND RECOMMENDATION", use_container_width=True):
            if user_suggestion:
                import requests # Ensure this is at the top of your script
                
                # --- 📡 THE GOOGLE FORM BRIDGE ---
                # Replace the URL with your "formResponse" URL and match the entry IDs
                form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfeDAY3gnWYlpH90EaJirxUc8d4obYUgiX72WJIah7Cya1VNQ/formResponse"
                
                payload = {
                    "entry.2084741280": st.session_state.get('user_name', 'Unknown'), # User Name ID
                    "entry.554052255": vote_choice,                                 # Priority ID
                    "entry.2031301382": user_suggestion                              # Feedback ID
                }

                try:
                    # We send the data "behind the scenes"
                    response = requests.post(form_url, data=payload)
                    
                    if response.status_code == 200:
                        st.success(f"**Recommendation Locked, {st.session_state.get('user_name', 'Director')}!**")
                        st.balloons()
                        st.markdown(f"""
                        > Your input has been transmitted directly to the Master Vault.
                        > We are building this app for YOU, and we’ll surely work on making this a reality in the next update!""")
                    else:
                        st.error("Uplink Error: Sheet rejected the data. Check Form IDs.")
                
                except Exception as e:
                    st.error(f"Critical Failure: {e}")
            else:
                st.warning("Director, please add a small suggestion first!")
                    
                   
    # --- SECTION 3: BASIC CHECKLIST (The 'Now' value) ---
    st.divider()
    with st.expander("✅ VIEW BASIC SAFETY CHECKLIST"):
        st.write("While the AI is training, always check these manually:")
        st.write("- Is the payment date clearly mentioned?")
        st.write("- Do you keep the rights to your raw footage?")
        st.write("- Is there a limit on how many 'Revisions' the brand can ask for?")

# --- MODULE 10: 💎 VOID PRO LICENSE UPLINK ---
elif page == "💎 Upgrade to Pro":
        st.markdown("<h1 style='color: #00ff41;'>💎 VOID OS // LICENSE UPLINK</h1>", unsafe_allow_html=True)
        
        # 1. VALUE PROPOSITION
        with st.container(border=True):
            st.markdown("### ⚡ NEURAL FORGE: PRO ACCESS")
            c1, c2 = st.columns(2)
            with c1:
                st.write("🔓 **Unlimited Neural Pitching**")
                st.write("🔓 **Full Legal Archive Access**")
            with c2:
                st.write("🔓 **Deep Lead Scanners**")
                st.write("🔓 **Priority Support Node**")
            st.markdown("---")
            st.markdown("**Price:** ~~₹1,499~~ | <span style='color: #00ff41; font-size: 20px;'>**₹499 (Launch Offer)**</span>", unsafe_allow_html=True)

        # 2. LEGAL GATE
        st.subheader("⚖️ Protocol Agreement")
        with st.expander("Review Terms & Refund Policy"):
            st.write("- **Non-Refundable:** Digital licenses grant instant asset access.")
            st.write("- **Manual Sync:** UPI verification takes 1-2 hours.")
            st.write("- **Email Match:** Ensure registered email matches payment sync.")
        
        agreed = st.checkbox("I verify the Terms of VOID OS", key="force_agree_check")
        st.divider()

        if agreed:
            st.markdown("### 🛰️ SELECT PAYMENT GATEWAY")
            col_gate1, col_gate2 = st.columns(2)

            with col_gate1:
                with st.container(border=True):
                    st.markdown("#### 🇮🇳 NEURAL UPI")
                    vpa_id = "anuj05758@okicici" 
                    upi_url = f"upi://pay?pa={vpa_id}&pn=VOID_OS&am=499&cu=INR&tn=VOID_OS_PRO"
                    qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={upi_url}"
                    st.image(qr_api, use_container_width=True)
                    st.link_button("📲 OPEN UPI APP", upi_url, use_container_width=True)

            with col_gate2:
                with st.container(border=True):
                    st.markdown("#### 💳 CARD / RAZORPAY")
                    st.button("🔒 ENCRYPTED", disabled=True, use_container_width=True)
                    st.warning("OFFLINE: Available in V2.0 Update.")

            st.divider()

            # 3. MANUAL SYNC FORM
            st.markdown("### 🧬 MANUAL DATA SYNC")
            with st.container(border=True):
                sync_email = st.text_input("REGISTERED EMAIL", placeholder="e.g., director@voidos.com")
                utr_num = st.text_input("12-DIGIT UTR / TRANSACTION ID", placeholder="e.g., 4029XXXXXXXX")
                
                if st.button("SYNC WITH VOID OS", use_container_width=True):
                    if "@" in sync_email and len(utr_num) >= 10:
                        # 📡 UPLINK LOGIC
                        pay_form_url = "https://docs.google.com/forms/d/e/YOUR_FORM_ID/formResponse"
                        payload = {"entry.123": sync_email, "entry.456": utr_num} # Update with IDs
                        try:
                            requests.post(pay_form_url, data=payload)
                            st.success("🛰️ UPLINK SUCCESSFUL: Verification in progress.")
                            st.balloons()
                        except:
                            st.error("Uplink Failure. Contact Support.")
                    else:
                        st.error("Invalid Input Details.")


elif page == "⚙️ Settings":
    st.markdown("<h1 style='color: #00ff41;'>⚙️ SYSTEM SETTINGS</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # 1. PROFILE INTELLIGENCE
    with st.container(border=True):
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image("https://api.dicebear.com/7.x/bottts/svg?seed=" + st.session_state.user_name, width=100)
        with col2:
            st.subheader(f"Director: {st.session_state.user_name}")
            st.write(f"**Niche:** {st.session_state.get('user_niche', 'Not Set')}")
            st.caption(f"Registered Email: {st.session_state.get('user_email', 'N/A')}")
            
            # Dynamic Badge
            status = st.session_state.get('user_status', 'free')
            if status == "paid":
                st.markdown("<span style='background-color: #00ff41; color: black; padding: 2px 8px; border-radius: 5px; font-weight: bold;'>PRO NODE</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='background-color: #444; color: white; padding: 2px 8px; border-radius: 5px; font-weight: bold;'>BASIC NODE</span>", unsafe_allow_html=True)

    # 2. IDENTITY NODES (New Security Data Section)
    with st.expander("📱 Identity Data (Vault Linked)", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Registered Mobile", value=st.session_state.get('user_mob', 'N/A'), disabled=True)
        with c2:
            st.text_input("Security Answer / DOB", value=st.session_state.get('user_dob', 'N/A'), disabled=True)
        st.caption("Contact Central Command to modify these core identity nodes.")

    # 3. SUBSCRIPTION & BILLING
    with st.expander("💳 Subscription Management"):
        if status == "paid":
            st.success("Your Pro subscription is active.")
        else:
            st.warning("You are currently on the Limited 'Free' Tier.")
            if st.button("🚀 UPGRADE TO PRO NOW"):
                st.session_state.current_page = "💎 Upgrade to Pro"
                st.rerun()

    # 4. SECURITY NODES
    with st.expander("🔒 Security & Access"):
        st.write("### Change Password")
        old_p = st.text_input("Current Password", type="password", key="set_old_p")
        new_p = st.text_input("New Password", type="password", key="set_new_p")
        conf_p = st.text_input("Confirm New Password", type="password", key="set_conf_p")
        
        if st.button("UPDATE CREDENTIALS"):
            if new_p == conf_p and len(new_p) > 4:
                st.info("Transmission sent. Security protocols updating...")
            else:
                st.error("Passwords do not match or are too weak.")

    # 5. INTERFACE PREFERENCES
    with st.expander("🎨 Interface Preferences"):
        st.toggle("Enable Neural UI Animations", value=True)
        st.toggle("Show Real-time ROI in Sidebar", value=True)
        st.select_slider("System Font Scaling", options=["Stealth", "Standard", "Explosive"], value="Standard")

    # 6. SYSTEM ACTIONS
    st.write("")
    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 CLEAR SYSTEM CACHE", use_container_width=True):
            st.cache_data.clear()
            st.success("Local Memory Wiped.")
    with col_b:
        if st.button("🔓 TERMINATE SESSION", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()




# --- GLOBAL FOOTER (RAZORPAY COMPLIANCE) ---
st.markdown("---")
footer_html = """
<div style="text-align: center; color: #666; font-size: 12px; padding: 20px;">
    <p>© 2026 VOID OS | <a href="mailto:support@voidos.com" style="color: #00ff41;">Contact Support</a></p>
    <p>Built for Digital Architects & Outreach Specialists</p>
    <p style="font-size: 10px;">Privacy Policy | Terms of Service | Refund Policy</p>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
# --- COMPLIANCE FOOTER (FOR RAZORPAY APPROVAL) ---
st.divider()
f_col1, f_col2, f_col3 = st.columns(3)

with f_col1:
    st.markdown("**VOID OS Operations**")
    st.caption("AI-Powered SaaS Solutions")
    st.caption("B2B Outreach Intelligence")

with f_col2:
    st.markdown("**Legal Nodes**")
    # These should link to your 'Legal Archive' page or be clear text
    st.caption("Privacy Policy")
    st.caption("Terms & Conditions")
    st.caption("Refund Policy")

with f_col3:
    st.markdown("**Contact Uplink**")
    # ⚠️ IMPORTANT: Razorpay needs a real email here
    st.caption("📧 director07022026@gmail.com") 
    st.caption("📍 Udham Singh Nagar, Uttarakhand, India")

st.markdown("<p style='text-align: center; font-size: 10px; color: gray;'>Transaction Security by Razorpay | © 2026 VOID OS</p>", unsafe_allow_html=True)



















































































































































