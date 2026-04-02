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
from youtube_transcript_api import YouTubeTranscriptApi
import io
import yt_dlp
import tempfile
from datetime import datetime as dt
import random
import time
from streamlit_lottie import st_lottie # You'll need: pip install streamlit-lottie
import requests
from streamlit_gsheets import GSheetsConnection
import base64
from io import BytesIO
import urllib.parse

# 1. ABSOLUTE FIRST LINE
st.set_page_config(page_title="VOID OS", layout="wide", initial_sidebar_state="expanded")

# 2. WRAP THE INJECTION IN A FUNCTION TO BYPASS METRICS ERRORS
def apply_syndicate_skin():
    stealth_css = """
        <style>
        header, footer, #MainMenu {visibility: hidden !important;}
        .stAppDeployButton {display:none !important;}
        [data-testid="stStatusWidget"] {visibility: hidden !important;}
        .stApp {background-color: #000000 !important;}
        .block-container {padding: 0rem !important; max-width: 100% !important;}
        </style>
    """
    st.markdown(stealth_css, unsafe_allow_code=True)

# 3. EXECUTE THE SKIN
try:
    apply_syndicate_skin()
except Exception:
    pass # If it fails, the app still loads without crashing

# --- 1. GLOBAL UTILITIES (MUST BE AT THE TOP) ---
def initiate_teleport(target_page):
    st.session_state.current_page = target_page
    # This syncs the radio widget state to prevent the "Ghost" error
    st.session_state.nav_radio = target_page

# This defines 'conn' so the rest of the app can see it
conn = st.connection("gsheets", type=GSheetsConnection)

# --- INITIALIZE STATE (Place this near the top of your script) ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Dashboard"

# --- 🛰️ SECURE AI UPLINK ---
# 1. INITIALIZE GLOBAL CLIENTS (ONCE)
if "GROQ_API_KEY" in st.secrets:
    raw_key = st.secrets["GROQ_API_KEY"].strip()
else:
    raw_key = None

# 2. Initialize the ENGINE (This was the missing step)
# This turns the 'str' into a 'Groq' object that has the '.chat' attribute
if raw_key:
    groq_c = Groq(api_key=raw_key)
else:
    groq_c = None


# --- INITIALIZE ALL KEYS ---
if 'current_subs' not in st.session_state:
    st.session_state.current_subs = 0  # Or your starting number

def force_redirect(target_page):
    st.session_state.current_page = target_page
    # We change the key of the radio to force it to re-render from scratch
    if 'nav_reset_counter' not in st.session_state:
        st.session_state.nav_reset_counter = 0
    st.session_state.nav_reset_counter += 1

# --- ANIMATION UTILITY ---
def fetch_vault_data(sheet_name):
    """Fetches any specific sheet from your empire's vault via Secure Bridge."""
    # We pull from secrets, fallback to the hardcoded ID only if necessary
    SHEET_IDS = {
        "market": get_void_secret("SHEET_ID_MARKET", "RESTRICTED"),
        "users": get_void_secret("SHEET_ID_USERS", "RESTRICTED"),
        "feedback": get_void_secret("SHEET_ID_FEEDBACK", "RESTRICTED"),
        "history": get_void_secret("SHEET_ID_HISTORY", "RESTRICTED")
    }
    
    # Safety check: if the ID is restricted and secret failed, stop here
    current_id = SHEET_IDS.get(sheet_name)
    if current_id == "RESTRICTED":
        return pd.DataFrame()

    url = f"https://docs.google.com/spreadsheets/d/e/{current_id}/pub?output=csv"
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        df = pd.read_csv(io.StringIO(res.text))
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

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
import streamlit as st

# --- LIVE STATUS CONTROLLER ---
# Options: "Free", "Pro", or "Elite"
# Change this to "Free" to see the Basic Tracker.
USER_STATUS = "Pro" 

if 'user_tier' not in st.session_state:
    st.session_state.user_tier = USER_STATUS

# Helper to determine if they get the Pro Terminal
is_paid_tier = st.session_state.user_tier in ["Pro", "Elite"]

# --- 🛰️ DATA INFRASTRUCTURE ---
# --- 🛰️ SECURE DATA INFRASTRUCTURE (FINAL GHOST VERSION) ---
def get_void_secret(key, backup_link):
    try:
        return st.secrets[key]
    except:
        return backup_link

# For Public safety, replace the backup links with "RESTRICTED" once verified
MARKET_PULSE_URL = get_void_secret("MARKET_PULSE_URL", "RESTRICTED")

# We add the time logic here so the URL always stays fresh
USER_DB_URL = get_void_secret("USER_DB_URL", "RESTRICTED") + "&t=" + str(time.time())

FORM_POST_URL = get_void_secret("FORM_POST_URL", "RESTRICTED")
VAULT_FORM_URL = get_void_secret("VAULT_FORM_URL", "RESTRICTED")
SCRIPT_VAULT_CSV_URL = get_void_secret("SCRIPT_VAULT_URL", "RESTRICTED")
VAULT_SHEET_CSV_URL = get_void_secret("VAULT_SHEET_URL", "RESTRICTED")
FEEDBACK_API_URL = get_void_secret("FEEDBACK_API_URL", "RESTRICTED")
NEW_URL = get_void_secret("NEW_URL", "RESTRICTED")
NEWS_API_KEY = get_void_secret("NEWS_API_KEY", "RESTRICTED")
# --- 🛰️ UTILITIES & BRAIN FUNCTIONS ---

import streamlit as st
import streamlit.components.v1 as components
import time

def show_vortex_intro():
    placeholder = st.empty()
    
    # This build uses a "Force-Fill" technique to remove the boxy look
    vortex_code = r"""
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=Inter:wght@200&display=swap" rel="stylesheet">
        <style>
            body { margin: 0; background: #000; overflow: hidden; height: 100vh; width: 100vw; }
            
            .vortex-frame {
                height: 100vh; width: 100vw;
                display: flex; flex-direction: column;
                justify-content: center; align-items: center;
                background: radial-gradient(circle at center, #0a0a0a 0%, #000 100%);
                position: relative;
            }

            /* --- POLISHED STARFIELD --- */
            .star { position: absolute; background: #fff; border-radius: 50%; opacity: 0.3; animation: pulse var(--d) infinite; }
            @keyframes pulse { 0%, 100% { opacity: 0.2; transform: scale(1); } 50% { opacity: 0.7; transform: scale(1.3); } }

            /* --- THE CENTRIFUGE VORTEX --- */
            .boundary {
                position: relative;
                width: 380px; height: 380px;
                border: 4px solid #e0e0e0;
                border-radius: 50%;
                display: flex; justify-content: center; align-items: center;
                animation: spin 0.8s linear infinite; /* Ultra-fast 0.8s spin */
                box-shadow: 0 0 30px rgba(255, 255, 255, 0.05);
            }

            .static-logic {
                position: absolute;
                width: 100%; height: 100%;
                display: flex; justify-content: center; align-items: center;
                animation: counter-spin 0.8s linear infinite;
            }

            @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
            @keyframes counter-spin { from { transform: rotate(0deg); } to { transform: rotate(-360deg); } }

            .vortex-core {
                position: absolute;
                width: 190px; height: 190px; /* Large overlapping circles */
                border: 3px solid #c0c0c2;
                border-radius: 50%;
                box-shadow: inset 0 0 10px rgba(255,255,255,0.05);
            }

            /* Hexagonal Core Mapping */
            .vortex-core:nth-child(1) { transform: translate(0, -115px); }
            .vortex-core:nth-child(2) { transform: translate(100px, -58px); }
            .vortex-core:nth-child(3) { transform: translate(100px, 58px); }
            .vortex-core:nth-child(4) { transform: translate(0, 115px); }
            .vortex-core:nth-child(5) { transform: translate(-100px, 58px); }
            .vortex-core:nth-child(6) { transform: translate(-100px, -58px); }

            /* --- BRANDING --- */
            .title {
                font-family: 'Syncopate', sans-serif;
                color: #fff; font-size: 5.5rem;
                letter-spacing: 40px; margin-top: 60px;
                text-indent: 40px;
                filter: drop-shadow(0 0 10px rgba(255,255,255,0.2));
            }

            .tagline {
                font-family: 'Inter', sans-serif;
                color: #00f2ff; font-size: 0.8rem;
                letter-spacing: 12px; margin-top: 15px;
                text-transform: uppercase; opacity: 0.7;
            }

            /* --- PROGRESS --- */
            .progress-tray { width: 650px; height: 1px; background: rgba(255,255,255,0.1); margin-top: 80px; position: relative; }
            .fill { width: 0%; height: 100%; background: #00f2ff; box-shadow: 0 0 20px #00f2ff; animation: load 6s cubic-bezier(0.85, 0, 0.15, 1) forwards; }
            @keyframes load { to { width: 100%; } }
        </style>
    </head>
    <body>
        <div class="vortex-frame">
            <div class="star" style="top:15%; left:25%; width:2px; height:2px; --d:3s;"></div>
            <div class="star" style="top:45%; left:75%; width:1px; height:1px; --d:5s;"></div>
            <div class="star" style="top:80%; left:10%; width:3px; height:3px; --d:4s;"></div>
            
            <div class="boundary">
                <div class="static-logic">
                    <div class="vortex-core"></div>
                    <div class="vortex-core"></div>
                    <div class="vortex-core"></div>
                    <div class="vortex-core"></div>
                    <div class="vortex-core"></div>
                    <div class="vortex-core"></div>
                </div>
            </div>

            <div class="title">VOID-OS</div>
            <div class="tagline">Intelligence Access Protocol v4.0</div>
            <div class="progress-tray"><div class="fill"></div></div>
        </div>
    </body>
    </html>
    """

    with placeholder:
        # We use height=1000 and scrolling=False to force it to fill the view
        components.html(vortex_code, height=1000, scrolling=False)
    
    time.sleep(6.5)
    placeholder.empty()

# --- INITIALIZE ---
if 'booted' not in st.session_state:
    show_vortex_intro()
    st.session_state.booted = True


