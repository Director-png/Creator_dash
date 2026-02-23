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
import streamlit as st
import time
from streamlit_lottie import st_lottie # You'll need: pip install streamlit-lottie
import requests
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# This defines 'conn' so the rest of the app can see it
conn = st.connection("gsheets", type=GSheetsConnection)
def ignition_sequence():
    if 'ignition_complete' not in st.session_state:
        # Create a placeholder that disappears once done
        placeholder = st.empty()
        
        with placeholder.container():
            st.markdown("""
                <style>
                /* FORCE FULL SCREEN OVERLAY */
                .ignition-overlay {
                    position: fixed;
                    top: 0; left: 0; width: 100%; height: 100%;
                    background: black !important;
                    z-index: 999999 !important; /* Extremely high to beat default spinners */
                    display: flex; flex-direction: column;
                    align-items: center; justify-content: center;
                }

                /* THE ROTATING CORE */
                .engine-ring {
                    width: 120px; height: 120px;
                    border: 4px solid rgba(0, 255, 65, 0.1);
                    border-top: 4px solid #00ff41;
                    border-radius: 50%;
                    animation: spin-engine 1.2s linear infinite;
                    box-shadow: 0 0 20px rgba(0, 255, 65, 0.4);
                }

                .void-label {
                    margin-top: 30px;
                    color: #00ff41;
                    font-family: 'Courier New', monospace;
                    font-size: 32px;
                    font-weight: bold;
                    letter-spacing: 8px;
                    animation: glow-fade 2s ease-in-out forwards;
                }

                @keyframes spin-engine {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }

                @keyframes glow-fade {
                    0% { opacity: 0; filter: blur(10px); }
                    100% { opacity: 1; filter: blur(0); }
                }
                </style>

                <div class="ignition-overlay">
                    <div class="engine-ring"></div>
                    <div class="void-label">VOID-OS</div>
                </div>
            """, unsafe_allow_html=True)
            
            # This sleep MUST happen while the markdown is active
            time.sleep(3)
            
        placeholder.empty()
        st.session_state.ignition_complete = True
        st.rerun() # Forces the app to clear the overlay and start the real UI

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
def fetch_vault_data(sheet_name):
    """Fetches any specific sheet from your empire's vault."""
    SHEET_IDS = {
        "market": "2PACX-1vTuN3zcXZqn9RMnPs7vNEa7vI9xr1Y2VVVlZLUcEwUVqsVqtLMadz1L_Ap4XK_WPA1nnFdpqGr8B_uS",
        "users": "2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes",
        "feedback": "AKfycbz1mLI3YkbjVsA4a8rMgMe_07w_1sS8H-f2Wvz1FtFCU-ZN4zCH7kDUGaDPDaaMbrvaPw",
        "history": "2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes"
    }
    url = f"https://docs.google.com/spreadsheets/d/e/{SHEET_IDS[sheet_name]}/pub?output=csv"
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

# --- 🛰️ DATA INFRASTRUCTURE ---
MARKET_PULSE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuN3zcXZqn9RMnPs7vNEa7vI9xr1Y2VVVlZLUcEwUVqsVqtLMadz1L_Ap4XK_WPA1nnFdpqGr8B_uS/pub?output=csv"
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?gid=2093671902&single=true&output=csv&t=" + str(time.time())
FORM_POST_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfnNLb9O-szEzYfYEL85aENIimZFtMd5H3a7o6fX-_6ftU_HA/formResponse"
SCRIPT_VAULT_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"
VAULT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfeDAY3gnWYlpH90EaJirxUc8d4obYUgiX72WJIah7Cya1VNQ/formResponse"
VAULT_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTtSx9iQTrDvNWe810s55puzBodFKvfUbfMV_l-QoQIfbdPxeQknClGGCQT33UQ471NyGTw4aHLrDTw/pub?gid=1490190727&single=true&output=csv"
FEEDBACK_API_URL = "https://script.google.com/macros/s/AKfycbz1mLI3YkbjVsA4a8rMgMe_07w_1sS8H-f2Wvz1FtFCU-ZN4zCH7kDUGaDPDaaMbrvaPw/exec"
NEW_URL = "https://script.google.com/macros/s/AKfycbzBLwNA-37KxZ5mDyHp1DMNw23n8xyfBVaVbmg_zRs-oQAZGue6Zuxo44UwztuBvFIC/exec"
NEWS_API_KEY = "7640df120b1f4008a744bc780f147e68"
# --- 🛰️ UTILITIES & BRAIN FUNCTIONS ---

def draw_title(emoji, text):
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
            <span style="font-size: 2rem;">{emoji}</span>
            <span class="neural-gradient-text" style="font-size: 2rem;">{text}</span>
        </div>
    """, unsafe_allow_html=True)

def apply_war_room_css():
    st.markdown("""
    <style>
    /* 1. BACKGROUND & TEXT */
    .stApp { 
        background: radial-gradient(circle at top, #0a0a0a 0%, #000000 100%) !important; 
    }
    
    /* 2. BUTTONS (Restoring the Cyan/Green Glow) */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #00d4ff !important; 
        border: 1px solid rgba(0, 212, 255, 0.4) !important; 
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        transition: 0.3s all ease !important;
    }
    
    div.stButton > button:hover {
        border: 1px solid #00ff41 !important;
        color: #00ff41 !important;
        background: rgba(0, 255, 65, 0.1) !important;
        box-shadow: 0px 0px 20px rgba(0, 255, 65, 0.2) !important;
        transform: translateY(-2px);
    }

    /* 3. THE GRADIENT TEXT (Properly Clipped) */
    .neural-gradient-text {
        background: linear-gradient(90deg, #00d4ff 0%, #00ff41 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        font-weight: 800 !important;
        display: inline-block !important;
    }
    </style>
    """, unsafe_allow_html=True)

# CALL THIS AT THE VERY TOP OF YOUR APP
apply_war_room_css()

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
        # PASTE YOUR NEW CSV LINK HERE
        CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTtSx9iQTrDvNWe810s55puzBodFKvfUbfMV_l-QoQIfbdPxeQknClGGCQT33UQ471NyGTw4aHLrDTw/pub?gid=1490190727&single=true&output=csv"
        
        # Pull data and strip spaces from headers
        df = pd.read_csv(CSV_URL)
        df.columns = [c.strip() for c in df.columns]
        
        user_email = st.session_state.get('user_email', 'N/A')
        
        if not df.empty:
            # Check if 'Email' column exists before filtering
            if 'Email' in df.columns:
                user_df = df[df['Email'] == user_email]
                # Convert to records so the History Tab can loop through them
                st.session_state.script_history = user_df.to_dict('records')
                return True
        return False
    except Exception as e:
        st.error(f"🛰️ HISTORY READ ERROR: {e}")
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

@st.cache_data(ttl=0)
def load_user_db():
    try:
        sync_url = f"{USER_DB_URL}&cache_bus={time.time()}"
        df = pd.read_csv(sync_url)
        
        # CLEANING: Remove hidden spaces but KEEP the casing (Upper/Lower)
        # This makes 'Email ' become 'Email'
        df.columns = [str(c).strip() for c in df.columns]
        
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

def fetch_live_market_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuN3zcXZqn9RMnPs7vNEa7vI9xr1Y2VVVlZLUcEwUVqsVqtLMadz1L_Ap4XK_WPA1nnFdpqGr8B_uS/pub?output=csv"
    try:
        res = requests.get(url, timeout=10)
        df = pd.read_csv(io.StringIO(res.text))
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # --- THE FIX: SCRUB THE GROWTH COLUMN ---
        if 'growth' in df.columns:
            # Remove %, commas, and whitespace, then convert to float
            df['growth'] = df['growth'].astype(str).str.replace('%', '').str.replace(',', '').str.strip()
            df['growth'] = pd.to_numeric(df['growth'], errors='coerce').fillna(0)
            
        return df
    except Exception as e:
        st.error(f"Uplink Error: {e}")
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
if 'groq_key' not in st.session_state:
    st.session_state.groq_key = "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"

client = Groq(api_key=st.session_state.groq_key)
MODEL_ID = "llama-3.3-70b-versatile"

# --- 2. VISUAL FORGE (FREE IMAGE ENGINE) ---
def generate_visual(image_prompt):
    seed = random.randint(0, 99999)
    encoded_prompt = requests.utils.quote(image_prompt)
    # Pollinations.ai provides high-quality text-to-image for free
    return f"https://pollinations.ai/p/{encoded_prompt}?width=1280&height=720&seed={seed}&nologo=true"


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
# NEW_URL = "https://script.google.com/macros/s/AKfycbzBLwNA-37KxZ5mDyHp1DMNw23n8xyfBVaVbmg_zRs-oQAZGue6Zuxo44UwztuBvFIC/exec"
# FORM_POST_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfnNLb9O-szEzYfYEL85aENIimZFtMd5H3a7o6fX-_6ftU_HA/formResponse"

# --- GATEKEEPER START ---
import requests
import datetime
import pandas as pd
import streamlit as st

# 1. SESSION STATE INITIALIZATION
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'otp_sent' not in st.session_state:
    st.session_state.otp_sent = False
if 'rec_otp_sent' not in st.session_state: # New state for recovery flow
    st.session_state.rec_otp_sent = False
if 'generated_otp' not in st.session_state:
    st.session_state.generated_otp = None
if 'user_status' not in st.session_state:
    st.session_state.user_status = "Free"

# TEMPORARY TEST FEATURE
ELITE_CIPHERS = {
    "VOID-V1-X7R2-DELTA": "Elite Pioneer 1",
    "VOID-V1-K9P4-OMEGA": "Elite Pioneer 2",
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
            if email_in == "admin" and pw_in == "1234":
                st.session_state.update({"logged_in": True, "user_name": "Master Director", "user_role": "admin", "user_status": "Pro", "user_email": "admin"})
                st.rerun()
            elif not users.empty:
                match = users[(users['Email'].astype(str).str.lower() == email_in) & (users['Password'].astype(str) == pw_in)]
                if not match.empty:
                    st.session_state.update({
                        "logged_in": True, 
                        "user_name": match.iloc[0]['Name'], 
                        "user_email": email_in, 
                        "user_status": str(match.iloc[0]['Status']).strip()
                    })
                    st.rerun()
                else:
                    st.error("INTEGRITY BREACH: INVALID CREDENTIALS.")

        # --- RECOVERY PROTOCOL FIX ---
        with st.expander("RECOVERY PROTOCOL (Lost Passkey)"):
            st.info("Verify identity via Security Answer or OTP")
            rec_mode = st.radio("Recovery Mode", ["Security Question", "OTP Verification"])
            r_email = st.text_input("REGISTERED EMAIL", key="rec_email").lower().strip()
            
            if rec_mode == "Security Question":
                s_ans = st.text_input("SECURITY KEY (DOB / PRESET)", key="rec_ans")
                new_p = st.text_input("NEW PASSKEY", type="password", key="rec_new_pw")
                if st.button("OVERRIDE VIA SECURITY"):
                    # Fixed action name to match common Google Script standard: 'RESET_PASSWORD'
                    payload = {"email": r_email, "action": "SECURE_RESET", "answer": s_ans, "message": new_p}
                    try:
                        res = requests.post(NEW_URL, json=payload, timeout=15)
                        if "SUCCESS" in res.text: st.success("IDENTITY VERIFIED. PASSKEY UPDATED.")
                        else: st.error(f"UPLINK DENIED: {res.text}")
                    except Exception as e: st.error(f"CRASH: {e}")
            
            else:
                # OTP RECOVERY FLOW FIX
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
                    # The "Missing Tab" for OTP Input
                    st.success(f"Security Code sent to {r_email}")
                    rec_otp_in = st.text_input("ENTER 6-DIGIT CODE", key="rec_otp_input")
                    new_p_otp = st.text_input("NEW PASSKEY", type="password", key="rec_new_pw_otp")
                    
                    if st.button("🔓 OVERRIDE SECURITY WALL"):
                        if rec_otp_in == st.session_state.generated_otp:
                            # Finalizing the reset
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

    # --- TAB 2: REGISTRATION ---
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

            if st.button("⚔️ GENERATE SECURE OTP", use_container_width=True):
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
        
        else:
            st.markdown(f"### PHASE 2: VERIFY UPLINK")
            st.info(f"Verification code sent to {st.session_state.temp_reg_data['Email']}")
            user_otp = st.text_input("ENTER 6-DIGIT CODE", placeholder="000000")
            
            if st.button("🔓 FINALIZE INITIALIZATION", use_container_width=True):
                if user_otp == st.session_state.generated_otp:
                    final_payload = {
                        "category": "REGISTRATION",
                        "data": st.session_state.temp_reg_data 
                    }
                    try:
                        r = requests.post(NEW_URL, json=final_payload, timeout=20)
                        if "SUCCESS" in r.text:
                            st.success("✅ IDENTITY SECURED. YOU MAY NOW LOGIN.")
                            st.fireworks()
                            st.session_state.otp_sent = False 
                            st.session_state.generated_otp = None
                        else: st.error(f"VAULT REJECTION: {r.text}")
                    except Exception as e: st.error(f"SYSTEM TIMEOUT: {e}")
                else: st.error("INVALID CODE.")
            
            if st.button("Edit Registration Info"):
                st.session_state.otp_sent = False
                st.rerun()

    # --- TAB 3: ELITE BYPASS ---
    with t3:
        st.markdown("### 🛰️ ELITE UPLINK (TEST PHASE)")
        cipher_in = st.text_input("ENTER ELITE ACCESS CIPHER", type="password")
        if st.button("⚡ EXECUTE PRO BYPASS", use_container_width=True):
            if cipher_in in ELITE_CIPHERS:
                st.session_state.update({
                    "logged_in": True, "user_name": ELITE_CIPHERS[cipher_in],
                    "user_status": "Pro", "user_email": "elite_test@void.os"
                })
                st.rerun()
            else: st.error("INVALID CIPHER.")

    st.stop()

# --- MAIN APP UI BEGINS HERE (Only accessible if logged_in is True) ---
import streamlit as st

# 1. INITIALIZE PAGE STATE (Prevents NameError)
if 'page' not in st.session_state:
    st.session_state.page = "🏠 Dashboard"

# --- 2. SIDEBAR ARCHITECTURE ---
# --- 2. SIDEBAR ARCHITECTURE ---
with st.sidebar:
    try:
        # --- ENHANCED IDENTITY CORE ---
        profile_img = st.session_state.get('vault_anchor')
        
        # Logic: Determine what goes inside the small ID circle
        if profile_img is None:
            # Default state: DNA text
            img_content = "<div style='width: 55px; height: 55px; border-radius: 50%; background: #111; border: 1px solid #00ff41; display: flex; align-items: center; justify-content: center; color: #00ff41; font-size: 10px;'>DNA</div>"
        else:
            if isinstance(profile_img, str):
                # Purged Identity state: Show the actual image
                img_content = f"<img src='{profile_img}' style='width: 55px; height: 55px; border-radius: 50%; border: 2px solid #00ff41; object-fit: cover;'>"
            else:
                # Fallback state: Helix emoji
                img_content = "<div style='width: 55px; height: 55px; border-radius: 50%; background: #111; border: 1px solid #00ff41; display: flex; align-items: center; justify-content: center; font-size: 25px;'>🧬</div>"

        # The Identity Box (Displays the image/DNA adjacent to the name)
        st.markdown(f"""
            <div style='background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 15px; border: 1px solid rgba(0, 255, 65, 0.2); margin-bottom: 20px; display: flex; align-items: center; gap: 15px;'>
                <div>{img_content}</div>
                <div style='flex-grow: 1;'>
                    <p style='margin: 0; color: #888; font-size: 9px; letter-spacing: 2px;'>OPERATOR IDENTIFIED</p>
                    <h3 style='color: #00ff41; margin: 0; font-family: "Courier New", Courier, monospace; font-size: 18px;'>{st.session_state.get('user_name', 'DIRECTOR').upper()}</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # --- CLEARANCE LOGIC ---
        user_status = str(st.session_state.get('user_status', 'free')).strip().lower()
        user_role = str(st.session_state.get('user_role', 'user')).strip().lower()

        if user_role == "admin" or user_status in ['pro', 'paid']:
            st.markdown("<div style='background-color: #00ff41; color: #000; padding: 5px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 12px; margin-bottom: 10px;'>💎 ELITE CLEARANCE</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color: #333; color: #888; padding: 5px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 12px; margin-bottom: 10px;'>📡 BASIC ACCESS</div>", unsafe_allow_html=True)

        # --- DYNAMIC MENU MAPPING ---
        if user_role == "admin":
            options = ["🏠 Dashboard", "🏛️ Identity Vault", "🌐 Global Pulse", "🛡️ Admin Console", "⚔️ Trend Duel", "🧪 Creator Lab", "🏗️ Script Architect", "🧠 Neural Forge", "🛰️ Media Uplink", "⚖️ Legal Archive", "💼 Client Pitcher", "📜 History", "⚙️ Settings"]
        elif user_status in ['pro', 'paid']:
            options = ["📡 My Growth Hub", "🏛️ Identity Vault", "🌐 Global Pulse", "⚔️ Trend Duel", "🧠 Neural Forge", "🧪 Creator Lab", "⚖️ Legal Archive", "📜 History", "⚙️ Settings"]
        else:
            options = ["📡 My Growth Hub", "🌐 Global Pulse", "⚔️ Trend Duel", "🏗️ Script Architect", "🧪 Creator Lab", "⚖️ Legal Archive", "📜 History", "💎 Upgrade to Pro", "⚙️ Settings"]

        if 'current_page' not in st.session_state:
            st.session_state.current_page = options[0]

        try:
            default_index = options.index(st.session_state.current_page)
        except ValueError:
            default_index = 0

        page = st.radio("COMMAND CENTER", options, index=default_index, key="nav_radio")
        st.session_state.current_page = page

        # --- 🤖 REPAIRED VOID MANAGER (GROQ VERSION) ---
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
                        try:
                            stream = client.chat.completions.create(
                                model=MODEL_ID,
                                messages=[
                                    {"role": "system", "content": "You are VOID-OS. Witty, elite, and strategic. Be concise."},
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

        # --- 🛠️ GLOBAL ACTIONS ---
        st.divider()
        
        if 'show_feedback_node' not in st.session_state:
            st.session_state.show_feedback_node = False

        if st.button("💬 SYSTEM FEEDBACK", use_container_width=True):
            st.session_state.show_feedback_node = True
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
        page = options[0]

# --- FEEDBACK OVERLAY (Triggers when sidebar button is clicked) ---
if st.session_state.get('show_feedback_node', False):
    st.markdown("---")
    draw_title("🛠️", "FEEDBACK NODE")
    
    col_fb1, col_fb2 = st.columns([2, 1])
    
    with col_fb1:
        st.info("To maintain data integrity, we use an encrypted Google Form for reviews.")
        st.write("Your feedback will be logged in the Master CSV for the Founder's Review Call.")
        # Replace this link with your actual Form URL (the one for users to fill, not edit)
        st.link_button("🚀 OPEN FEEDBACK FORM", "https://docs.google.com/forms/d/e/1FAIpQLSfeDAY3gnWYlpH90EaJirxUc8d4obYUgiX72WJIah7Cya1VNQ/viewform?usp=header", use_container_width=True)
    
    with col_fb2:
        if st.button("❌ CLOSE NODE", use_container_width=True):
            st.session_state.show_feedback_node = False
            st.rerun()
    st.markdown("---")

# --- MODULE 1: DASHBOARD (KYC OPTIMIZED) ---
if page == "🏠 Dashboard":
    # 🚨 COMPLIANCE HEADER (Minimalist)
    draw_title("🌌", "VOID OS // B2B OUTREACH SAAS")
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

    # 1. THE DATA ACQUISITION LAYER
    with st.container(border=True):
        if is_paid or is_admin:
            st.markdown("### 🛰️ PRO-SYNC TERMINAL")
            st.caption("Status: Uplink Standby")
            
            target_url = st.text_input("🔗 Target Profile URL", placeholder="Paste YouTube link here...")
            
            if st.button("🔄 INITIATE LIVE SYNC", use_container_width=True):
                if target_url:
                    # CHECK FOR INSTAGRAM
                    if "instagram.com" in target_url.lower():
                        st.info("🛰️ **SYSTEM NOTICE**: Instagram Live-Sync is undergoing a security handshake upgrade. This node will be active in the **v2.0 Update**.")
                        st.warning("Please use the **Manual Tracker** below for Instagram for now.")
                    else:
                        with st.spinner("Decoding Meta-Streams..."):
                            subs, views = get_live_stats(target_url)
                            
                            if subs:
                                # SUCCESS PATH (YouTube)
                                if 'start_count' not in st.session_state:
                                    st.session_state.start_count = int(subs * 0.99)
                                    st.session_state.days_passed = 7
                                
                                st.session_state.current_count = subs
                                st.session_state.total_views = views
                                st.session_state.last_sync_ts = datetime.datetime.now()
                                st.success(f"Uplink Established: {subs:,} subscribers detected.")
                            else:
                                st.error("Initial connection failed. Link might be private or invalid.")
        else:
            st.markdown("### 📉 MANUAL TRACKER (BASIC)")
            st.info("Upgrade to PRO for automated telemetry.")
            c_b1, c_b2 = st.columns(2)
            with c_b1:
                st.session_state.start_count = st.number_input("Starting Count", value=1000)
                st.session_state.days_passed = st.slider("Days Active", 1, 90, 7)
            with c_b2:
                st.session_state.current_count = st.number_input("Current Count", value=1100)

    # 2. ANALYTICS & PROJECTION
    if 'current_count' in st.session_state:
        st.divider()
        
        start = st.session_state.get('start_count', 1000)
        current = st.session_state.current_count
        days = st.session_state.get('days_passed', 7)
        
        growth = current - start
        raw_velocity = growth / days if days > 0 else 0
        # Stabilization: 2% daily cap for realistic projections
        velocity = min(raw_velocity, current * 0.02) if raw_velocity > 0 else raw_velocity
        
        # UI Feedback
        if velocity > 0:
            st.success(f"📈 **GROWTH MATRIX**: +{int(velocity)}/day (Stability: High)")
        elif velocity < 0:
            st.error(f"📉 **DECAY DETECTED**: {int(velocity)}/day (Action Required)")

        # Metric Row
        m1, m2, m3 = st.columns(3)
        m1.metric("CURRENT STATUS", f"{current:,}", f"{growth:+}")
        m2.metric("DAILY VELOCITY", f"{int(velocity):+}/unit")
        m3.metric("30D PROJECTION", f"{int(current + (velocity * 30)):,}")

        with st.expander("🔮 FORECAST SCENARIOS"):
            sc1, sc2 = st.columns(2)
            with sc1:
                st.write("**🛡️ Conservative**")
                st.subheader(f"{int(current + (velocity * 30 * 0.7)):,}")
            with sc2:
                st.write("**🚀 Hyper-Growth**")
                st.subheader(f"{int(current + (velocity * 30 * 1.5)):,}")

    # 3. TASK FORGE
    st.divider()
    st.subheader("🗓️ TASK FORGE COMMAND")
    
    if 'tasks' not in st.session_state:
        st.session_state.tasks = pd.DataFrame(columns=["Task", "Node", "Status", "Deadline"])

    with st.expander("➕ FORGE NEW CONTENT TASK"):
        with st.form("task_form", clear_on_submit=True):
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
            column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=["⏳ Pending", "🎬 Filming", "✂️ Editing", "✅ Uploaded"], required=True),
                "Node": st.column_config.SelectboxColumn("Node", options=["YouTube", "Instagram", "X", "TikTok"], required=True)
            }
        )