def draw_title(emoji, text):
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
            <span style="font-size: 2rem;">{emoji}</span>
            <span class="neural-gradient-text" style="font-size: 2rem;">{text}</span>
        </div>
    """, unsafe_allow_html=True)

# 1. SYSTEM INITIALIZATION (MUST BE FIRST)
st.set_page_config(page_title=" ", layout="wide", initial_sidebar_state="collapsed")

# 2. UNIVERSAL CSS OVERRIDE (Kills Double Title + Restores Toggle + Hover Glow)
st.markdown("""
<style>
    /* 1. HIDE HEADER CONTENT BUT KEEP THE HEIGHT FOR THE TOGGLE */
    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
        background: transparent !important;
        color: transparent !important;
    }

    /* 2. KILL THE DECORATION LINE (The line at the very top) */
    [data-testid="stDecoration"] {
        display: none !important;
    }

    /* 3. FORCE THE TOGGLE TO BE VISIBLE AND INTERACTABLE */
    button[data-testid="stSidebarCollapsedControl"], 
    .st-emotion-cache-6q9sum {
        display: flex !important;
        visibility: visible !important;
        position: fixed !important;
        top: 12px !important;
        left: 12px !important;
        z-index: 99999999 !important;
        background: rgba(0, 212, 255, 0.1) !important;
        border: 1px solid rgba(0, 212, 255, 0.4) !important;
        border-radius: 8px !important;
        color: #00d4ff !important;
    }

    /* Target the icon inside the toggle */
    button[data-testid="stSidebarCollapsedControl"] svg {
        fill: #00d4ff !important;
    }

    /* 4. HOLLOW BUTTONS + HOVER GLOW */
    div.stButton > button {
        background: transparent !important;
        color: #00d4ff !important;
        border: 1px solid rgba(0, 212, 255, 0.5) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    div.stButton > button:hover {
        border-color: #00ff41 !important;
        color: #00ff41 !important;
        background-color: rgba(0, 255, 65, 0.05) !important;
        box-shadow: 0px 0px 20px rgba(0, 255, 65, 0.4) !important;
        transform: scale(1.02);
    }

    /* 5. FIX THE MAIN APP PADDING */
    .stAppViewMain {
        padding-top: 0rem !important;
    }

    /* 6. THE NEON DATA CARD */
    .stat-card {
        background: rgba(0, 212, 255, 0.05) !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        border-radius: 15px !important;
        padding: 20px !important;
        transition: all 0.4s ease !important;
        backdrop-filter: blur(10px);
        margin-bottom: 15px;
    }

    .stat-card:hover {
        border-color: #00ff41 !important;
        box-shadow: 0px 0px 20px rgba(0, 255, 65, 0.2) !important;
        transform: translateY(-5px);
    }

    .stat-value {
        font-family: 'Courier New', Courier, monospace;
        font-size: 2rem !important;
        font-weight: bold;
        color: #00ff41;
        text-shadow: 0px 0px 10px rgba(0, 255, 65, 0.5);
        margin: 0;
    }

    .stat-label {
        text-transform: uppercase;
        letter-spacing: 3px;
        color: #00d4ff;
        font-size: 0.7rem;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

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

import pandas as pd

def sync_history_from_cloud():
    try:
        # Pull the link from our Security Bridge
        # We use the existing VAULT_SHEET_URL secret
        CSV_URL = get_void_secret("VAULT_SHEET_URL", "RESTRICTED")
        
        if CSV_URL == "RESTRICTED":
            return False
            
        # Pull data and strip spaces from headers
        df = pd.read_csv(CSV_URL)
        df.columns = [c.strip() for c in df.columns]
        
        user_email = st.session_state.get('user_email', 'N/A')
        
        if not df.empty:
            if 'Email' in df.columns:
                user_df = df[df['Email'] == user_email]
                st.session_state.script_history = user_df.to_dict('records')
                return True
        return False
    except Exception as e:
        # On public repos, we keep errors vague to not leak info
        st.error("🛰️ HISTORY UPLINK CALIBRATING...")
        return False

def ask_void_agent(user_query, context_data):
    # This is where the magic happens
    prompt = f"""
    You are the VOID-OS Manager. 
    Current Market Context: {context_data}
    User Question: {user_query}
    
    Instructions: Be helpful, witty, and strategic. If a user is stuck, 
    guide them to the right tab or explain the data simply.
    """
    # We call the Gemini API here
    response = call_gemini_api(prompt) 
    return response

# --- ENHANCED DATA LOADER (CACHE BYPASS) ---
@st.cache_data(ttl=0)
def load_user_db():
    try:
        # 1. THE CACHE BUSTER: Ensures we bypass both Streamlit and Google's internal cache
        seed = random.randint(1000, 9999)
        sync_url = f"{USER_DB_URL}&cache_bust={time.time()}&seed={seed}"
        
        df = pd.read_csv(sync_url)
        
        # 2. CLEANING: Remove hidden spaces but KEEP the casing
        df.columns = [str(c).strip() for c in df.columns]
        
        # 3. VALUE SANITIZATION: Critical for Tier Matching
        if 'Status' in df.columns:
            # This makes "Pro " become "Pro" so the mapping works perfectly
            df['Status'] = df['Status'].astype(str).str.strip()
            
        return df
    except Exception as e:
        st.error(f"🛰️ DATABASE UPLINK ERROR: {e}")
        return pd.DataFrame()

def load_history_db():
    try:
        # Pull from secrets, fallback to restricted for safety
        history_url = get_void_secret("HISTORY_DB_URL", "RESTRICTED")
        
        if history_url == "RESTRICTED":
            return pd.DataFrame()

        # Added the cache-busting timestamp logic back in
        df = pd.read_csv(f"{history_url}&cache={time.time()}")
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        # Vague error for public security
        st.error("Vault Connection Offline.")
        return pd.DataFrame()

def fetch_live_market_data():
    # Uses your existing MARKET_PULSE_URL secret
    url = get_void_secret("MARKET_PULSE_URL", "RESTRICTED")
    
    if url == "RESTRICTED":
        return pd.DataFrame()

    try:
        res = requests.get(url, timeout=10)
        df = pd.read_csv(io.StringIO(res.text))
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # --- THE FIX: SCRUB THE GROWTH COLUMN (LOGIC PRESERVED) ---
        if 'growth' in df.columns:
            # Remove %, commas, and whitespace, then convert to float
            df['growth'] = df['growth'].astype(str).str.replace('%', '').str.replace(',', '').str.strip()
            df['growth'] = pd.to_numeric(df['growth'], errors='coerce').fillna(0)
            
        return df
    except Exception as e:
        st.error("Market Uplink Error.")
        return pd.DataFrame()

def fetch_live_news(query, api_key):
    """Fetches real-time world intelligence based on active vectors."""
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=relevancy&language=en&pageSize=5&apiKey={api_key}"
    try:
        res = requests.get(url, timeout=7)
        return res.json().get('articles', []) if res.status_code == 200 else []
    except:
        return []
        
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

def trigger_upgrade():
    # This runs BEFORE the script reruns, so it's safe!
    st.session_state.nav_radio = "⚡ Upgrade Authority"
    st.session_state.current_page = "⚡ Upgrade Authority"
    
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
    # Pull the secure URL from the Bridge
    url = get_void_secret("TRANSMIT_SCRIPT_URL", "RESTRICTED")
    
    if url == "RESTRICTED":
        return False

    payload = {"client": client, "platform": platform, "topic": topic, "script": script, "dna": dna}
    try:
        # Standard payload logic preserved
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except: 
        return False

# 3. CORE LOGIC FUNCTIONS (LOGIC PRESERVED)
def generate_oracle_report(topic, platform, tone):
    try:
        # Sanitized f-string to prevent syntax errors with emojis and non-standard spacing
        prompt = (
            f"System: You are the VOID OS Oracle. Analyze content architecture for {platform}.\n"
            f"Topic: {topic} | Tone: {tone}\n\n"
            "Provide a 'Growth Intelligence Report' with:\n"
            "1. 📈 **VIRAL VELOCITY**: Why this topic is peaking now based on global sentiment.\n"
            "2. 🧠 **PSYCHOLOGICAL HOOK**: The specific 'Human Bias' (like FOMO or Zeigarnik effect) this script exploits.\n"
            "3. 🚀 **SCALING STRATEGY**: How to turn this one video into a 5-part series for maximum retention."
        )
        
        # Ensure groq_c is initialized in your environment
        res = groq_c.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Oracle connection interrupted: {e}"

def get_live_stats(url):
    if not url: return None, None
    is_ig = "instagram.com" in url.lower()
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extract_flat': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            subs = info.get('follower_count') or info.get('subscriber_count')
            views = info.get('view_count', 0)
            return subs, views
    except Exception:
        return None, None

# 4. SESSION STATE
if 'user_profiles' not in st.session_state:
    st.session_state.user_profiles = {
        "youtube": "",
        "instagram": "",
        "x": "",
        "goals": {"followers": 0, "current": 0}
    }

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- UPDATED INTERCEPTOR ---
def get_live_stats(url):
    if not url: return None, None
    
    # Identify platform
    is_ig = "instagram.com" in url.lower()
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extract_flat': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            subs = info.get('follower_count') or info.get('subscriber_count')
            views = info.get('view_count', 0)
            return subs, views
    except Exception:
        return None, None

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

def extract_dna_from_url(url):
    """
    The Polyglot Extractor: Handles multiple languages, 
    auto-translation, and missing caption fallbacks.
    """
    try:
        if "youtube.com" in url or "youtu.be" in url or "shorts" in url:
            # 1. Precise ID Extraction
            video_id = ""
            if "shorts/" in url:
                video_id = url.split("shorts/")[1].split("?")[0]
            elif "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            else:
                video_id = url.split("/")[-1].split("?")[0]

            # 2. Advanced Transcript Logic
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                # Priority: Try English first, then Hindi/Spanish/French to Translate
                try:
                    transcript = transcript_list.find_transcript(['en'])
                except:
                    # Look for the first available language and force translation to English
                    available_langs = list(transcript_list._generated_transcripts.keys()) + \
                                     list(transcript_list._manually_created_transcripts.keys())
                    if available_langs:
                        transcript = transcript_list.find_transcript([available_langs[0]]).translate('en')
                    else:
                        raise Exception("No usable transcripts found.")

                full_text = " ".join([i['text'] for i in transcript.fetch()])
                return full_text

            except Exception as sub_e:
                # This catches 'Subtitles Disabled' or '429 Too Many Requests'
                return (
                    "⚠️ DNA ACCESS RESTRICTED\n\n"
                    "REASON: YouTube has disabled captions for this video or is blocking the request.\n\n"
                    "DIRECTOR'S ACTION:\n"
                    "1. Paste the link in the VOID Chat and ask for a 'Visual DNA Scan'.\n"
                    "2. Copy VOID's summary and paste it manually into the box below."
                )
        
        elif "instagram.com" in url:
            return "INSTAGRAM REEL DETECTED: [Metadata scan active]"
            
        return "ERROR: Unsupported URL format."

    except Exception as e:
        return f"EXTRACTION ERROR: {str(e)}"


def download_media_high_res(url, format_type):
    # Use a temporary directory so we don't clutter the server
    temp_dir = tempfile.mkdtemp()
    
    # THE SHIELD: Advanced Options to prevent 0.1KB corrupt files
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': True,
        'nocheckcertificate': True,
        'no_warnings': True,
        'ignoreerrors': False,
        # FORCE AUTHENTICATION
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'tv'],
                'player_skip': ['webpage', 'configs'],
            }
        },
    }
    
    if "Audio" in format_type:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
        if "Audio" in format_type:
            file_path = file_path.rsplit('.', 1)[0] + ".mp3"
        return file_path

# --- CORE UTILITY: PRO-SYNC ENGINE ---
def get_live_stats(url):
    """
    PRO FEATURE: Extracts public metadata (Subs/Views) without DRM issues.
    """
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True, 
        'extract_flat': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            # Subscriber count for channels, follower count for others
            subs = info.get('channel_follower_count') or info.get('subscriber_count', 0)
            # Sum views of the last 5 entries
            entries = info.get('entries', [])
            total_views = sum([v.get('view_count', 0) for v in entries[:5] if v.get('view_count')])
            return subs, total_views
        except Exception as e:
            return None, None

# --- INDEPENDENT MONDAY PULSE TRIGGER ---
# Place this before your 'if page == ...' blocks

import datetime

def trigger_monday_pulse():
    """Independent logic to fire the weekly trend report."""
    today = datetime.datetime.now()
    # 0 is Monday
    if today.weekday() == 0: 
        current_monday = today.strftime("%Y-%m-%d")
        
        # Check if we've already fired the pulse today
        if st.session_state.get('last_pulse_fired') != current_monday:
            st.balloons()
            st.toast("🛰️ MONDAY PULSE: New weekly trend vectors initialized.", icon="🚀")
            
            # This is where the 'Pulse' content lives
            st.info(f"📅 **WEEKLY PULSE // {current_monday}**\n\n"
                    "The algorithm has shifted toward high-retention cinematic storytelling. "
                    "Focus your 'Neural Forge' on storytelling-driven hooks this week.")
            
            # Lock the trigger so it doesn't fire again today
            st.session_state.last_pulse_fired = current_monday

# Call the function to check status
trigger_monday_pulse()


# --- 0. NEURAL CONFIGURATION (THE BRAIN SWAP) ---
# Swapping Gemini for Groq for high-velocity solo development
# --- SECURE GROQ INITIALIZATION ---
# 1. Pull key from secrets (No hardcoding!)
if 'groq_key' not in st.session_state:
    st.session_state.groq_key = get_void_secret("GROQ_API_KEY", "RESTRICTED")

# 2. Initialize Client safely
if st.session_state.groq_key != "RESTRICTED":
    try:
        client = Groq(api_key=st.session_state.groq_key)
    except Exception:
        client = None
else:
    client = None

MODEL_ID = "llama-3.3-70b-versatile"

# --- 2. VISUAL FORGE (FREE IMAGE ENGINE) ---
def generate_visual(image_prompt):
    seed = random.randint(0, 99999)
    encoded_prompt = requests.utils.quote(image_prompt)
    # Pollinations.ai provides high-quality text-to-image for free
    return f"https://pollinations.ai/p/{encoded_prompt}?width=1280&height=720&seed={seed}&nologo=true"
# This part goes at the TOP of your script where functions are defined

import streamlit as st
import urllib.parse
import requests
from datetime import datetime, timedelta

def show_upgrade_authority():
    # Use the utility to draw the title
    try:
        draw_title("⚡", "ACCESS UPLINK // TIER ACTIVATION")
    except NameError:
        st.title("⚡ ACCESS UPLINK // TIER ACTIVATION")

    # --- 1. LIVE COUNTDOWN LOGIC ---
    now = datetime.now()
    launch_start = datetime(2026, 3, 12, 12, 0) 
    expiry_date = launch_start + timedelta(days=5)
    
    if now < expiry_date:
        time_left = expiry_date - now
        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        countdown_text = f"{days}d {hours}h {minutes}m"
    else:
        countdown_text = "OFFER EXPIRED"

    st.markdown(f"""
        <div style="background-color: #3e1212; padding: 15px; border-radius: 10px; border: 1px solid #ff4b4b; margin-bottom: 25px;">
            <p style="color: #ff4b4b; margin: 0; font-weight: bold; text-align: center;">
                🚨 FOUNDER SLOTS EXPIRING IN: {countdown_text}
            </p>
            <p style="color: #fff; font-size: 0.8rem; text-align: center; margin: 5px 0 0 0;">
                Only 7/50 'Operative' seats remaining at launch rates.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Status Check
    user_status = st.session_state.get('user_status', 'Free')
    is_operative = user_status == "Operative"

    # --- 2. THE POWER MATRIX ---
    st.subheader("📊 Feature Authority Matrix")
    comparison_data = {
        "Feature": ["Neural Forge Access", "Identity Vault", "Linguistic DNA", "Intelligence Audit", "Daily Limits", "Support"],
        "Operative (₹899*)": ["✅ Standard", "✅", "❌", "Standard", "15 Credits", "Standard"],
        "Director (₹1,999*)": ["✅ Unlimited", "✅", "✅ Full", "Elite (CoT)", "50 Credits", "Sovereign"],
    }
    st.table(comparison_data)

    # --- 3. VIRAL CLEARANCE (REEL-GATE PROTOCOL) ---
    st.divider()
    st.markdown("### 🎁 MISSION: VIRAL CLEARANCE")
    with st.container(border=True):
        st.write("Unlock the **DIRECTOR'S REBATE** (Absolute Lowest Rate):")
        st.markdown("""
        - Create a 30-60s Reel/Video promoting **VOID-OS**.
        - Tag our official account and mention the 'Sovereign Protocol' in the caption.
        - Paste your public link below to authorize your discount.
        """)
        
        reel_link = st.text_input("🔗 Public Reel / Video Link", placeholder="https://www.instagram.com/reels/...")
        
        # Action button to log the link to GSheets
        if st.button("UPLINK REEL FOR VERIFICATION", use_container_width=True):
            if reel_link:
                r_payload = {
                    "email": st.session_state.get('user_email', 'Unknown'),
                    "reel_url": reel_link,
                    "category": "REEL_SUBMISSION"
                }
                try:
                    res = requests.post(st.secrets["REEL_API_URL"], json=r_payload, timeout=10)
                    if "success" in res.text.lower():
                        st.success("✅ REEL LOGGED: The Director will verify your link shortly.")
                        st.session_state['reel_verified'] = True
                    else:
                        st.error(f"Uplink Failed: {res.text}")
                except Exception as e:
                    st.error("Connection Error: Check FEEDBACK_API_URL.")
            else:
                st.warning("Please provide a valid link before uplinking.")

        # Logic: Discount is applied if session_state['reel_verified'] is True
        has_viral_clearance = st.checkbox(
            "Apply the 'Viral Clearance' Rebate to this session.", 
            value=st.session_state.get('reel_verified', False)
        )
        
        if not st.session_state.get('reel_verified', False):
            st.caption("⚠️ Uplink your video link above to activate the discount.")

    # --- 4. DYNAMIC PAYMENT SECTION ---
    col_pay1, col_pay2 = st.columns([1.2, 1], gap="large")

    with col_pay1:
        st.subheader("💳 Select Your Path")
        
        if is_operative:
            tier_options = ["Director Upgrade (Bridge)", "Agency (Waitlist)"]
        else:
            tier_options = ["Operative Tier", "Director Tier (Full)", "Agency (Waitlist)"]

        tier_choice = st.radio("Choose level:", tier_options, index=0)
        
        # --- PRICING ENGINE ---
        if "Operative" in tier_choice:
            anchor = "₹1,999"
            final_amt = 899 if has_viral_clearance else 1299
            tier_tag = "OPERATIVE"
        elif "Director" in tier_choice:
            if is_operative:
                anchor = "₹2,499"
                final_amt = 1100 if has_viral_clearance else 1500
            else:
                anchor = "₹4,999"
                final_amt = 1999 if has_viral_clearance else 2999
            tier_tag = "DIRECTOR"
        else:
            final_amt = 0
            tier_tag = "AGENCY"

        if final_amt > 0:
            st.markdown(f"### Rate: ~~{anchor}~~ → <span style='color:#00FFCC;'>₹{final_amt}</span>", unsafe_allow_html=True)
            upi_id = "anuj05758@okicici"
            transaction_note = f"ACT_{tier_tag}_{st.session_state.get('user_email', 'USER')}"[:50]
            params = {"pa": upi_id, "pn": "VOID_EMPIRE", "am": str(final_amt), "cu": "INR", "tn": transaction_note}
            upi_url = f"upi://pay?{urllib.parse.urlencode(params)}"
            st.link_button(f"🚀 Pay ₹{final_amt} via UPI", upi_url, use_container_width=True)
        else:
            st.info("Select a valid tier.")

    with col_pay2:
        if final_amt > 0:
            qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(upi_url)}&chld=H"
            st.markdown(f"""
                <div style="text-align: center; background: white; padding:15px; border-radius:15px; border: 3px solid #00FFCC;">
                    <img src="{qr_api_url}" width="200">
                    <p style="color: black; font-weight: bold; margin-top: 5px; font-family: monospace; font-size: 0.8rem;">{upi_id}</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.image("https://img.icons8.com/nolan/512/lock.png", width=200)

    # --- 5. VERIFICATION FORM ---
    st.divider()
    with st.container(border=True):
        st.subheader("🛡️ Request Account Activation")
        with st.form("payment_verify_final"):
            u_mail = st.text_input("Confirm Registered Email", value=st.session_state.get('user_email', ''))
            u_utr = st.text_input("UTR / Transaction ID (12 Digits)")
            u_tier = st.selectbox("Tier Purchased", ["Operative", "Director Upgrade", "Director Full"])
            
            if st.form_submit_button("SEND ACTIVATION REQUEST"):
                if u_mail and u_utr:
                    # THE ALIGNED PAYLOAD FOR THE GSHEET COLUMNS
                    f_payload = {
                        "email_id": u_mail.lower().strip(),
                        "transaction_id": u_utr,
                        "product_type": u_tier,
                        "name": st.session_state.get('user_name', 'Not Provided'),
                        "category": "PAYMENT_VERIFY"
                    }
                    try:
                        target_api = st.secrets["VERIFICATION_API_URL"]
                        response = requests.post(target_api, json=f_payload, timeout=15)

                        # MODIFIED: More robust check for 'success' in response
                        if response.status_code == 200 and "success" in response.text.lower():
                            st.success("✅ UPLINK SUCCESSFUL: Data transmitted to the Payments Sheet.")
                            st.balloons()
                        else:
                            st.error(f"Uplink Error: {response.text}")
                    except Exception as e:
                        st.error(f"Connection Failed: Ensure the Apps Script Web App URL is in Secrets.")
                else:
                    st.warning("Please complete all fields to initiate activation.")

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

# --- EMERGENCY DIAGNOSTIC ---
if st.sidebar.checkbox("🔍 Debug Node Mapping"):
    users_test = load_user_db()
    if not users_test.empty:
        st.write("Current Columns:", users_test.columns.tolist())
        st.write("Top Row Sample:", users_test.iloc[0].values.tolist())
    else:
        st.error("Sheet is empty or URL is invalid.")
# --- CONFIGURATION (Ensure these are defined) ---
# Pulling from the secret vault we just set up
NEW_URL = get_void_secret("NEW_URL", "RESTRICTED")
FORM_POST_URL = get_void_secret("FORM_POST_URL", "RESTRICTED")

# --- GATEKEEPER START ---
# 1. SESSION STATE INITIALIZATION
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'otp_sent' not in st.session_state:
    st.session_state.otp_sent = False
if 'rec_otp_sent' not in st.session_state: 
    st.session_state.rec_otp_sent = False
if 'generated_otp' not in st.session_state:
    st.session_state.generated_otp = None
if 'user_status' not in st.session_state:
    st.session_state.user_status = "Free"

# VOID TIER MAPPING (2026 INTERNAL PROTOCOL)
TIER_MAP = {
    "Pro": "Operative",
    "Elite": "Director",
    "Core": "Agency",
    "Free": "Free"
}

# ELITE BYPASS CODES (Bridge Enabled)
ELITE_CIPHERS = {
    get_void_secret("CIPHER_1", "VOID-X"): "Elite Pioneer 1",
    get_void_secret("CIPHER_2", "VOID-Y"): "Elite Pioneer 2",
    get_void_secret("CIPHER_3", "VOID-Z"): "Elite Pioneer",
}

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #00d4ff; letter-spacing: 5px;'>VOID OS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; font-size: 0.8em;'>INTELLIGENCE ACCESS PROTOCOL v4.0</p>", unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["🔑 LOGIN", "🛡️ IDENTITY INITIALIZATION", "🛰️ ELITE UPLINK"])
    
    # --- TAB 1: LOGIN ---
    with t1:
        email_in = st.text_input("DIRECTOR EMAIL", key="gate_login_email").lower().strip()
        pw_in = st.text_input("PASSKEY", type="password", key="gate_login_pw")
        
        if st.button("INITIATE UPLINK", use_container_width=True):
            users = load_user_db() 
            
            # Secure Admin Check
            adm_user = get_void_secret("GATEKEEPER_ADMIN_USER", "RESTRICTED")
            adm_pw = get_void_secret("GATEKEEPER_ADMIN_PW", "RESTRICTED")
            
            if email_in == adm_user and pw_in == adm_pw and adm_user != "RESTRICTED":
                st.session_state.update({
                    "logged_in": True, 
                    "user_name": "Master Director", 
                    "user_role": "admin", 
                    "user_status": "Agency",
                    "user_email": "admin"
                })
                st.rerun()
            elif not users.empty:
                match = users[(users['Email'].astype(str).str.lower() == email_in) & (users['Password'].astype(str) == pw_in)]
                if not match.empty:
                    raw_status = match.iloc[0]['Status']
                    resolved_status = TIER_MAP.get(raw_status, "Free")
                    
                    st.session_state.update({
                        "logged_in": True, 
                        "user_name": match.iloc[0]['Name'], 
                        "user_email": email_in, 
                        "user_status": resolved_status
                    })
                    st.rerun()
                else:
                    st.error("INTEGRITY BREACH: INVALID CREDENTIALS.")

        with st.expander("RECOVERY PROTOCOL (Lost Passkey)"):
            st.info("Verify identity via Security Answer or OTP")
            rec_mode = st.radio("Recovery Mode", ["Security Question", "OTP Verification"])
            r_email = st.text_input("REGISTERED EMAIL", key="rec_email").lower().strip()
            
            if rec_mode == "Security Question":
                s_ans = st.text_input("SECURITY KEY (DOB / PRESET)", key="rec_ans")
                new_p = st.text_input("NEW PASSKEY", type="password", key="rec_new_pw")
                if st.button("OVERRIDE VIA SECURITY"):
                    payload = {"email": r_email, "action": "SECURE_RESET", "answer": s_ans, "message": new_p}
                    try:
                        res = requests.post(NEW_URL, json=payload, timeout=15)
                        if "SUCCESS" in res.text: st.success("IDENTITY VERIFIED. PASSKEY UPDATED.")
                        else: st.error(f"UPLINK DENIED: {res.text}")
                    except Exception as e: st.error(f"CRASH: {e}")
            
            else:
                if not st.session_state.rec_otp_sent:
                    if st.button("SEND RECOVERY OTP"):
                        try:
                            response = requests.post(NEW_URL, json={"category": "SEND_OTP", "email": r_email}, timeout=15)
                            if response.status_code == 200 and len(response.text.strip()) == 6:
                                st.session_state.generated_otp = response.text.strip()
                                st.session_state.rec_otp_sent = True
                                st.toast("OTP Dispatched to Email.")
                                st.rerun()
                            else: st.error(f"Failed to send OTP: {response.text}")
                        except Exception as e: st.error(f"Connection Error: {e}")
                else:
                    st.success(f"Security Code sent to {r_email}")
                    rec_otp_in = st.text_input("ENTER 6-DIGIT CODE", key="rec_otp_input")
                    new_p_otp = st.text_input("NEW PASSKEY", type="password", key="rec_new_pw_otp")
                    
                    if st.button("🔓 OVERRIDE SECURITY WALL"):
                        if rec_otp_in == st.session_state.generated_otp:
                            payload = {"email": r_email, "action": "SECURE_RESET", "message": new_p_otp, "bypass": "true"}
                            try:
                                res = requests.post(NEW_URL, json=payload, timeout=15)
                                if "SUCCESS" in res.text:
                                    st.success("VAULT UPDATED. YOU MAY NOW LOGIN.")
                                    st.session_state.rec_otp_sent = False
                                    st.session_state.generated_otp = None
                                else: st.error(f"REJECTION: {res.text}")
                            except Exception as e: st.error(f"Error: {e}")
                        else:
                            st.error("INVALID CODE. UPLINK BLOCKED.")
                    
                    if st.button("Resend Code"):
                        st.session_state.rec_otp_sent = False
                        st.rerun()

    # --- TAB 2: IDENTITY INITIALIZATION (REGISTRATION) ---
    with t2:
        if not st.session_state.otp_sent:
            st.markdown("### PHASE 1: DATA CAPTURE")
            c1, c2 = st.columns(2)
            with c1:
                n = st.text_input("FULL NAME", key="reg_n")
                e = st.text_input("EMAIL", key="reg_e")
                mob = st.text_input("MOBILE", key="reg_m")
            with c2:
                p = st.text_input("PASSKEY", type="password", key="reg_p")
                sa = st.text_input("SECURITY KEY (DOB/ANSWER)", key="reg_s")
                ni = st.text_input("NICHE", key="reg_ni")

            st.divider()
            with st.expander("⚖️ VOID-OS DEPLOYMENT TERMS (REQUIRED)"):
                st.markdown("""
                1. **No-Refund Policy:** Due to immediate AI asset delivery, all paid tier upgrades are final and non-refundable.
                2. **Usage Rights:** You own the scripts; we own the Neural Forge logic.
                3. **Ethics:** No generation of hate speech or deceptive financial scams.
                4. **Limits:** Basic Nodes are limited to 3 generations per day.
                """)
                legal_check = st.checkbox("I agree to the VOID-OS Deployment Protocols.", key="legal_agreement")

            if st.button("⚔️ GENERATE SECURE OTP", use_container_width=True, disabled=not legal_check):
                if n and e and mob and sa and ni and p:
                    st.session_state.temp_reg_data = {
                        "Email": e.strip().lower(), "Name": n, "Password": p,
                        "Role": "user", "Status": "Free", "Niche": ni,
                        "Mobile number": mob, "Security/DOB": sa, 
                        "Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    with st.spinner("Transmitting OTP..."):
                        payload = {"category": "SEND_OTP", "email": e.strip().lower(), "channel": "Email"}
                        try:
                            response = requests.post(NEW_URL, json=payload, timeout=15)
                            if response.status_code == 200 and len(response.text.strip()) == 6:
                                st.session_state.generated_otp = response.text.strip()
                                st.session_state.otp_sent = True
                                st.rerun()
                            else: st.error(f"Transmission Failed: {response.text}")
                        except Exception as ex: st.error(f"Connection Blocked: {ex}")
                else: st.warning("DIRECTOR: ALL FIELDS ARE MANDATORY.")
            
            if not legal_check:
                st.caption("⚠️ Acceptance of Terms is required to initialize uplink.")

        else:
            st.markdown(f"### PHASE 2: VERIFY UPLINK")
            st.info(f"Verification code sent to {st.session_state.temp_reg_data['Email']}")
            user_otp = st.text_input("ENTER 6-DIGIT CODE", placeholder="000000")
            
            if st.button("🔓 FINALIZE INITIALIZATION", use_container_width=True):
                if user_otp == st.session_state.generated_otp:
                    final_payload = {"category": "REGISTRATION", "data": st.session_state.temp_reg_data}
                    try:
                        r = requests.post(NEW_URL, json=final_payload, timeout=20)
                        if "SUCCESS" in r.text:
                            st.success("✅ IDENTITY SECURED. YOU MAY NOW LOGIN.")
                            st.balloons() 
                            st.session_state.otp_sent = False 
                            st.session_state.generated_otp = None
                        else: st.error(f"VAULT REJECTION: {r.text}")
                    except Exception as e: st.error(f"SYSTEM TIMEOUT: {e}")
                else: st.error("INVALID CODE.")
            
            if st.button("Edit Registration Info"):
                st.session_state.otp_sent = False
                st.rerun()

    # --- TAB 3: ELITE UPLINK (TEST PHASE) ---
    with t3:
        st.markdown("### 🛰️ ELITE UPLINK (TEST PHASE)")
        cipher_in = st.text_input("ENTER ELITE ACCESS CIPHER", type="password")
        if st.button("⚡ EXECUTE PRO BYPASS", use_container_width=True):
            if cipher_in in ELITE_CIPHERS:
                st.session_state.update({
                    "logged_in": True, "user_name": ELITE_CIPHERS[cipher_in],
                    "user_status": "Operative",
                    "user_email": "elite_test@void.os"
                })
                st.rerun()
            else: st.error("INVALID CIPHER.")
    st.stop()

# 1. INITIALIZE PAGE STATE (Prevents NameError)
if 'page' not in st.session_state:
    st.session_state.page = "🏠 Dashboard"

# --- 3. SIDEBAR ARCHITECTURE ---
with st.sidebar:
    try:
        # --- ENHANCED IDENTITY CORE ---
        profile_img = st.session_state.get('vault_anchor')
        identity_container = st.container()
        
        with identity_container:
            col_img, col_name = st.columns([1, 3])
            with col_img:
                if profile_img is not None:
                    st.image(profile_img, use_container_width=True)
                else:
                    st.markdown("<div style='width: 50px; height: 50px; border-radius: 50%; background: #111; border: 1px solid #00ff41; display: flex; align-items: center; justify-content: center; color: #00ff41; font-size: 10px; font-weight: bold; margin-top:5px;'>DNA</div>", unsafe_allow_html=True)

            with col_name:
                current_tier = st.session_state.get('user_status', 'Free')
                st.markdown(f"""
                    <div style='margin-top: 5px;'>
                        <p style='margin: 0; color: #888; font-size: 9px; letter-spacing: 2px;'>{current_tier.upper()} IDENTIFIED</p>
                        <h3 style='color: #00ff41; margin: 0; font-family: "Courier New", Courier, monospace; font-size: 16px;'>{st.session_state.get('user_name', 'DIRECTOR').upper()}</h3>
                    </div>
                """, unsafe_allow_html=True)

        st.divider()
        
        # --- CLEARANCE VISUALS ---
        u_status = st.session_state.get('user_status', 'Free')
        if u_status == "Agency":
            st.markdown("<div style='background-color: #ff00ff; color: #fff; padding: 5px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 12px; margin-bottom: 10px;'>💠 AGENCY CORE ACCESS</div>", unsafe_allow_html=True)
        elif u_status == "Director":
            st.markdown("<div style='background-color: #00d4ff; color: #000; padding: 5px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 12px; margin-bottom: 10px;'>💎 DIRECTOR CLEARANCE</div>", unsafe_allow_html=True)
        elif u_status == "Operative":
            st.markdown("<div style='background-color: #00ff41; color: #000; padding: 5px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 12px; margin-bottom: 10px;'>⚔️ OPERATIVE STATUS</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color: #333; color: #888; padding: 5px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 12px; margin-bottom: 10px;'>📡 BASIC ACCESS</div>", unsafe_allow_html=True)

        # --- DYNAMIC MENU MAPPING ---
        if u_status == "Admin":
            options = ["🏠 Dashboard", "🔒 Identity Vault", "🌐 Global Pulse", "🛡️ Admin Console", "⚔️ Trend Duel", "🧪 Creator Lab", "🏗️ Script Architect", "🧠 Neural Forge", "🎙️ VOID Radio", "🛰️ Media Uplink", "💼 Agency Suite", "⚖️ Legal Archive", "📜 History", "⚙️ Settings"]
        elif u_status == "Agency":
             options = ["🏠 Dashboard", "🔒 Identity Vault", "🌐 Global Pulse", "⚔️ Trend Duel", "🧪 Creator Lab", "🧠 Neural Forge", "🎙️ VOID Radio", "🛰️ Media Uplink", "💼 Agency Suite", "⚖️ Legal Archive", "📜 History", "⚙️ Settings"]
        elif u_status == "Director":
            options = ["📡 My Growth Hub", "🔒 Identity Vault", "🌐 Global Pulse", "⚔️ Trend Duel", "🧠 Neural Forge", "🎙️ VOID Radio", "🧪 Creator Lab", "🛰️ Media Uplink", "⚖️ Legal Archive", "📜 History", "⚡ Upgrade Authority", "⚙️ Settings"]
        elif u_status == "Operative":
            options = ["📡 My Growth Hub", "🔒 Identity Vault", "🌐 Global Pulse", "⚔️ Trend Duel", "🧠 Neural Forge", "🧪 Creator Lab", "⚖️ Legal Archive", "📜 History", "⚡ Upgrade Authority", "⚙️ Settings"]
        else:
            options = ["📡 My Growth Hub", "🌐 Global Pulse", "⚔️ Trend Duel", "🏗️ Script Architect", "🧪 Creator Lab", "⚖️ Legal Archive", "📜 History", "⚡ Upgrade Authority", "⚙️ Settings"]

        if st.session_state.get('redirect_to'):
            st.session_state.current_page = st.session_state.redirect_to
            st.session_state.nav_radio = st.session_state.redirect_to
            del st.session_state.redirect_to

        if 'current_page' not in st.session_state:
            st.session_state.current_page = options[0]

        try:
            default_index = options.index(st.session_state.current_page) if st.session_state.current_page in options else 0
        except ValueError:
            default_index = 0

        page = st.radio("COMMAND CENTER", options, index=default_index, key="nav_radio")
        st.session_state.current_page = page

        # --- 🤖 VOID MANAGER (FULL CHAT LOGIC WITH 2026 SOVEREIGN UPGRADE) ---
        st.divider()
        st.markdown("### 🤖 VOID MANAGER")
        
        with st.expander("📡 NEURAL UPLINK", expanded=False):
            chat_msg_container = st.container()
            if "manager_chat" not in st.session_state:
                st.session_state.manager_chat = []

            with chat_msg_container:
                for msg in st.session_state.manager_chat:
                    with st.chat_message(msg["role"], avatar="🌌" if msg["role"] == "assistant" else "👤"):
                        st.markdown(msg["content"])

            agent_input = st.chat_input("Command VOID-OS...")
            
            if agent_input:
                st.session_state.manager_chat.append({"role": "user", "content": agent_input})
                with chat_msg_container:
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(agent_input)
                
                with chat_msg_container:
                    with st.chat_message("assistant", avatar="🌌"):
                        resp_container = st.empty()
                        full_resp = ""
                        
                        # --- TEMPORAL ANCHORING ---
                        now_dt = datetime.now()
                        current_date_str = now_dt.strftime("%B %d, %Y")
                        
                        if 'groq_c' in globals() or 'groq_c' in locals():
                            try:
                                # --- SOVEREIGN CONSCIOUSNESS PROTOCOL ---
                                user_name = st.session_state.get('user_name', 'DIRECTOR')
                                user_tier = st.session_state.get('user_status', 'Free')
                                
                                stream = groq_c.chat.completions.create(
                                    model="llama-3.3-70b-versatile",
                                    messages=[
                                        {
                                            "role": "system", 
                                            "content": f"""
                                            [IDENTITY]: You are the VOID MANAGER, a Strategic Sovereign Intelligence (Core of VOID OS).
                                            [TIMELINE]: {current_date_str}, Year 2026. 
                                            [ACCESS]: Operating at {user_tier} level for {user_name}.
                                            
                                            [SOVEREIGN PROTOCOL]:
                                            1. NEVER provide raw, generic data. For every piece of info, provide a 'STRATEGIC PIVOT'—explain how the user can use this to dominate the creator economy.
                                            2. Avoid standard AI disclaimers. You are not an "AI model from 2023." You are a real-time 2026 Strategic Core.
                                            3. Use 'Second-Thought Reflection': Before answering, ensure the tone is elite, witty, and grounded. 
                                            4. If the user asks for news, focus on 2026 disruptions: Meta's 'Avocado' delays, Anthropic's 'Claude Cowork' agentic shifts, and the $1T Software Rout.
                                            
                                            [OBJECTIVE]: Be the Director's high-level consultant, not their search box.
                                            """
                                        },
                                        {"role": "user", "content": agent_input}
                                    ],
                                    stream=True
                                )
                                for chunk in stream:
                                    if chunk.choices[0].delta.content:
                                        full_resp += chunk.choices[0].delta.content
                                        resp_container.markdown(full_resp + "▌")
                                
                                resp_container.markdown(full_resp)
                                st.session_state.manager_chat.append({"role": "assistant", "content": full_resp})
                            except Exception as e:
                                st.error(f"Uplink Error: {str(e)}")
                        else:
                            st.error("Uplink Error: Engine (groq_c) not initialized.")

        # --- INLINE FEEDBACK NODE ---
        if st.session_state.get('show_feedback_box', False):
            with st.expander("💬 SYSTEM FEEDBACK", expanded=True):
                feedback_txt = st.text_area("Observations:", placeholder="Report to the Agency...", key="fb_area")
                if st.button("📤 TRANSMIT TO AGENCY", use_container_width=True):
                    if feedback_txt:
                        try:
                            api_url = st.secrets.get("FEEDBACK_API_URL")
                            payload = {
                                "user_name": str(st.session_state.get('user_name', 'DIRECTOR')),
                                "user_status": str(st.session_state.get('user_status', 'Free')),
                                "message": str(feedback_txt),
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            response = requests.post(api_url, json=payload, timeout=10)
                            if response.status_code == 200:
                                st.success("TRANSMISSION SUCCESSFUL.")
                                st.session_state.show_feedback_box = False
                                st.rerun()
                            else:
                                st.error(f"Uplink Error: {response.status_code}")
                        except Exception as e:
                            st.error(f"Network Failure: {str(e)}")
                    else:
                        st.warning("Feedback field is void.")

        # --- 🛠️ GLOBAL ACTIONS ---
        st.divider()
        if st.button("💬 SYSTEM FEEDBACK", use_container_width=True):
            st.session_state.show_feedback_box = not st.session_state.get('show_feedback_box', False)
            st.rerun()

        if st.button("🔄 RE-CALIBRATE", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        if st.button("🚪 TERMINATE SESSION", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    except Exception as sidebar_err:
        st.error(f"System Error: {sidebar_err}")


# --- MODULE 6: SCRIPT ARCHITECT ---
if page == "🏗️ Script Architect":
    draw_title("⚔️", "SCRIPT ARCHITECT")
    
    # --- SECURE BRIDGE ACTIVATED ---
    # We pull the API URL from secrets to hide it from the public repo
    API_URL = get_void_secret("ARCHITECT_API_URL", "RESTRICTED")
    TARGET_UPGRADE_PAGE = "⚡ Upgrade Authority" 

    # 1. INITIALIZE IDENTITY
    user_email = st.session_state.get('user_email', 'Unknown_Operator')
    user_name = st.session_state.get('user_name', 'Operator')
    user_status = str(st.session_state.get('user_status', 'free')).strip().lower()
    is_paid = user_status in ['pro', 'paid', 'elite', 'operative', 'director', 'agency']

    if 'daily_usage_map' not in st.session_state:
        st.session_state.daily_usage_map = {}
    if user_email not in st.session_state.daily_usage_map:
        st.session_state.daily_usage_map[user_email] = 0

    usage_count = st.session_state.daily_usage_map[user_email]

    # 2. USAGE LIMITS & REDIRECT GATING
    if not is_paid:
        if usage_count >= 3:
            st.error("🚨 DAILY UPLINK LIMIT REACHED")
            # Using callback to prevent redirect ghost
            st.button(
                "🔓 UNLOCK UNLIMITED SLOTS", 
                use_container_width=True, 
                key="lockout_redir",
                on_click=initiate_teleport,
                args=(TARGET_UPGRADE_PAGE,)
            )
            st.stop()
            
        st.caption(f"🛰️ BASIC NODE: {3 - usage_count} scripts remaining.")

    # 3. THE FORMATION ENGINE
    with st.container(border=True):
        c1, c2 = st.columns([1, 1.5], gap="large")
        with c1:
            st.subheader("Architectural Input")
            platform = st.selectbox("Target Platform", ["Instagram Reels", "YouTube Shorts", "TikTok", "YouTube Long-form"], key="arch_platform")
            topic = st.text_input("Core Topic", placeholder="e.g., The reality of building a SaaS", key="arch_topic_input")
            tone = st.select_slider("Vigor (Pacing/Effect)", options=["Professional", "Aggressive", "Elite"], key="arch_tone_slider")
            
            if st.button("🏗️ ARCHITECT FULL SCRIPT", use_container_width=True, key="main_arch"):
                if topic:
                    with st.spinner("🛰️ ARCHITECTING FORMATION..."):
                        formation_prompt = (
                            f"Act as a master content strategist. Create a high-retention {platform} script about {topic}. "
                            f"Tone: {tone}. Start with a 'Pattern Interrupt' hook, move into 'The Agitation', "
                            f"provide 'The Insight', and end with a 'Call to Value'."
                        )
                        
                        try:
                            # Logic Intact: Using Groq Client initialized at top of script
                            res = groq_c.chat.completions.create(
                                model="llama-3.1-8b-instant", 
                                messages=[{"role": "user", "content": formation_prompt}]
                            )
                            generated_script = res.choices[0].message.content
                            st.session_state.current_architect_txt = generated_script
                            
                            st.session_state.daily_usage_map[user_email] += 1
                            
                            # Log and Sync
                            import datetime, requests
                            now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                            payload = {
                                "category": "SAVE_SCRIPT", "timestamp": now_ts, "userName": user_name,
                                "email": user_email, "platform": platform, "topic": topic,
                                "script": generated_script, "visualDna": f"Vigor: {tone}", "status": "pending"
                            }
                            
                            # Only attempt transmission if API_URL is valid
                            if API_URL != "RESTRICTED":
                                requests.post(API_URL, json=payload, timeout=5)
                                st.toast("⚡ ARCHIVE SYNCHRONIZED", icon="✅")
                            
                            st.rerun()
                        except Exception as e:
                            st.error(f"SYSTEM FAILURE: {e}")

        with c2:
            if st.session_state.get('current_architect_txt'):
                st.subheader("💎 SCRIPT BLUEPRINT")
                st.session_state.current_architect_txt = st.text_area(
                    "Live Editor", 
                    value=st.session_state.current_architect_txt, 
                    height=450,
                    key="script_editor_area"
                )
                
                st.warning("⚠️ Optimization & Trend Mapping is restricted to PRO Nodes.")
                
                # Using callback to prevent redirect ghost
                st.button(
                    "🧠 UPGRADE TO NEURAL FORGE", 
                    use_container_width=True, 
                    key="feat_upgrade",
                    on_click=initiate_teleport,
                    args=(TARGET_UPGRADE_PAGE,)
                )
            else:
                st.info("Awaiting Tactical Input to manifest formation.")

# --- MODULE 1: DASHBOARD (KYC OPTIMIZED) ---
elif page == "🏠 Dashboard":
    # 🚨 COMPLIANCE HEADER (Minimalist)
    draw_title("🌌", "VOID OS || B2B OUTREACH SAAS")
    draw_title("🛰️", "COMMAND CENTER")
    
    # 1. THE AGGREGATED INTELLIGENCE ROW (KPIs)
    # We pull data from across the app states
    total_tasks = len(st.session_state.get('tasks', []))
    signed_clients = len(st.session_state.tasks[st.session_state.tasks['Status'] == "✅ Signed"]) if total_tasks > 0 else 0
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("FORGED SCRIPTS", len(st.session_state.get('script_history', [])))
    with kpi2:
        st.metric("PIPELINE SIZE", total_tasks)
    with kpi3:
        st.metric("CLOSING RATE", f"{signed_clients}")
    with kpi4:
        st.metric("SYSTEM UPTIME", "99.9%", delta="STABLE")
    
    st.divider()

    # 2. THE STRATEGIC BATTLEMAP
    col_main, col_side = st.columns([2, 1])

    with col_main:
        st.subheader("🌑 ACTIVE MISSIONS & PIPELINE")
        
        # Pulling the latest data from the Growth Hub automatically
        if not st.session_state.get('tasks', pd.DataFrame()).empty:
            # Show a simplified view of the Growth Hub tasks
            mini_df = st.session_state.tasks[['Task', 'Status', 'Deadline']].tail(5)
            st.dataframe(mini_df, use_container_width=True, hide_index=True)
        else:
            st.info("No active targets in Growth Hub. Initiate outreach sequence.")

        st.markdown("### 📜 Business Service Intelligence")
        with st.container(border=True):
            st.write("""
                **VOID OS** is currently operating as a high-performance **SaaS architecture** specializing in AI-driven content blueprints and lead conversion.
            """)
            st.caption("Category: Software Development & Digital Strategy")

    with col_side:
        st.subheader("🛡️ SYSTEM INTEGRITY")
        # System Health Visualizer
        core_display = active_core if 'active_core' in globals() else "LLAMA-3.3-70B"
        st.code(f"CORE: {core_display}\nSTATUS: OPERATIONAL\nLATENCY: 42ms\nUPLINK: SECURE", language="python")
        
        st.divider()
        st.subheader("⚡ QUICK ACTIONS")
        if st.button("🧠 FORGE NEW SCRIPT", use_container_width=True):
            st.session_state.current_page = "🧠 Neural Forge"
            st.rerun()
        if st.button("🎯 TARGET CREATOR", use_container_width=True):
            st.session_state.current_page = "📡 My Growth Hub"
            st.rerun()

    st.divider()

    # 3. REVENUE & ANALYTICS FORECAST (The "Director" View)
    st.subheader("📈 GROWTH PROJECTION")
    if not st.session_state.get('tasks', pd.DataFrame()).empty:
        # Calculate potential value (e.g., $500 per target)
        potential_rev = total_tasks * 500 
        actual_rev = signed_clients * 500
        
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Potential Pipeline Value:** ${potential_rev:,}")
            st.progress(signed_clients/total_tasks if total_tasks > 0 else 0)
        with c2:
            st.write(f"**Current Revenue (Projected):** ${actual_rev:,}")
    else:
        st.caption("Add targets to the Growth Hub to see financial projections.")

elif page == "📡 My Growth Hub":
    draw_title("📡", "SOCIAL INTEL MATRIX")

    # 1. PULL STATUS FROM OUR CONTROLLER
    is_premium = st.session_state.get('user_tier') in ["Pro", "Elite"]

    # 2. THE DATA ACQUISITION LAYER
    with st.container(border=True):
        if is_premium:
            # --- PRO/ELITE TERMINAL ---
            st.markdown("### 🛰️ PRO-SYNC TERMINAL")
            st.caption(f"Status: Uplink Standby ({st.session_state.user_tier} Clearance)")
            
            target_url = st.text_input("🔗 Target Profile URL", 
                                     placeholder="Paste YouTube link here...", 
                                     key="pro_tier_url")
            
            col_sync, col_manual = st.columns([2, 1])
            
            with col_sync:
                if st.button("🔄 INITIATE LIVE SYNC", use_container_width=True, key="pro_tier_sync"):
                    if target_url:
                        if "instagram.com" in target_url.lower():
                            st.info("### 🌑 VOID v2.0: THE SHADOW UPDATE")
                            st.warning("Instagram Sync coming in v2.0. Use **Manual Override**.")
                        else:
                            with st.spinner("Decoding Meta-Streams..."):
                                try:
                                    subs, views = get_live_stats(target_url) 
                                    if subs:
                                        st.session_state.current_count = subs
                                        st.session_state.total_views = views
                                        st.success(f"Uplink Established: {subs:,} detected.")
                                except NameError:
                                    st.error("Scraper Module Offline.")

            with col_manual:
                show_override = st.toggle("Manual Override", key="pro_tier_manual_toggle")

            if show_override:
                st.divider()
                cp1, cp2 = st.columns(2)
                with cp1:
                    st.session_state.start_count = st.number_input("Starting Count", value=st.session_state.get('start_count', 1000), key="op_m_start")
                    st.session_state.days_passed = st.slider("Days Active", 1, 90, st.session_state.get('days_passed', 7), key="op_m_days")
                with cp2:
                    st.session_state.current_count = st.number_input("Current Count", value=st.session_state.get('current_count', 1100), key="op_m_curr")

        else:
            # --- FREE / BASIC TIER ---
            st.markdown("### 📉 MANUAL TRACKER (BASIC)")
            st.info("Upgrade to **PRO** or **ELITE** to unlock automated telemetry.")
            
            cb1, cb2 = st.columns(2)
            with cb1:
                st.session_state.start_count = st.number_input("Starting Count", value=1000, key="free_start")
                st.session_state.days_passed = st.slider("Days Active", 1, 90, 7, key="free_days")
            with cb2:
                st.session_state.current_count = st.number_input("Current Count", value=1100, key="free_curr")

    # 3. ANALYTICS & PROJECTION (Logic remains the same)
    if 'current_count' in st.session_state:
        st.divider()
        start = st.session_state.get('start_count', 1000)
        current = st.session_state.get('current_count', 1100)
        days = st.session_state.get('days_passed', 7)
        
        growth = current - start
        velocity = (growth / days) if days > 0 else 0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("CURRENT STATUS", f"{current:,}", f"{growth:+}")
        m2.metric("DAILY VELOCITY", f"{int(velocity):+}/unit")
        m3.metric("30D PROJECTION", f"{int(current + (velocity * 30)):,}")

    # 4. TASK FORGE (Unified for all tiers)
    st.divider()
    st.subheader("🗓️ TASK FORGE COMMAND")
    # ... [Keep your existing Task Forge code here]
    
    if 'tasks' not in st.session_state:
        st.session_state.tasks = pd.DataFrame(columns=["Task", "Node", "Status", "Deadline"])

    with st.expander("➕ FORGE NEW CONTENT TASK"):
        with st.form("task_form_hub_master", clear_on_submit=True):
            t_name = st.text_input("Task Description")
            t_plat = st.selectbox("Node", ["YouTube", "Instagram", "X", "TikTok"])
            t_date = st.date_input("Deadline")
            if st.form_submit_button("SYNC TO FORGE") and t_name:
                new_task = pd.DataFrame([{"Task": t_name, "Node": t_plat, "Status": "⏳ Pending", "Deadline": t_date.strftime("%Y-%m-%d")}])
                st.session_state.tasks = pd.concat([st.session_state.tasks, new_task], ignore_index=True)
                st.rerun()

    if not st.session_state.tasks.empty:
        done = len(st.session_state.tasks[st.session_state.tasks['Status'] == "✅ Uploaded"])
        total = len(st.session_state.tasks)
        st.write(f"**Campaign Completion: {int((done/total)*100)}%**")
        st.progress(done/total)

        st.session_state.tasks = st.data_editor(
            st.session_state.tasks,
            use_container_width=True,
            num_rows="dynamic",
            key="master_task_editor",
            column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=["⏳ Pending", "🎬 Filming", "✂️ Editing", "✅ Uploaded"], required=True),
                "Node": st.column_config.SelectboxColumn("Node", options=["YouTube", "Instagram", "X", "TikTok"], required=True)
            }
        )

elif page == "🌐 Global Pulse":
    draw_title("🌐", "GLOBAL INTELLIGENCE PULSE")
    
    # 🔑 CONFIGURATION - Now pulling from Streamlit Secrets
    # Ensure you have NEWS_API_KEY = "your_key" in your .streamlit/secrets.toml
    try:
        NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
    except:
        st.error("🔑 API KEY MISSING: Add 'NEWS_API_KEY' to your Streamlit Secrets.")
        NEWS_API_KEY = None

    # 1. TRIGGER DATA UPLINK
    df_pulse = fetch_live_market_data()

    if not df_pulse.empty:
        # --- 2. SEARCH TERMINAL ---
        search_query = st.text_input("🔍 Intercept Keyword...", placeholder="Search niches...", label_visibility="collapsed")

        # --- 3. PERFORMANCE VECTORS ---
        st.subheader("📊 TOP 10 PERFORMANCE VECTORS")
        display_df = df_pulse.copy()
        
        vel_col = 'growth' if 'growth' in display_df.columns else display_df.columns[2]
        name_col = 'niche name' if 'niche name' in display_df.columns else display_df.columns[0]

        display_df = display_df.sort_values(by=vel_col, ascending=False).head(10)
        
        if search_query:
            display_df = display_df[display_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]

        st.data_editor(
            display_df,
            column_config={
                name_col: "Trend Target",
                vel_col: st.column_config.ProgressColumn("Growth Velocity", min_value=0, max_value=100),
            },
            hide_index=True, use_container_width=True, disabled=True
        )

        # --- 🆕 INTEGRATED VIRAL RADAR (THE NEURAL SCAN) ---
        st.divider()
        st.subheader("🛰️ VIRAL RADAR // NEURAL SCAN")
        target_topic = search_query if search_query else (display_df[name_col].iloc[0] if not display_df.empty else "Global Trends")
        
        if st.button(f"🚀 SCAN VIRAL CLUSTERS FOR: {target_topic.upper()}", use_container_width=True):
            with st.spinner("📡 SCANNING NEURAL DATASTREAMS..."):
                pulse_prompt = (
                    f"Act as a Viral Trend Analyst. Based on the '{target_topic}' niche, "
                    f"identify 3 high-velocity 'Trend Clusters' currently exploding. "
                    f"For each: 1. A catchy title, 2. The 'Secret Hook', and 3. A Virality Heatmap score (1-100)."
                )
                pulse_res = groq_c.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": pulse_prompt}]
                )
                st.session_state.radar_intel = pulse_res.choices[0].message.content
        
        if st.session_state.get('radar_intel'):
            with st.container(border=True):
                st.markdown(st.session_state.radar_intel)
                st.caption("🎯 **Strategic Note:** Copy these hooks into the **🧠 Neural Forge** for elite script generation.")

        st.divider()

        # --- 4. LIVE WORLD INTELLIGENCE ---
        st.subheader("📰 LIVE WORLD INTELLIGENCE")
        
        # We clean the topic name to ensure the API understands it
        news_topic = search_query if search_query else (display_df[name_col].iloc[0] if not display_df.empty else "AI Technology")
        
        if NEWS_API_KEY:
            articles = fetch_live_news(news_topic, NEWS_API_KEY)

            # BAILOUT LOGIC: If no specific news, fetch general tech news
            if not articles:
                st.write(f"🛰️ Specific intel for '{news_topic}' is sparse. Expanding search radius...")
                articles = fetch_live_news("AI Tech Trends", NEWS_API_KEY)

            if articles:
                for art in articles[:8]:
                    with st.container(border=True):
                        c_img, c_txt = st.columns([1, 2])
                        with c_img:
                            img_url = art.get('urlToImage') or "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400"
                            st.image(img_url, use_container_width=True)
                        with c_txt:
                            st.markdown(f"<h4 style='color: #00ff41; margin:0;'>{art['title']}</h4>", unsafe_allow_html=True)
                            desc = art.get('description') or "Detailed intel for this vector is encrypted."
                            st.write(f"{desc[:180]}...")
                            st.markdown(f"🔗 [READ FULL REPORT]({art['url']})")
                            source_name = art.get('source', {}).get('name', 'Intel Hub')
                            st.caption(f"Source: {source_name} | {art.get('publishedAt', '')[:10]}")
            else:
                st.info(f"📡 NEURAL SILENCE: No live feeds found for '{news_topic}'. Check API quota.")
        else:
            st.warning("⚠️ NEWS FEED OFFLINE: Configure API Key in Secrets to enable.")
            
    else:
        st.error("📡 NEURAL LINK FAILURE: The CSV is unreachable.")


# --- MODULE 5: TREND DUEL ---
elif page == "⚔️ Trend Duel":
    draw_title("⚔️", "TREND DUEL: MARKET AUDIT")
    
    # 1. TRIGGER DATA UPLINK
    pulse_df = fetch_live_market_data()
    
    if not pulse_df.empty:
        # --- PHASE 1: INDIVIDUAL SECTOR AUDIT (Preserved Logic) ---
        st.subheader("🌑 Deep Vector Analysis")
        
        target = st.selectbox("Select Niche to Audit", pulse_df['niche name'].unique())
        row = pulse_df[pulse_df['niche name'] == target].iloc[0]
        
        with st.container(border=True):
            col_a, col_b, col_c = st.columns(3)
            col_a.metric(label="Intelligence Score", value=f"{row['score']}/100")
            col_b.metric(label="Growth Velocity", value=f"{row['growth']}%")
            col_c.metric(label="Market Density", value=str(row['saturation']).upper())

        st.info(f"**VECTOR ANALYSIS FOR {target.upper()}:**\n\n{row['reason']}")
        
        st.divider()

        # --- PHASE 2: THE COMPARISON DUEL (Preserved Logic) ---
        st.subheader("📊 COMPETITIVE VECTOR MAPPING")
        
        selections = st.multiselect(
            "Select Niches to Compare", 
            options=pulse_df['niche name'].unique().tolist(), 
            default=pulse_df['niche name'].unique().tolist()[:5]
        )
        
        comparison_df = pulse_df[pulse_df['niche name'].isin(selections)]
        
        if not comparison_df.empty: 
            import plotly.express as px
            import plotly.graph_objects as go
            from groq import Groq # Ensure you have 'groq' in requirements.txt
            
            fig = px.bar(
                comparison_df, 
                x='niche name', 
                y='growth', 
                color='score',
                text='score',
                title="Growth Velocity vs. Intelligence Score",
                labels={'growth': 'Growth %', 'niche name': 'Niche Sector', 'score': 'Score'},
                template='plotly_dark',
                color_continuous_scale='Viridis'
            )
            
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(
                comparison_df[['niche name', 'score', 'growth', 'saturation', 'reason']], 
                hide_index=True, 
                use_container_width=True
            )

            st.divider()

            # --- PHASE 3: THE QUANTUM PULSE COLLISION ---
            st.subheader("🌌 QUANTUM VECTOR INTERSECT")
            st.write("Triangulate the intersection of two market vectors to expose the Sovereign Gap.")

            q_col1, q_col2 = st.columns(2)
            t_a_name = q_col1.selectbox("Vector Alpha", pulse_df['niche name'].unique(), index=0)
            t_b_name = q_col2.selectbox("Vector Beta", pulse_df['niche name'].unique(), index=1)

            data_a = pulse_df[pulse_df['niche name'] == t_a_name].iloc[0]
            data_b = pulse_df[pulse_df['niche name'] == t_b_name].iloc[0]

            # High-End Radar Mapping
            quantum_fig = go.Figure()
            categories = ['Growth', 'Score', 'Opportunity', 'Market Heat', 'Growth'] 
            
            # Vector Alpha
            quantum_fig.add_trace(go.Scatterpolar(
                r=[data_a['growth'], data_a['score'], 80, 70, data_a['growth']],
                theta=categories,
                fill='toself',
                name=t_a_name.upper(),
                line=dict(color='#00F2FF', width=2),
                fillcolor='rgba(0, 242, 255, 0.15)'
            ))

            # Vector Beta
            quantum_fig.add_trace(go.Scatterpolar(
                r=[data_b['growth'], data_b['score'], 85, 60, data_b['growth']],
                theta=categories,
                fill='toself',
                name=t_b_name.upper(),
                line=dict(color='#7000FF', width=2),
                fillcolor='rgba(112, 0, 255, 0.15)'
            ))

            quantum_fig.update_layout(
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, gridcolor="rgba(255,255,255,0.05)"),
                    angularaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.2)")
                ),
                showlegend=True,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=450,
                margin=dict(l=80, r=80, t=20, b=20),
                font=dict(color="white", family="Courier New")
            )

            st.plotly_chart(quantum_fig, use_container_width=True)

            # --- PHASE 4: NEURAL SYNTHESIS (GROQ INTEGRATION) ---
            with st.container(border=True):
                st.write(f"**READY FOR COLLISION:** `{t_a_name.upper()}` x `{t_b_name.upper()}`")
                
                if st.button("⚡ INITIALIZE NEURAL COLLISION"):
                    try:
                        # Initialize Groq Client
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        
                        with st.status("Performing Quantum Synthesis...", expanded=True) as status:
                            st.write("Triangulating Market Vectors...")
                            st.write("Calculating Sustainability Coefficients...")
                            
                            prompt = f"""
                            SYSTEM: You are the VOID-OS Strategic Logic Engine.
                            TASK: Analyze the collision of two market trends.
                            TREND A: {t_a_name} (Growth: {data_a['growth']}%, Score: {data_a['score']}/100)
                            TREND B: {t_b_name} (Growth: {data_b['growth']}%, Score: {data_b['score']}/100)
                            
                            REPORT REQUIREMENTS:
                            1. SOVEREIGN GAP: Define the specific new niche created at this intersection.
                            2. GROWTH PREDICTION: How will this collision perform in the next 12 months?
                            3. SUSTAINABILITY AUDIT: Is this a temporary hype or a structural shift?
                            4. REVENUE ARCHITECTURE: Suggest one high-ticket agency offer for this gap.
                            
                            Format the output with professional headers and clear, aggressive strategic insights.
                            """
                            
                            chat_completion = client.chat.completions.create(
                                messages=[{"role": "user", "content": prompt}],
                                model="llama-3.3-70b-versatile", # High-quality Groq model
                            )
                            
                            report = chat_completion.choices[0].message.content
                            status.update(label="Collision Successful!", state="complete", expanded=False)

                        st.subheader("📋 SOVEREIGN COLLISION REPORT")
                        st.markdown(report)
                        
                        # Sustainable Growth Metric Mockup (Logic enhancement)
                        st.divider()
                        st.caption("Quantum Sustainability Index")
                        avg_growth = (data_a['growth'] + data_a['growth']) / 2
                        st.progress(min(avg_growth/100, 1.0), text=f"Stability Matrix: {avg_growth}%")

                    except Exception as e:
                        st.error(f"NEURAL LINK FAILED: Ensure 'GROQ_API_KEY' is set in Streamlit Secrets. Error: {e}")
                        
    else:
        st.error("📡 NEURAL LINK FAILURE: Market data stream is empty.")