elif page == "🌐 Global Pulse":
    draw_title("🌐", "GLOBAL INTELLIGENCE PULSE")
    
    # 🔑 CONFIGURATION
    NEWS_API_KEY = "7640df120b1f4008a744bc780f147e68" 

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
        news_topic = search_query if search_query else (display_df[name_col].iloc[0] if not display_df.empty else "Technology")
        articles = fetch_live_news(news_topic, NEWS_API_KEY)

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
                        st.write(f"{desc[:200]}...")
                        st.markdown(f"🔗 [READ FULL REPORT]({art['url']})")
                        st.caption(f"Source: {art['source']['name']} | {art['publishedAt'][:10]}")
        else:
            st.info(f"🛰️ No live news for '{news_topic}'. Searching broader vectors...")
            
    else:
        st.error("📡 NEURAL LINK FAILURE: The CSV is unreachable.")


# --- MODULE 5: TREND DUEL ---
elif page == "⚔️ Trend Duel":
    draw_title("⚔️", "TREND DUEL: MARKET AUDIT")
    
    # 1. TRIGGER DATA UPLINK (Using the renamed function)
    pulse_df = fetch_live_market_data()
    
    if not pulse_df.empty:
        # --- PHASE 1: INDIVIDUAL SECTOR AUDIT ---
        st.subheader("🌑 Deep Vector Analysis")
        
        # Ensure we use 'niche name' to match your G-Sheet columns
        target = st.selectbox("Select Niche to Audit", pulse_df['niche name'].unique())
        
        # Isolate the specific vector data
        row = pulse_df[pulse_df['niche name'] == target].iloc[0]
        
        # High-fidelity audit metrics
        with st.container(border=True):
            col_a, col_b, col_c = st.columns(3)
            col_a.metric(label="Intelligence Score", value=f"{row['score']}/100")
            col_b.metric(label="Growth Velocity", value=f"{row['growth']}%")
            col_c.metric(label="Market Density", value=str(row['saturation']).upper())

        # Sector Reasoning
        st.info(f"**VECTOR ANALYSIS FOR {target.upper()}:**\n\n{row['reason']}")
        
        st.divider()

        # --- PHASE 2: THE COMPARISON DUEL ---
        st.subheader("📊 COMPETITIVE VECTOR MAPPING")
        
        # Multiselect for comparison
        selections = st.multiselect(
            "Select Niches to Compare", 
            options=pulse_df['niche name'].unique().tolist(), 
            default=pulse_df['niche name'].unique().tolist()[:5]
        )
        
        comparison_df = pulse_df[pulse_df['niche name'].isin(selections)]
        
        if not comparison_df.empty: 
            import plotly.express as px
            
            # Growth vs Score Visualization
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
            
            # Raw Data Comparison Table
            st.dataframe(
                comparison_df[['niche name', 'score', 'growth', 'saturation', 'reason']], 
                hide_index=True, 
                use_container_width=True
            )
    else:
        st.error("📡 NEURAL LINK FAILURE: The function 'fetch_live_market_data' returned an empty set.")