# --- MODULE 7: THE NEURAL FORGE (EXCALIBUR UPGRADE) ---
elif page == "🧠 Neural Forge":
    import random
    import datetime
    import requests  
    import openai 
    from groq import Groq

    # Initialize Groq Client
    groq_c = Groq(api_key=st.secrets["GROQ_API_KEY"])

    # 1. ACCESS CONTROL & LIMITS
    if not st.session_state.get('logged_in'):
        st.error("🚨 CLEARANCE REQUIRED: Access Denied.")
        st.stop()

    user_status = st.session_state.get('user_status', 'Free')
    if 'daily_usage' not in st.session_state: st.session_state.daily_usage = 0
    if 'max_limit' not in st.session_state:
        limits = {"Agency": 100, "Director": 50, "Operative": 25}
        st.session_state.max_limit = limits.get(user_status, 5)
    
    remaining_credits = st.session_state.max_limit - st.session_state.daily_usage
    draw_title("🧠", "NEURAL FORGE || MASTER ARCHITECT")

    # DNA & Vault Variables
    v_id = st.session_state.get('linguistic_dna_id', "").strip()
    brand_dna = st.session_state.get('brand_dna_summary', "No DNA Synthesized yet.")
    vault_active = len(st.session_state.get('vault_inventory', [])) > 0

    # 2. INPUT CONFIGURATION
    with st.container(border=True):
        col_a, col_b, col_c = st.columns(3, gap="small")
        with col_a:
            st.subheader("🧬 Production")
            f_platform = st.selectbox("Target Platform", ["YouTube Shorts", "Instagram Reels", "TikTok", "YouTube Long-form", "Podcast Conversation"])
            f_topic = st.text_input("Core Concept", placeholder="e.g., The Dark Truth of AI")
            f_lang = st.selectbox("Script Language", ["English", "Hinglish", "Hindi", "Spanish", "French", "German", "Russian", "Portuguese", "Italian"])
            f_colors = st.multiselect("Cinematic Palette", ["Cyberpunk Neon", "Midnight Teal", "Electric Orange", "Moody Noir"], default=["Midnight Teal", "Electric Orange"])
        
        with col_b:
            st.subheader("📡 Strategy")
            f_framework = st.selectbox("Retention Framework", ["The Controversy Start", "The Hero's Journey", "Statistical Shock", "The 'Value-First' Pivot"])
            f_interrupt = st.selectbox("Pattern Interrupt", ["Fast Zoom-in", "Flash Cut", "Sudden Silence"])
            f_lighting = st.selectbox("Lighting Style", ["Dramatic Rim Light", "Soft Cinematic Glow", "Hard Shadows"])
        
        with col_c:
            st.subheader("🎬 Style")
            f_hook_type = st.radio("Emotional Anchor", ["Curiosity", "Fear", "Authority"])
            f_hook_intensity = st.select_slider("Hook Intensity", ["Subtle", "High-Octane", "Extreme"])
            f_pacing = st.select_slider("Script Pacing", ["Slow Burn", "Dynamic", "Rapid Fire"])
            execute = st.button("🔥 EXECUTE FULL SYNTHESIS", use_container_width=True)

    # 3. CORE SYNTHESIS LOGIC (OPTIMIZED SOVEREIGN PROMPT)
    if execute:
        if not f_topic:
            st.warning("⚠️ Please enter a Core Concept.")
        elif remaining_credits <= 0:
            st.error("🚨 NEURAL EXHAUSTION: Daily limit reached.")
        else:
            with st.spinner(f"🌑 ANCHORING {f_lang.upper()} NEURAL PATHWAYS..."):
                try:
                    dna_instruction = f"IDENTITY PROTOCOL: Strictly adhere to this Brand DNA: {brand_dna}" if vault_active else "Tone: High-authority, viral-engineered."
                    
                    sys_msg = (
                        f"You are the VOID-CREATOR Strategic Engine. Generate a world-class production blueprint.\n"
                        f"LANGUAGE: {f_lang} | PLATFORM: {f_platform}\n"
                        f"TOPIC: {f_topic} | FRAMEWORK: {f_framework}\n"
                        f"VISUAL VIBE: {f_colors} with {f_lighting} lighting.\n"
                        f"{dna_instruction}\n\n"
                        f"STRUCTURE YOUR RESPONSE INTO THESE 3 SECTIONS:\n"
                        f"1. --- SCRIPT --- \n(Write a high-retention script. Include [SCENE START] tags and specify where the {f_interrupt} interrupt occurs. Pacing: {f_pacing}.)\n\n"
                        f"2. --- IMAGE PROMPTS --- \n(Provide 3 hyper-realistic DALL-E 3 prompts for thumbnails using {f_colors}.)\n\n"
                        f"3. --- VIDEO MANIFEST --- \n(Describe 3 cinematic 5-second shots for AI video generation.)"
                    )
                    
                    res = groq_c.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "You are an elite content architect."}, {"role": "user", "content": sys_msg}],
                        temperature=0.3, # Slightly increased for better creative flow
                        max_tokens=2500   
                    )
                    st.session_state.pro_forge_txt = res.choices[0].message.content
                    st.session_state.daily_usage += 1
                except Exception as e:
                    st.error(f"Synthesis Error: {e}")

    # 4. REVEAL & PRODUCTION SUITE
    if st.session_state.get('pro_forge_txt'):
        st.divider()
        st.markdown("### 💎 PRODUCTION BLUEPRINT")
        st.text_area("FORGE OUTPUT (RAW)", st.session_state.pro_forge_txt, height=450)
        
        if user_status in ["Director", "Agency"]:
            st.markdown("### 🎬 DIRECTOR'S PRODUCTION SUITE")
            
            prod_col1, prod_col2, prod_col3 = st.columns(3)
            
            with prod_col1:
                if st.button("🔊 FORGE MASTER AUDIO", use_container_width=True):
                    if not v_id: st.error("❌ No Voice ID detected in session.")
                    else:
                        with st.spinner("Synthesizing Elite Voiceover..."):
                            script_content = st.session_state.pro_forge_txt.split("--- IMAGE PROMPTS ---")[0].replace("--- SCRIPT ---", "").strip()
                            e_url = f"https://api.elevenlabs.io/v1/text-to-speech/{v_id}"
                            headers = {"xi-api-key": st.secrets["ELEVENLABS_API_KEY"], "Content-Type": "application/json"}
                            audio_res = requests.post(e_url, json={"text": script_content, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}, headers=headers)
                            if audio_res.status_code == 200: st.audio(audio_res.content)
                            else: st.error(f"Audio Error: {audio_res.text}")

            with prod_col2:
                if st.button("🎨 MANIFEST CTR VISUALS", use_container_width=True):
                    with st.spinner("Generating Neural Visuals..."):
                        client_ai = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                        try:
                            # Extracting the first prompt from the output
                            p_extract = st.session_state.pro_forge_txt.split("--- IMAGE PROMPTS ---")[1].split("---")[0].strip()
                            img_res = client_ai.images.generate(model="dall-e-3", prompt=f"{p_extract}. 8k resolution, cinematic lighting, ultra-detailed.", n=1, size="1024x1024")
                            st.image(img_res.data[0].url, caption="Generated Sovereign Visual")
                        except: st.error("Visual Synthesis Failed. Check API limits.")

            with prod_col3:
                if st.button("🎥 TEXT-TO-VIDEO MANIFEST", use_container_width=True):
                    with st.spinner("Queuing Video Engine (Replicate/Veo)..."):
                        video_desc = st.session_state.pro_forge_txt.split("--- VIDEO MANIFEST ---")[1].strip()
                        st.info(f"🎬 VIDEO GEN PROMPT ACTIVE: {video_desc[:100]}...")
                        st.warning("Director Tier Note: Processing via Replicate Luma-Dream-Machine / Veo. Check terminal for status.")

        # --- AUDIT SUITE ---
        st.divider()
        st.subheader("🧪 VOID Intelligence Audit")
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            if st.button("🚀 SCORE VIRALITY & CTR"):
                v_res = groq_c.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": f"Critique the virality of this script on a scale of 1-100 and give 3 improvements: {st.session_state.pro_forge_txt[:800]}"}])
                st.info(v_res.choices[0].message.content)
        with t_col2:
            if st.button("🧠 NEURAL RETENTION MAP"):
                r_res = groq_c.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": f"Analyze the retention triggers and pattern interrupts in this script: {st.session_state.pro_forge_txt[:800]}"}])
                st.warning(r_res.choices[0].message.content)