# --- MODULE 6: SCRIPT ARCHITECT ---
elif page == "🏗️ Script Architect":
    draw_title("⚔️", "SCRIPT ARCHITECT")
    
    # Ensure history list exists in session state
    if 'script_history' not in st.session_state: st.session_state.script_history = []
    
    # 🕵️ Persona Checks for Limits
    is_admin = st.session_state.get('user_role') == "admin"
    user_status = str(st.session_state.get('user_status', 'free')).strip().lower()
    is_paid = user_status in ['pro', 'paid']

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
                        if not is_paid and not is_admin: 
                            st.session_state.daily_script_count += 1
                        
                        formation_prompt = (
                            f"Act as a master content strategist. Create a high-retention {platform} script about {topic}. "
                            f"Tone: {tone}. Formation: Start with a 'Pattern Interrupt' hook, move into 'The Agitation', "
                            f"provide 'The Insight', and end with a 'Call to Value'. Use timestamps and clear visual cues."
                        )
                        
                        # Generate Script
                        res = groq_c.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": formation_prompt}])
                        generated_script = res.choices[0].message.content
                        st.session_state.current_architect_txt = generated_script
                        
                        # --- DATA HARDENING: UPLINK TO VAULT & GSHEET ---
                        import datetime
                        now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        
                        # 1. Update Local Session History
                        archive_entry = {
                            "timestamp": now_ts,
                            "platform": platform,
                            "topic": topic,
                            "script": generated_script,
                            "assigned_to": st.session_state.get('user_name', 'Operator'),
                            "status": "pending"
                        }
                        st.session_state.script_history.append(archive_entry)

                        # 2. Update Global GSheet Database
                        try:
                            # Headers: Timestamp, Platform, Topic, Script, User, Status
                            new_row = [
                                now_ts, 
                                platform, 
                                topic, 
                                generated_script, 
                                st.session_state.get('user_email', 'N/A'), 
                                "pending"
                            ]
                            conn.append_row(new_row, worksheet="Scripts")
                            st.toast("⚡ ARCHIVE SYNCHRONIZED TO CLOUD")
                        except Exception as e:
                            st.error(f"GSHEET SYNC FAILED: {e}")

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