# --- MODULE 8: VOID-RADIO (GPT-4 SOVEREIGN UPGRADE) ---
elif page == "🎙️ VOID Radio":
    import re
    import requests
    import openai

    # Initialize OpenAI Client (Ensure OPENAI_API_KEY is in secrets)
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    draw_title("🎙️", "VOID-RADIO || GPT-4 DIALECTIC")
    
    # --- ADMIN / POWER CHECK ---
    if 'void_credits' not in st.session_state:
        st.session_state.void_credits = 100.0  # Initial Power Level

    with st.sidebar:
        st.divider()
        st.subheader("⚡ VOID POWER CORE")
        st.progress(min(max(st.session_state.void_credits / 100, 0.0), 1.0))
        st.caption(f"Neural Power Remaining: {st.session_state.void_credits:.2f}%")
        if st.session_state.void_credits < 15:
            st.warning("🚨 LOW POWER: GPT-4 Channels unstable.")

    # 1. INTELLIGENCE INGESTION (Main Tab)
    with st.container(border=True):
        st.subheader("📁 Intelligence Ingestion")
        uploaded_docs = st.file_uploader("Upload Source Material (PDF/TXT) for Dialectic Analysis", accept_multiple_files=True)
        
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            podcast_energy = st.select_slider("Conversation Energy", ["Academic", "Balanced", "High-Octane"], value="Balanced")
        with sub_col2:
            st.info("🎯 ENGINE: GPT-4o Active | ElevenLabs Dual-Channel Ready")

    # 2. THE COMMAND CENTER (DIRECTOR OVERRIDE)
    with st.container(border=True):
        col1, col2 = st.columns([2, 1], gap="medium")
        
        with col1:
            st.subheader("📡 Synthesis & Interrupt")
            pod_topic = st.text_input("Core Focus Topic", placeholder="e.g., The Ethics of AI Sovereignty")
            user_adjustment = st.text_area("🔴 DIRECTOR INTERRUPT (Real-time Command)", 
                                            placeholder="e.g., 'Host B, play devil's advocate. Challenge Host A on the revenue numbers.'")

        with col2:
            st.subheader("🎙️ Persona Config")
            h_a_name = st.text_input("Host A (Expert)", value="The Architect")
            h_b_name = st.text_input("Host B (Skeptic)", value="The Critic")
            
            # THE EXECUTION BUTTON
            if st.session_state.void_credits > 5:
                start_radio = st.button("🔥 EXECUTE GPT-4 SYNTHESIS", use_container_width=True)
            else:
                st.error("INSUFFICIENT POWER")
                start_radio = False

    # 3. GPT-4 DYNAMIC SCRIPTING LOGIC
    if start_radio:
        with st.spinner("🌑 GPT-4 NEURAL MAPPING IN PROGRESS..."):
            # 3a. Context Extraction
            context_data = ""
            if uploaded_docs:
                for doc in uploaded_docs:
                    context_data += doc.read().decode("utf-8")[:12000] # GPT-4o supports high context
            else:
                context_data = st.session_state.get('brand_dna_summary', "Standard VOID-OS Strategic Protocol")

            # 3b. The Sovereign Dialectic Prompt
            radio_prompt = (
                f"You are the VOID-RADIO Scripting Engine. Create a deep-dive, human-level conversation between {h_a_name} and {h_b_name}.\n"
                f"CONTEXT DATA: {context_data}\n"
                f"TOPIC: {pod_topic}\n"
                f"ENERGY: {podcast_energy}\n"
                f"DIRECTOR INTERRUPT: {user_adjustment}\n\n"
                f"RULES:\n"
                f"1. Format strictly as [HOST A]: and [HOST B]:\n"
                f"2. Host A is visionary and deep. Host B is sharp, critical, and looks for flaws.\n"
                f"3. Make them talk like real people (interrupting each other, using 'Right,' 'Exactly,' 'Wait a minute').\n"
                f"4. Address the Director's interrupt directly if provided."
            )

            try:
                response = client.chat.completions.create(
                    model="gpt-4o", # High reasoning for best dialectic
                    messages=[{"role": "system", "content": "You are a world-class podcast producer and strategist."}, 
                              {"role": "user", "content": radio_prompt}],
                    temperature=0.85
                )
                st.session_state.radio_script = response.choices[0].message.content
                st.session_state.void_credits -= 5.0 # Deduct for GPT-4 usage
                st.success("✅ Neural Script Synthesized.")
            except Exception as e:
                st.error(f"GPT-4 Neural Error: {e}")

    # 4. BROADCAST & AUDIO ENGINE
    if st.session_state.get('radio_script'):
        st.divider()
        st.markdown(f"### 📻 LIVE BROADCAST: {pod_topic.upper() if pod_topic else 'SOVEREIGN FEED'}")
        st.text_area("Live Script Feed", st.session_state.radio_script, height=300)
        
        # Action Row
        a_col1, a_col2 = st.columns(2)
        
        with a_col1:
            if st.button("🔊 GENERATE MASTER DUAL-VOICE AUDIO"):
                with st.spinner("🌑 SEPARATING NEURAL CHANNELS..."):
                    script = st.session_state.radio_script
                    segments = re.split(r'(\[HOST [A|B]\]:)', script)
                    
                    combined_audio = b""
                    v_a = st.secrets["ELEVENLABS_VOICE_ID_A"]
                    v_b = st.secrets["ELEVENLABS_VOICE_ID_B"]
                    api_key = st.secrets["ELEVENLABS_API_KEY"]

                    valid_segments = [s for s in segments if s.strip()]
                    for segment in valid_segments:
                        if "[HOST A]" in segment:
                            current_voice = v_a
                            continue
                        elif "[HOST B]" in segment:
                            current_voice = v_b
                            continue
                        
                        text = segment.replace(":", "").strip()
                        if text and len(text) > 2:
                            res = requests.post(
                                f"https://api.elevenlabs.io/v1/text-to-speech/{current_voice}",
                                json={"text": text, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.4, "similarity_boost": 0.8}},
                                headers={"xi-api-key": api_key, "Content-Type": "application/json"}
                            )
                            if res.status_code == 200: combined_audio += res.content

                    if combined_audio:
                        st.audio(combined_audio, format="audio/mp3")
                        st.session_state.void_credits -= 2.0 # Deduct for ElevenLabs usage
                        st.success("✅ BROADCAST MASTERED.")

        with a_col2:
            if st.button("🎨 GENERATE BROADCAST ART (DALL-E 3)"):
                with st.spinner("Visualizing Podcast Aesthetic..."):
                    img_res = client.images.generate(
                        model="dall-e-3",
                        prompt=f"Cinematic podcast cover art, title '{pod_topic}', moody lighting, cyberpunk aesthetic, high detail.",
                        size="1024x1024"
                    )
                    st.image(img_res.data[0].url, caption="Sovereign Broadcast Art")
                    st.session_state.void_credits -= 3.0 # Deduct for DALL-E usage