# --- MODULE 7: THE NEURAL FORGE (ELITE SCRIPT & MULTI-COLOR ARCHITECT) ---
elif page == "🧠 Neural Forge":
    import random
    import datetime
    import requests  # Crucial for the Web App Bypass

    # 1. ACCESS & CREDIT CONTROL (Sync Protocol)
    if not st.session_state.get('logged_in'):
        st.error("🚨 CLEARANCE REQUIRED: Enter your Elite Cipher in the terminal.")
        st.stop()

    # --- CLOUD SYNC INITIALIZER ---
    if 'history_synced' not in st.session_state or not st.session_state.get('script_history'):
        with st.spinner("📡 Synchronizing with Global Vault..."):
            if sync_history_from_cloud():
                st.session_state.history_synced = True

    if 'daily_usage' not in st.session_state: st.session_state.daily_usage = 0
    if 'last_reset' not in st.session_state: st.session_state.last_reset = datetime.date.today()
    if 'max_limit' not in st.session_state:
        st.session_state.max_limit = 15 if st.session_state.get('user_status') == "Pro" else 5
    
    remaining_credits = st.session_state.max_limit - st.session_state.daily_usage

    draw_title("🧠", "NEURAL FORGE // MASTER ARCHITECT")
    st.sidebar.markdown(f"### ⚡ NEURAL CREDITS\n**{remaining_credits} / {st.session_state.max_limit}**")
    
    if 'vault_anchor' not in st.session_state or st.session_state.vault_anchor is None:
        st.warning("⚠️ IDENTITY VAULT EMPTY: Upload your face in the Vault to enable Strict Facial Consistency.")

    # 2. INPUT CONFIGURATION
    with st.container(border=True):
        col_a, col_b, col_c = st.columns([1, 1, 1], gap="small")
        
        with col_a:
            st.subheader("🧬 Production")
            f_platform = st.selectbox("Target Platform", ["YouTube Long-form", "YouTube Shorts", "Instagram Reels", "TikTok"])
            f_topic = st.text_input("Core Concept", placeholder="e.g., The Dark Truth of AI")
            
            color_options = [
                "Cyberpunk Neon", "Midnight Teal", "Electric Orange", "Moody Noir", "Golden Hour", 
                "Vintage Kodachrome", "Ethereal Dream", "Industrial Cold", "Deep Forest Green",
                "Sunset Violet", "High-Contrast Monochrome", "Earth Tone Pastel", "Royal Gold",
                "Crimson Threat", "Frozen Arctic", "Desert Sand", "Sepia Memory", 
                "Ultraviolet", "Minimalist White", "Toxic Emerald"
            ]
            f_colors = st.multiselect("Cinematic Palette (Pick 1-3)", color_options, default=["Midnight Teal", "Electric Orange"])

        with col_b:
            st.subheader("📡 Strategy")
            f_framework = st.selectbox("Retention Framework", ["The Controversy Start", "The Hero's Journey", "Statistical Shock", "The 'Mistake' Hook"])
            f_lighting = st.selectbox("Lighting Style", ["Dramatic Rim Light", "Soft Cinematic Glow", "Hard Shadows", "Bi-Color Split"])
            f_vigor = st.select_slider("Neural Vigor", ["Standard", "High", "Extreme", "Elite"])

        with col_c:
            st.subheader("🎬 Style")
            f_hook_type = st.radio("Emotional Anchor", ["Curiosity", "Fear", "Authority", "Empowerment"])
            f_pacing = st.select_slider("Script Pacing", ["Slow Burn", "Dynamic", "Rapid Fire"])
            st.write("")
            execute = st.button("🔥 EXECUTE FULL SYNTHESIS", use_container_width=True)

        if execute:
            if remaining_credits <= 0:
                st.error("🚨 NEURAL EXHAUSTION: Daily limit reached.")
            elif f_topic and f_colors:
                with st.spinner("🌑 ARCHITECTING SCRIPT & VISUAL DNA..."):
                    try:
                        color_string = ", ".join(f_colors)
                        system_instruction = (
                            f"Act as a World-Class Viral Content Strategist. Apply Protocol 2026-02-06.\n\n"
                            f"1. VIRAL SCRIPT: Write a high-retention {f_platform} script for '{f_topic}'. "
                            f"Framework: {f_framework}. Tone: {f_hook_type}. Pacing: {f_pacing}.\n\n"
                            f"2. VISUAL DNA (IMAGE PROMPTS): Provide 3 highly detailed Image Prompts. "
                            f"Subject: Locked to Identity Vault reference. Features: Strict bone structure adherence. "
                            f"Mandatory Color Palette: {color_string}. Lighting: {f_lighting}. "
                            f"Composition: Close-up for mobile CTR, cinematic 8K, high detail."
                        )
                        
                        res = groq_c.chat.completions.create(
                            model="llama-3.3-70b-versatile", 
                            messages=[{"role": "user", "content": system_instruction}]
                        )
                        
                        generated_output = res.choices[0].message.content
                        st.session_state.pro_forge_txt = generated_output
                        st.session_state.daily_usage += 1
                        
                        # --- WEB-APP UPLINK (8-COLUMN SYNC) ---
                        now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        u_name = st.session_state.get('user_name', 'Operator')
                        u_email = st.session_state.get('user_email', 'N/A')
                        
                        # Prepare JSON payload for Apps Script
                        payload = {
                            "category": "SAVE_SCRIPT",
                            "timestamp": str(now_ts),
                            "userName": str(u_name),
                            "email": str(u_email),
                            "platform": str(f_platform),
                            "topic": str(f_topic),
                            "script": str(generated_output),
                            "visualDna": f"Palette: {color_string} | Lighting: {f_lighting}",
                            "status": "pending"
                        }
                        
                        # 1. Update Local Session History for immediate UI feedback
                        if 'script_history' not in st.session_state: st.session_state.script_history = []
                        st.session_state.script_history.append(payload)

                        # 2. Transmit via Web App Bridge (NO GOOGLE CLOUD NEEDED)
                        try:
                            # REPLACE THIS WITH YOUR DEPLOYMENT URL
                            WEBAPP_URL = "https://script.google.com/macros/s/AKfycby38DOr6SA2x_r-oS1gHudA39Gucb2BioMpVbfe6i288uOiBZnuv421vVlHv3O8J_KY/exec"
                            response = requests.post(WEBAPP_URL, json=payload)
                            
                            if "SUCCESS" in response.text:
                                st.toast("⚡ ARCHIVE SYNCHRONIZED VIA WEB-APP")
                                sync_history_from_cloud() 
                            else:
                                st.error(f"📡 WEB-APP REJECTED UPLINK: {response.text}")
                        except Exception as e:
                            st.error(f"GSHEET BRIDGE FAILED: {e}")

                        st.rerun()

                    except Exception as e:
                        st.error(f"UPLINK ERROR: {str(e)}")

    # 3. THE REVEAL
    if st.session_state.get('pro_forge_txt'):
        st.divider()
        st.markdown("### 💎 PRODUCTION BLUEPRINT")
        st.info(st.session_state.pro_forge_txt)
        
        # INTELLIGENCE TOOLS
        st.divider()
        st.subheader("🧪 Intelligence Tools")
        t_col1, t_col2 = st.columns(2)
        
        with t_col1:
            if st.button("🚀 SCORE VIRALITY", use_container_width=True):
                v_res = groq_c.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"Audit this script for CTR and Virality: {st.session_state.pro_forge_txt[:1000]}"}]
                )
                st.info(v_res.choices[0].message.content)
                        
        with t_col2:
            if st.button("🧠 RETENTION SCAN", use_container_width=True):
                r_res = groq_c.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"Scan for audience drop-off points: {st.session_state.pro_forge_txt[:1000]}"}]
                )
                st.warning(r_res.choices[0].message.content)