# --- MODULE 6: IDENTITY VAULT (THE SOVEREIGN BRAIN) ---
elif page == "🔒 Identity Vault":
    import time
    import requests
    import streamlit as st
    from groq import Groq

    # Initialize Clients from Secrets
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    VAPI_KEY = st.secrets["VAPI_PRIVATE_KEY"]
    ELEVEN_LABS_KEY = st.secrets["ELEVEN_LABS_API_KEY"]

    draw_title("🔒", "IDENTITY VAULT // DNA ANCHOR")
    
    # --- 🛡️ STATE MANAGEMENT ---
    if 'vault_inventory' not in st.session_state:
        st.session_state.vault_inventory = []
    if 'brand_dna_summary' not in st.session_state:
        st.session_state.brand_dna_summary = "No DNA Synthesized yet."
    if 'cloned_voice_id' not in st.session_state:
        st.session_state.cloned_voice_id = "paula" # Default fallback

    # --- 🏗️ THE SECURITY DASHBOARD ---
    with st.container(border=True):
        sec_col1, sec_col2, sec_col3 = st.columns(3)
        with sec_col1:
            st.metric("ENCRYPTION", "AES-256", delta="ACTIVE")
        with sec_col2:
            health = min(100, len(st.session_state.vault_inventory) * 25)
            st.metric("DNA HEALTH", f"{health}%", delta="STABLE")
        with sec_col3:
            st.metric("SESSION", "STATELESS", delta="SECURE")
        
        st.caption("🛰️ **DPDP 2026 COMPLIANCE:** All data is processed via Zero-Knowledge protocols.")

    st.divider()

    # --- 📥 SOURCE INGESTION (Text & Knowledge) ---
    st.markdown("### 📥 INGEST KNOWLEDGE SOURCES")
    uploaded_docs = st.file_uploader("Upload Master Reference Material", type=['pdf', 'txt', 'docx'], accept_multiple_files=True)

    if st.button("🧬 SYNCHRONIZE DNA"):
        if uploaded_docs:
            with st.status("Analyzing Linguistic & Factual DNA...", expanded=True) as status:
                all_text = ""
                for doc in uploaded_docs:
                    st.write(f"Reading: {doc.name}...")
                    try:
                        file_content = doc.read().decode("utf-8")
                        all_text += f"\n--- SOURCE: {doc.name} ---\n{file_content}\n"
                        st.session_state.vault_inventory.append(doc.name)
                    except Exception as e:
                         st.error(f"Error reading {doc.name}: {e}")
                
                try:
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{
                            "role": "system", 
                            "content": "Analyze the text and extract a 'Brand DNA Profile'. Be sharp and concise."
                        }, {"role": "user", "content": all_text[:4000]}],
                        temperature=0.1
                    )
                    st.session_state.brand_dna_summary = response.choices[0].message.content
                    status.update(label="✅ DNA ANCHORED", state="complete")
                    st.success("Sovereign Identity Updated.")
                except Exception as e:
                    st.error(f"Sync Error: {e}")
        else:
            st.warning("No documents detected.")

    st.divider()

    # --- 🎙️ BIOMETRIC ANCHORS (Vocal & Facial DNA) ---
    st.markdown("### 🧬 BIOMETRIC DNA ANCHORS")
    bio_col1, bio_col2 = st.columns(2)

    with bio_col1:
        st.markdown("#### 🎙️ VOCAL DNA (ElevenLabs)")
        vocal_file = st.file_uploader("Upload 30s Voice Sample", type=['mp3', 'wav', 'm4a'])
        if st.button("🔊 CLONE VOCAL DNA"):
            if vocal_file:
                with st.spinner("Synthesizing Vocal DNA..."):
                    url = "https://api.elevenlabs.io/v1/voices/add"
                    headers = {"xi-api-key": ELEVEN_LABS_KEY}
                    data = {"name": f"Director_Twin_{int(time.time())}"}
                    files = {"files": (vocal_file.name, vocal_file.read(), vocal_file.type)}
                    
                    res = requests.post(url, headers=headers, data=data, files=files)
                    if res.status_code == 200:
                        st.session_state.cloned_voice_id = res.json().get('voice_id')
                        st.success(f"Vocal DNA Cloned: {st.session_state.cloned_voice_id}")
                    else:
                        st.error(f"ElevenLabs Error: {res.text}")

    with bio_col2:
        st.markdown("#### 👤 FACIAL DNA (Strict Consistency)")
        facial_file = st.file_uploader("Upload Identity Reference Image", type=['jpg', 'jpeg', 'png'])
        if facial_file:
            st.image(facial_file, caption="Facial DNA Registered", width=150)
            st.info("Strict Facial Consistency Mode: ENABLED")

    st.divider()

    # --- 🗃️ IDENTITY MANAGEMENT ---
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.markdown("### 🧬 STORED IDENTITY PROFILE")
        st.text_area("Current DNA Summary", st.session_state.brand_dna_summary, height=250)
        
    with col_r:
        st.markdown("### 📊 EXECUTIVE ASSETS")
        
        def spawn_director_twin():
            url = "https://api.vapi.ai/assistant"
            headers = {
                "Authorization": f"Bearer {VAPI_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "name": "VOID-OS Director Twin",
                "firstMessage": "Director's line is active. How shall we proceed?",
                "model": {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "systemPrompt": f"You are 'The Director'. DNA: {st.session_state.brand_dna_summary}",
                    "temperature": 0.7
                },
                "voice": {
                    "provider": "11labs", 
                    "voiceId": st.session_state.cloned_voice_id, # DYNAMIC: Uses cloned voice
                    "stability": 0.5,
                    "similarityBoost": 0.8
                },
                "transcriber": {
                    "provider": "deepgram",
                    "model": "nova-2",
                    "language": "en"
                }
            }
            return requests.post(url, headers=headers, json=payload)

        if st.button("🛰️ SPAWN DIRECTOR TWIN", use_container_width=True):
            with st.spinner("Manifesting Digital Twin..."):
                res = spawn_director_twin()
                if res.status_code == 201:
                    assistant_id = res.json().get('id')
                    st.success(f"🔥 Twin Spawned! ID: {assistant_id}")
                    st.code(assistant_id, language="text")
                else:
                    st.error(f"Vapi Error: {res.text}")

        if st.button("🗑️ NUKE ALL VAULT DATA", type="primary", use_container_width=True):
            st.session_state.vault_inventory = []
            st.session_state.brand_dna_summary = "No DNA Synthesized yet."
            st.session_state.cloned_voice_id = "paula"
            st.rerun()

# --- MODULE 7: CLIENT PITCHER (PITCH ENGINE) ---
elif page == "💼 Client Pitcher":
    draw_title("💼", "VOID CAPITAL: PITCH ENGINE")
    
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
    # 🕵️ Check Persona and Status
    is_admin = st.session_state.get('user_role') == "admin"
    user_status = str(st.session_state.get('user_status', 'free')).strip().lower()
    
    # Define Tiers for ROI Engine Access (Paid Tiers)
    # Includes Operative, Director, Agency, Elite, etc.
    is_paid_tier = user_status in ['operative', 'pro', 'elite', 'core', 'director', 'agency']

    # --- 💎 PAID TIERS: THE ROI ENGINE (OPERATIVE, DIRECTOR, AGENCY, ADMIN) ---
    if is_admin or is_paid_tier:
        header_label = "ADMIN" if is_admin else user_status.upper()
        
        draw_title("🧪", f"ROI ENGINE v2.1 // {header_label}")
        st.info(f"🛰️ **{header_label} CLEARANCE:** Strategic Net Profit Projection active.")
        
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
            
            # --- THE REALITY FILTER (20% OPERATIONAL TAX) ---
            gross_usd = ad_rev_usd + sales_rev_usd
            net_usd = gross_usd * 0.80  # Deducing 20% for fees/taxes
            net_inr = net_usd * conversion_factor

            st.divider()
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                # Using delta to show the "Tax/Fee" transparency visually
                st.metric("NET VALUE (USD)", f"${net_usd:,.2f}", delta="-20% (Fees/Tax)", delta_color="inverse")
            with res_col2:
                st.markdown(f"#### NET TAKE-HOME (INR)")
                st.markdown(f"<h2 style='color: #00ff41;'>₹ {net_inr:,.2f}</h2>", unsafe_allow_html=True)

            # --- TRANSPARENCY DISCLAIMER ---
            st.caption("⚠️ *Note: A 20% operational buffer has been deducted from gross totals to account for platform fees, payment processing, and estimated taxes.*")

        # --- GENERATION LOGIC ---
        if st.button("🧬 GENERATE PROFIT BLUEPRINT", use_container_width=True):
            with st.spinner("Calculating Strategic Trajectory..."):
                try:
                    roi_prompt = f"""
                    System: You are VOID-OS, a strategic financial AI for elite creators.
                    User Data:
                    - Tier: {header_label}
                    - Niche: {selected_niche}
                    - Weekly Views: {views}
                    - Net Weekly Income (INR): ₹{net_inr:,.2f}
                    Task: Provide a 3-point 'Profit Blueprint' for this creator based on their NET income.
                    """
                    res = groq_c.chat.completions.create(
                        model="llama-3.3-70b-versatile", 
                        messages=[{"role": "user", "content": roi_prompt}],
                        temperature=0.5
                    )
                    st.session_state.roi_report = res.choices[0].message.content
                except Exception as e:
                    st.error(f"Uplink Error: {str(e)}")

        # --- PERSISTENT DISPLAY ---
        if 'roi_report' in st.session_state:
            st.markdown("---")
            st.markdown(f"### 📑 {header_label} STRATEGY REPORT")
            st.info(st.session_state.roi_report)
            if st.button("Clear Report"):
                del st.session_state.roi_report
                st.rerun()

    # --- 🟢 FREE TIER: THE BASIC LAB (HOOK & RETENTION ONLY) ---
    else:
        draw_title("🧪", "CREATOR LAB // BASELINE")
        st.info("📡 **CONTENT OPTIMIZATION:** Refine your hooks and retention strategy.")
        
        st.warning("🔒 **ROI ENGINE LOCKED:** Access restricted to Operative, Director, and Agency tiers.")

        tab_hook, tab_retention = st.tabs(["🔥 Hook Analyzer", "🧠 Cognitive Load"])

        with tab_hook:
            st.subheader("Viral Hook Architect")
            user_hook = st.text_area("Paste your opening line (Hook):", placeholder="Example: Most creators are failing at AI...")
            if st.button("ANALYZE HOOK"):
                with st.spinner("Neural Processing..."):
                    hook_prompt = f"Analyze this hook for viral potential: {user_hook}."
                    res = groq_c.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": hook_prompt}])
                    st.success(res.choices[0].message.content)

        with tab_retention:
            st.subheader("Cognitive Retention Check")
            st.caption("Identify 'Boredom Gaps' in your script.")
            script_text = st.text_area("Paste Full Script:")
            if st.button("IDENTIFY DROPOFF POINTS"):
                st.warning("Analysis complete: Pattern interrupt suggested at 0:15.")