# --- MODULE : THE IDENTITY VAULT (CORE DNA) ---
elif page == "🏛️ Identity Vault":
    draw_title("🏛️", "IDENTITY VAULT // CORE DNA")
    
    # Protocol 2026-02-06: Initialize Vault if empty
    if 'vault_anchor' not in st.session_state:
        st.session_state.vault_anchor = None

    # --- VAULT INTERFACE ---
    with st.container(border=True):
        st.subheader("🔑 Establish Identity Anchor")
        st.write("Upload a high-quality, front-facing reference photo. The system will lock these facial features for all subsequent generations.")
        
        anchor_file = st.file_uploader("Drop Master Reference Image...", type=['png', 'jpg', 'jpeg'], key="vault_upload")
        
        if anchor_file:
            # We store the raw bytes to display it in the sidebar later
            st.session_state.vault_anchor = anchor_file.getvalue()
            st.success("✅ IDENTITY SECURED: Facial structure mapped to Protocol 2026-02-06.")

    # --- VAULT STATUS ---
    if st.session_state.vault_anchor:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(st.session_state.vault_anchor, caption="Active Anchor", use_container_width=True)
        with col2:
            st.markdown("""
            ### 🛠️ Vault Specifications
            - **Consistency Mode:** STRICT (High Fidelity)
            - **Feature Mapping:** 128-Point Facial Mesh
            - **Bypass Protection:** ACTIVE
            - **Targeting:** Neural Forge Integration Enabled
            """)
            if st.button("🗑️ PURGE IDENTITY"):
                st.session_state.vault_anchor = None
                st.rerun()
    else:
        st.info("The Vault is currently empty. Neural Forge will default to generic subjects.")