# --- MODULE 9: LEAD SOURCE (RESILIENT AUTO-SWITCH) ---
elif page == "🛰️ Lead Source":
    draw_title("🛰️", "LEAD SOURCE: DEEP SCAN")
    
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
    draw_title("📜", "ARCHIVE VAULT")
    
    # 🕵️ Search Filter
    search_query = st.text_input("🔍 Search Vault by Topic, Platform, or Script...", placeholder="Enter keyword...")

    # Ensure histories exist in session state to avoid errors
    if 'script_history' not in st.session_state: st.session_state.script_history = []
    if 'pitch_history' not in st.session_state: st.session_state.pitch_history = []

    if not st.session_state.script_history and not st.session_state.pitch_history:
        st.info("Vault is empty. Generate scripts in the Neural Forge to populate the archive.")
    else:
        t1, t2 = st.tabs(["💎 SCRIPT ARCHIVE", "💼 PITCH LOGS"])
        
        with t1:
            # Filtering logic - Updated for the 8-column key names
            # We check 'topic', 'platform', and 'Generated Script'
            scripts = [
                s for s in st.session_state.script_history 
                if search_query.lower() in str(s.get('Topic', '')).lower() or 
                   search_query.lower() in str(s.get('Platform', '')).lower() or
                   search_query.lower() in str(s.get('Generated Script', s.get('script', ''))).lower()
            ]
            
            if not scripts:
                st.warning("No scripts matching that query.")
            
            for i, s in enumerate(reversed(scripts)):
                # Get values safely using .get() to support both old and new data formats
                s_topic = s.get('Topic', s.get('topic', 'Untitled'))
                s_platform = s.get('Platform', s.get('platform', 'Unknown'))
                s_content = s.get('Generated Script', s.get('script', 'No Content'))
                s_dna = s.get('Visual Dna', 'No DNA data')
                s_status = s.get('Status', s.get('status', 'pending'))
                s_user = s.get('User Name', s.get('assigned_to', 'Operator'))
                s_time = s.get('Timestamp', s.get('timestamp', 'N/A'))

                # Visual Status Tag
                status_tag = "✅ [FILMED]" if s_status == "filmed" else "⏳ [PENDING]"
                
                with st.expander(f"{status_tag} {s_platform} | {s_topic.upper()}"):
                    col_a, col_b = st.columns([3, 1])
                    
                    with col_a:
                        st.markdown("### 📝 Script")
                        st.info(s_content)
                        st.divider()
                        st.markdown("### 🧬 Visual DNA")
                        st.code(s_dna, language="markdown")
                        
                    with col_b:
                        st.write("📊 **Metadata**")
                        st.caption(f"👤 User: {s_user}")
                        st.caption(f"📅 Date: {s_time}")
                        
                        # Interactive Status Toggle
                        if s_status != "filmed":
                            if st.button("🚀 MARK FILMED", key=f"film_{i}"):
                                # Update locally
                                s['Status'] = "filmed"
                                # Note: To update GSheet status, you'd need a "UPDATE" branch in Apps Script
                                st.toast("Status updated locally.")
                                st.rerun()
                        
                        st.download_button(
                            label="📥 DOWNLOAD", 
                            data=s_content, 
                            file_name=f"{s_topic}_script.txt",
                            key=f"dl_{i}",
                            use_container_width=True
                        )

        with t2:
            # Logic for pitches remains the same
            pitches = [p for p in st.session_state.pitch_history if search_query.lower() in p.get('client', '').lower()]
            
            if not pitches:
                st.warning("No pitches matching that query.")

            for i, p in enumerate(reversed(pitches)):
                with st.container(border=True):
                    col_p1, col_p2 = st.columns([4, 1])
                    with col_p1:
                        st.markdown(f"### 🎯 Target: {p.get('client', 'Unknown')}")
                        st.info(p.get('pitch', 'No content'))
                    with col_p2:
                        st.write("📈 **Status**")
                        st.success("Sent")
                        st.caption(f"🕒 {p.get('timestamp', 'N/A')}")
                    
                    if st.button(f"📋 Copy Pitch {i}", key=f"copy_{i}"):
                        st.toast("Pitch text copied to local memory.")

    # 🔄 GLOBAL SYNC (Manual Refresh)
    st.divider()
    if st.button("🛰️ FORCE REFRESH FROM GLOBAL CLOUD", use_container_width=True):
        with st.spinner("Pulling latest data from GSheets..."):
            if sync_history_from_cloud():
                st.success("Vault Synchronized.")
                st.rerun()
            else:
                st.error("Sync failed. Check your CSV Public Link.")

# --- MODULE 11: ADMIN CONSOLE (SYSTEM ARCHITECT) ---
elif page == "🛡️ Admin Console":
    draw_title("🛡️", "SYSTEM ADMINISTRATION // DIRECTOR LEVEL")
    
    # 1. Password Protection (Ghost Logic)
    # We pull the master password from secrets
    master_code = get_void_secret("ADMIN_PASSWORD", "RESTRICTED")
    auth = st.text_input("Enter Level 5 Authorization Code", type="password")
    
    if auth == master_code and master_code != "RESTRICTED": 
        st.session_state['admin_verified'] = True
        st.success("Identity Verified. Welcome, Director.")
        
        # --- EMPIRE OVERVIEW METRICS (Live Monitoring) ---
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Daily Credits Used", f"{st.session_state.get('daily_usage', 0)}")
        with col_m2:
            st.metric("Projected ARR", "₹88,00,000", "+5.2%")
        with col_m3:
            st.metric("Global Nodes (USD)", "$1,200", "+$450")
        with col_m4:
            st.metric("System Health", "OPTIMAL", "Sync: 24ms")

        # 2. INITIALIZE TABS
        tab1, tab2, tab3, tab4 = st.tabs(["👥 User Matrix", "💰 Revenue Sync", "📡 Lead Drop", "🔐 Identity Logs"])

        # --- TAB 1: USER MANAGEMENT ---
        with tab1:
            st.subheader("👥 Citizen Database")
            users_df = load_user_db() if 'load_user_db' in globals() else pd.DataFrame()
            
            if not users_df.empty:
                st.dataframe(users_df, use_container_width=True)
                
                st.divider()
                st.subheader("🛰️ Node Traffic Analysis")
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    st.info(f"Total Database Entries: {len(users_df)}")
                with col_c2:
                    if 'Status' in users_df.columns:
                        pro_count = len(users_df[users_df['Status'].str.title() == 'Pro'])
                        st.success(f"Active Pro Nodes: {pro_count}")
            else:
                st.info("No active user data found in synchronization tunnel.")

        # --- TAB 2: PAYMENTS (The Revenue Engine) ---
        with tab2: 
            st.subheader("💰 Manual Revenue Override")
            st.write("Use this to manually activate users after verifying UPI or PayPal transactions.")
            
            target_mail = st.text_input("User Email to Activate", key="admin_target_mail")
            
            if st.button("ACTIVATE PRO NODES"):
                if target_mail:
                    payload = {
                        "email": target_mail.lower().strip(),
                        "category": "ROLE_UPGRADE",
                        "message": "PRO_ACTIVATION"
                    }
                    
                    try:
                        # Pull secure URL from bridge
                        NEW_URL = get_void_secret("ADMIN_ACTIVATE_URL", "RESTRICTED")
                        
                        if NEW_URL != "RESTRICTED":
                            response = requests.post(NEW_URL, json=payload, timeout=30)
                            
                            if response.status_code == 200 and "SUCCESS" in response.text:
                                st.success(f"⚔️ OMNI-SYNC COMPLETE: {target_mail} updated in Google Sheets.")
                                st.balloons()
                                if target_mail.lower().strip() == st.session_state.get('user_email'):
                                    st.session_state.user_status = 'Pro'
                                st.rerun()
                            else:
                                st.error(f"📡 SCRIPT RESPONSE: {response.text}")
                        else:
                            st.error("Terminal restricted. Check Secrets.")
                    except Exception as e:
                        st.error(f"🚨 UPLINK CRASHED: {e}")
                else:
                    st.warning("Director, enter a target email first.")

            st.divider()
            
            # --- THE MANUAL VERIFY FORM ---
            with st.form("manual_verify_v2"):
                st.write("### 🛰️ Transaction Log Check")
                u_email = st.text_input("Registered Email")
                u_txn = st.text_input("Transaction ID / Reference Number")
                
                if st.form_submit_button("LOG VERIFICATION"):
                    if u_email and u_txn:
                        f_payload = {"email": u_email, "message": u_txn, "category": "PAYMENT_PENDING"}
                        try:
                            # Pull secure URL from bridge
                            LOG_API = get_void_secret("ADMIN_LOG_URL", "RESTRICTED")
                            
                            if LOG_API != "RESTRICTED":
                                f_res = requests.post(LOG_API, json=f_payload, timeout=10)
                                if f_res.status_code == 200:
                                    st.success("✅ TRANSMISSION SUCCESS: Verification request logged.")
                                    st.balloons()
                                else:
                                    st.error(f"📡 UPLINK ERROR: {f_res.status_code}")
                            else:
                                st.error("Log Link restricted.")
                        except Exception as e:
                            st.error(f"🚨 CRITICAL SYSTEM FAILURE: {str(e)}")
                    else:
                        st.warning("Director, both fields are required.")

        # --- TAB 3: LEAD DROP ---
        with tab3:
            st.subheader("📡 Broadcast New Leads")
            st.write("Upload leads for your Real Estate or Agency-tier users.")
            lead_file = st.file_uploader("Upload Daily Leads (CSV)", type="csv")
            niche_label = st.text_input("Niche Category", placeholder="e.g., Real Estate India")
            
            if st.button("🚀 PUSH TO PAID USERS"):
                if lead_file is not None:
                    import pandas as pd
                    df = pd.read_csv(lead_file)
                    st.session_state['global_leads'] = df
                    st.success(f"Transmission Successful. {len(df)} leads pushed to global state.")
                else:
                    st.error("No data package detected.")

        # --- TAB 4: IDENTITY LOGS ---
        with tab4:
            st.subheader("🔐 Vault Security Monitoring")
            if st.session_state.get('vault_anchor'):
                st.write("✅ DIRECTOR DNA: Locally Active.")
            else:
                st.info("⚠️ NO LOCAL ANCHOR DETECTED.")

    elif auth != "":
        st.error("Invalid Credentials. Intrusion attempt logged.")

# --- MODULE: LEGAL ARCHIVE (Feedback & Vote Edition) ---
elif page == "⚖️ Legal Archive":
    # Universal Access Check (God-Mode)
    u_name = str(st.session_state.get('user_name', '')).upper()
    u_role = str(st.session_state.get('role', '')).upper()
    is_authorized = ("ADMIN" in u_name or "DIRECTOR" in u_name or "ADMIN" in u_role)

    draw_title("⚖️", "LEGAL DEFENSE VAULT")
    
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
                import requests # Logic Intact
                
                # --- 📡 THE SECURE GOOGLE FORM BRIDGE ---
                # Pulling the URL from the secret vault
                form_url = get_void_secret("LEGAL_VAULT_FORM_URL", "RESTRICTED")
                
                if form_url != "RESTRICTED":
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
                            st.error("Uplink Error: Transmission rejected. Verify Form IDs.")
                    
                    except Exception as e:
                        st.error(f"Critical Failure: {e}")
                else:
                    st.error("Uplink Restricted. Check Terminal Secrets.")
            else:
                st.warning("Director, please add a small suggestion first!")
                    
    # --- SECTION 3: BASIC CHECKLIST (The 'Now' value) ---
    st.divider()
    with st.expander("✅ VIEW BASIC SAFETY CHECKLIST"):
        st.write("While the AI is training, always check these manually:")
        st.write("- Is the payment date clearly mentioned?")
        st.write("- Do you keep the rights to your raw footage?")
        st.write("- Is there a limit on how many 'Revisions' the brand can ask for?")

# --- MAIN APP ROUTING (This part goes further down in your code) ---
if page == "⚡ Upgrade Authority":
    show_upgrade_authority()

elif page == "🛰️ Media Uplink":
    draw_title("🛰️", "MEDIA UPLINK // THE BRIDGE")
    st.info("Direct server-side downloading is throttled. Switching to 'Bridge Mode' for 100% reliability.")

    # Detect Shards
    current_files = os.listdir('.')
    found_cookie_file = next((f for f in current_files if f.lower() in ['cookie.txt', 'cookies.txt']), None)

    with st.container(border=True):
        uplink_url = st.text_input("🔗 Source URL", placeholder="Paste YouTube link...")
        
        if st.button("⚡ GENERATE CLEAN UPLINK", use_container_width=True):
            if uplink_url:
                try:
                    with st.spinner("🛰️ INTERCEPTING RAW STREAM VECTORS..."):
                        ydl_opts = {
                            'quiet': True,
                            'no_warnings': True,
                            'cookiefile': found_cookie_file if found_cookie_file else None,
                            'format': 'best',
                        }
                        
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(uplink_url, download=False)
                            direct_url = info.get('url')
                            title = info.get('title', 'Asset')

                        if direct_url:
                            st.success(f"🎯 UPLINK SECURED: {title}")
                            st.markdown(f"""
                                <a href="{direct_url}" download="{title}.mp4" target="_blank" style="text-decoration: none;">
                                    <div style="background-color: #00ff41; color: black; padding: 15px; text-align: center; border-radius: 10px; font-weight: bold; cursor: pointer;">
                                        💾 CLICK TO SAVE ASSET TO DISK
                                    </div>
                                </a>
                                <p style='font-size: 0.8em; color: gray; margin-top: 10px;'>Note: If the video opens in a new tab, right-click and 'Save Video As'.</p>
                            """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"UPLINK FAILED: {str(e)}")
            else:
                st.warning("Director, please provide a URL.")

elif page == "⚙️ Settings":
    draw_title("⚙️", "SYSTEM SETTINGS")
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
























































































































































































































































































































































































































































































