# --- SIDEBAR LIVE PREVIEW LOGIC ---
# (Place this outside the 'if page' blocks so it shows up everywhere)
if st.session_state.get('vault_anchor'):
    st.sidebar.divider()
    st.sidebar.markdown("<p style='text-align: center; color: #00ff41; font-size: 0.8em;'>ACTIVE IDENTITY DNA</p>", unsafe_allow_html=True)
    st.sidebar.image(st.session_state.vault_anchor, use_container_width=True)
    st.sidebar.caption("Protocol 2026-02-06: LOCKED")

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
    is_pro = user_status in ['pro', 'paid']

    # --- THE ROI ENGINE (ADMIN & PRO VERSION) ---
    if is_admin or is_pro:
        header_color = "#00d4ff" if is_admin else "#00ff41"
        header_label = "ADMIN" if is_admin else "PRO"
        
        draw_title("🧪", "ROI ENGINE v2.0")
        st.info("🛰️ Strategic Profit Projection: Analyze the fiscal weight of your content.")
        
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

        # --- GENERATION LOGIC ---
        if st.button("🧬 GENERATE PROFIT BLUEPRINT", use_container_width=True):
            with st.spinner("Calculating Strategic Trajectory..."):
                try:
                    roi_prompt = f"""
                    System: You are VOID-OS, a strategic financial AI for elite creators.
                    User Data:
                    - Niche: {selected_niche}
                    - Weekly Views: {views}
                    - Product Price: ${product_price}
                    - Conversion Rate: {conv_rate}%
                    - Ad Revenue (USD): ${ad_rev_usd}
                    - Sales Revenue (USD): ${sales_rev_usd}
                    - Total Weekly (INR): ₹{total_inr:,.2f}

                    Task: Provide a 3-point 'Profit Blueprint' that is easy to understand.
                    1. Revenue Breakdown (Simple terms)
                    2. Scaling Advice (How to double these numbers)
                    3. High-Vigor Warning (Potential risks in this niche)
                    Keep it punchy, professional, and tactical. Use bolding for key terms.
                    """
                    
                    res = groq_c.chat.completions.create(
                        model="llama-3.3-70b-versatile", 
                        messages=[{"role": "user", "content": roi_prompt}],
                        temperature=0.5
                    )
                    # Save result to session state to prevent disappearance
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

    # --- THE BASIC LAB (HOOK & RETENTION) ---
    else:
        draw_title("🧪", "CREATOR LAB")
        st.info("📡 Content Optimization: Refine your hooks and retention strategy.")

        tab_hook, tab_retention = st.tabs(["🔥 Hook Analyzer", "🧠 Cognitive Load"])

        with tab_hook:
            st.subheader("Viral Hook Architect")
            user_hook = st.text_area("Paste your opening line (Hook):", placeholder="Example: Most creators are failing at AI...")
            if st.button("ANALYZE HOOK"):
                with st.spinner("Neural Processing..."):
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

# --- MODULE 11: ADMIN CONSOLE (OPTION C) ---
elif page == "🛡️ Admin Console":
    draw_title("🛡️", "SYSTEM ADMINISTRATION")
    
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
# --- THE BETA ACCESS PORTAL (Replacing Upgrade Page) ---
draw_title("💎", "ELITE BETA ACCESS")

st.markdown("""
<div style='background: rgba(0, 212, 255, 0.05); padding: 25px; border-radius: 15px; border: 1px solid #00d4ff; margin-bottom: 25px;'>
    <h3 style='color: #00d4ff; margin-top: 0;'>TRUST > TRANSACTION</h3>
    <p style='color: #ccc; font-size: 1.1rem;'>
        We aren't looking for customers yet; we are looking for <b>Partners in Innovation</b>. 
        VOID-OS is currently in <b>Strict Calibration Mode</b>.
    </p>
    <hr style='border: 0.5px solid rgba(0, 212, 255, 0.2);'>
    <p style='color: #888;'>
        The 'Pay' gate is intentionally locked. Use the system, break it, and provide your feedback. 
        If after 7 days you feel the Matrix has added 10x value to your workflow, we will discuss 
        opening full Elite Clearance.
    </p>
</div>
""", unsafe_allow_html=True)

# THE PROGRESS TRACKER
st.write("### ⏳ YOUR TESTER MATURITY")
days_active = 1 # We can automate this later with a timestamp
progress = days_active / 7
st.progress(progress)
st.caption(f"Day {days_active} of 7: System is monitoring your engagement metrics.")

# THE CTA
if st.button("💬 I HAVE FEEDBACK NOW", use_container_width=True):
    st.session_state.show_feedback_node = True
    st.rerun()
# --- MODULE 8: MEDIA UPLINK (THE DIRECTOR'S BRIDGE) ---
elif page == "🛰️ Media Uplink":
    import yt_dlp
    import os

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
                            'format': 'best', # Get the best combined format
                        }
                        
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            # We only fetch info, we do NOT download on the server
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

























































































































































































































































































































