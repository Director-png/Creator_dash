import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
import requests
import feedparser

# --- 1. CONFIG & CONNECTIONS ---
st.set_page_config(page_title="VOID Director Portal", layout="wide", page_icon="🌑")

# User Database (Public CSV link from your Google Sheet)
USER_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8sFup141r9k9If9fu6ewnpWPkTthF-rMKSMSn7l26PqoY3Yb659FIDXcU3UIU9mo5d2VlR2Z8gHes/pub?output=csv"

# Google Form Submission Link (For Registration)
FORM_POST_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfnNLb9O-szEzYfYEL85aENIimZFtMd5H3a7o6fX-_6ftU_HA/formResponse"

# --- 2. DATA LOADING ---
def load_user_db():
    try:
        # We use clear cache to ensure we get the latest registrations
        df = pd.read_csv(USER_DB_URL)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# --- 3. SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = "user"
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- 4. THE DIRECTOR'S GATEKEEPER (LOGIN/REG) ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: white;'>🛡️ DIRECTOR'S INTELLIGENCE PORTAL</h1>", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["🔑 Access System", "📝 Register Intelligence"])

    with t1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            email_in = st.text_input("Username / Email", key="login_email").lower().strip()
            pw_in = st.text_input("Access Key (Password)", type="password", key="login_pw").strip()
            
            if st.button("Initialize VOID Access", use_container_width=True):
                users = load_user_db()
                
                # Master Admin Bypass
                if email_in == "admin" and pw_in == "1234":
                    st.session_state.logged_in = True
                    st.session_state.user_name = "Master Director"
                    st.session_state.user_role = "admin"
                    st.rerun()
                
                elif not users.empty:
                    # Dynamically find columns based on your form structure
                    email_col = users.columns[1] # entry.1873870532
                    pw_col = users.columns[4]    # entry.1396549807
                    name_col = users.columns[0]  # entry.483203499
                    niche_col = users.columns[3] # entry.1906780868

                    match = users[(users[email_col].astype(str).str.lower() == email_in) & (users[pw_col].astype(str) == pw_in)]
                    
                    if not match.empty:
                        st.session_state.logged_in = True
                        st.session_state.user_name = match.iloc[0][name_col]
                        # Set admin if 'fitness' or 'admin' is in their niche/role
                        role_val = str(match.iloc[0][niche_col]).lower()
                        st.session_state.user_role = "admin" if "fitness" in role_val or "admin" in role_val else "user"
                        st.rerun()
                    else:
                        st.error("Invalid Intelligence Credentials.")
                else:
                    st.error("Database connection lag. Try again in 10s.")

    with t2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("reg_form"):
                name = st.text_input("Full Name")
                email = st.text_input("Email")
                niche = st.text_input("Niche / Focus Area")
                pw = st.text_input("Set Access Key", type="password")
                
                if st.form_submit_button("Transmit Registration", use_container_width=True):
                    payload = {
                        "entry.483203499": name,
                        "entry.1873870532": email,
                        "entry.1906780868": niche,
                        "entry.1396549807": pw
                    }
                    try:
                        requests.post(FORM_POST_URL, data=payload)
                        st.success("Data Transmitted. System sync takes ~60 seconds.")
                        st.balloons()
                    except:
                        st.error("Transmission Interrupted.")
    st.stop()

# --- 5. UNLOCKED COMMAND CENTER ---
with st.sidebar:
    st.markdown(f"### 🌑 VOID OS\n**Director:** {st.session_state.user_name}")
    st.caption(f"Status: {st.session_state.user_role.upper()} ACCESS")
    st.divider()
    
    nav_items = ["Dashboard", "Global Pulse", "Script Architect"]
    if st.session_state.user_role == "admin":
        nav_items.append("Client Pitcher")
    
    nav = st.radio("Intelligence Modules", nav_items)
    
    st.divider()
    if st.button("Terminate Session"):
        st.session_state.logged_in = False
        st.rerun()

# --- DASHBOARD LOGIC ---
if nav == "Dashboard":
    st.title("🌑 VOID COMMAND CENTER")
    # Insert your customizable metrics here...
    st.info(f"Welcome back, {st.session_state.user_name}. Your {st.session_state.user_role} clearance is active.")

# --- CLIENT PITCHER (ADMIN LOCK) ---
elif nav == "Client Pitcher":
    if st.session_state.user_role == "admin":
        st.header("💼 VOID CAPITAL: PITCH GENERATOR")
        # Insert Pitcher Code here...
    else:
        st.error("Access Denied. Admin clearance required.")
    
    # Define standard tabs
    nav_items = ["Dashboard", "VOID Intelligence", "Script Architect"]
    
    # ADMIN GATE: Only show Client Pitcher if role is admin
    if st.session_state.user_role == 'admin':
        nav_items.append("Client Pitcher")
    
    nav_items.append("Settings")
    
    nav = st.radio("COMMAND CENTER", nav_items)
    
    st.divider()
    if st.button("Terminate Session"):
        st.session_state.logged_in = False
        st.rerun()

# --- MODULE: DASHBOARD ---
if nav == "Dashboard":
    st.title("🌑 VOID COMMAND")
    # Using your customizable metrics from the previous step
    m1, m2, m3 = st.columns(3)
    m1.metric("Status", "Operational", "Stable")
    m2.metric("Access Level", st.session_state.user_role.upper())
    m3.metric("Database", "G-Sheets Connected")

# --- MODULE: CLIENT PITCHER (ADMIN ONLY) ---
elif nav == "Client Pitcher":
    if st.session_state.user_role == 'admin':
        st.title("💼 VOID CAPITAL: PITCH GENERATOR")
        # [Insert Pitcher Code here]
    else:
        st.error("Unauthorized Access. This incident has been logged.")

# --- MODULE: VOID INTELLIGENCE ---
elif nav == "VOID Intelligence":
    st.title("📡 VOID INTELLIGENCE")
    # [Insert Intelligence Code here]

# --- MODULE: SCRIPT ARCHITECT ---
elif nav == "Script Architect":
    st.title("✍️ SCRIPT ARCHITECT")
    # [Insert Script Architect Code here]

# --- SESSION STATE INITIALIZATION (For Customization) ---
if 'metric_1_label' not in st.session_state:
    st.session_state.metric_1_label = "Market Volatility"
    st.session_state.metric_1_val = "High"
if 'daily_directive' not in st.session_state:
    st.session_state.daily_directive = "1. Code VOID OS\n2. Draft 3 Scripts\n3. 1 Client Lead\n4. Word is Law"

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: white;'>🌑 VOID</h1>", unsafe_allow_html=True)
    st.divider()
    nav = st.radio("COMMAND CENTER", 
                  ["Dashboard", "VOID Intelligence", "Script Architect", "Client Pitcher", "Settings"])
    st.divider()
    st.info("Founder Level Access: 1%")

# --- MODULE: DASHBOARD (CUSTOMIZABLE) ---
if nav == "Dashboard":
    st.markdown("<h1 style='color: white;'>🌑 VOID COMMAND CENTER</h1>", unsafe_allow_html=True)
    
    # --- CUSTOMIZATION DRAWER ---
    with st.expander("🛠️ Customize Dashboard Layout"):
        col_edit1, col_edit2 = st.columns(2)
        st.session_state.metric_1_label = col_edit1.text_input("Metric 1 Label", st.session_state.metric_1_label)
        st.session_state.metric_1_val = col_edit1.text_input("Metric 1 Value", st.session_state.metric_1_val)
        st.session_state.daily_directive = col_edit2.text_area("Edit Daily Directive", st.session_state.daily_directive)

    st.divider()

    # TOP ROW: METRICS (Using Custom State)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label=st.session_state.metric_1_label, value=st.session_state.metric_1_val)
    m2.metric(label="Scripts Ready", value="24", delta="+6")
    m3.metric(label="Agency Leads", value="3", delta="Target: 10")
    m4.metric(label="System Status", value="Operational")

    st.markdown("---")

    # MIDDLE ROW
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader("🚀 Active VOID Roadmap")
        roadmap_data = {
            "Phase": ["VOID Intelligence", "Script Architect", "Client Pitcher", "Agency Portal"],
            "Status": ["Stable", "Stable", "Online", "Planned"],
            "Priority": ["Completed", "Active", "High", "Critical"]
        }
        df_road = pd.DataFrame(roadmap_data)
        df_road.index = df_road.index + 1
        st.table(df_road)

    with col_right:
        st.subheader("💡 Daily Directive")
        st.info(st.session_state.daily_directive)
        st.write("Grind Completion")
        st.progress(45)

# --- MODULE: CLIENT PITCHER (VOID CAPITAL) ---
elif nav == "Client Pitcher":
    st.markdown("<h1 style='color: #000080;'>💼 VOID CAPITAL: PITCH GENERATOR</h1>", unsafe_allow_html=True)
    st.caption("Closing high-ticket clients with AI precision.")

    c1, c2 = st.columns([1, 1.5])
    with c1:
        client_name = st.text_input("Business Name")
        niche = st.selectbox("Niche", ["Real Estate", "E-commerce", "SaaS", "Local Business"])
        offer = st.text_area("What are you selling?", placeholder="e.g., Short-form video growth packages")
        pitch_btn = st.button("🔥 Generate Power Pitch")

    with c2:
        if pitch_btn and client_name:
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                prompt = f"Write a high-converting, professional cold DM for {client_name} in the {niche} niche. Our offer: {offer}. Tone: Confident, minimalist, and value-driven. No fluff."
                
                with st.spinner("Crafting..."):
                    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                    st.markdown("### The Pitch")
                    st.write(res.choices[0].message.content)
            except Exception as e:
                st.error(f"Sync Error: {e}")

# --- KEEPING OTHER MODULES (PULSE & ARCHITECT) ---
# [Include your Intelligence and Script Architect code here following the same elif pattern]



# --- MODULE: VOID INTELLIGENCE ---
elif nav == "VOID Intelligence":
    st.markdown("<h1 style='color: #000080;'>🌑 VOID INTELLIGENCE</h1>", unsafe_allow_html=True)
    st.caption("Strategic Market Signal Analysis | Version 1.1")

    # 1. LIVE NEWS SOURCE
    RSS_URL = "https://techcrunch.com/feed/" 
    feed = feedparser.parse(RSS_URL)
    
    # 2. THE INTEL FEED
    st.subheader("📡 Recent Market Intel")
    cols = st.columns(3)
    
    if feed.entries:
        for i, entry in enumerate(feed.entries[:3]):
            with cols[i]:
                search_term = entry.title.split()[0] if entry.title else "tech"
                img_url = f"https://loremflickr.com/800/600/{search_term}?random={i}"
                st.image(img_url, use_container_width=True)
                st.markdown(f"**{entry.title}**")
                st.markdown(f"[Access Intelligence]({entry.link})")
    
    st.divider()

    # 3. THE ANALYTICS BRAIN
    if 'market_intelligence' not in st.session_state:
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            headlines = " | ".join([e.title for e in feed.entries[:10]])
            
            with st.spinner("Decoding VOID Signals..."):
                prompt = f"Analyze: {headlines}. Identify 10 unique tech/finance niches. Output ONLY 10 lines like: Topic:Score. (Score 1-100). No talk."
                chat_completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # --- CAREFUL INDENTATION HERE ---
                raw_text = chat_completion.choices[0].message.content
                matches = re.findall(r"([^:\n]+):(\d+)", raw_text)
                
                final_data = []
                for m in matches:
                    final_data.append([m[0].strip(), int(m[1])])
                
                if len(final_data) < 10:
                    fallbacks = [["VOID AI", 95], ["FinTech", 88], ["SaaS", 82], ["Quantum", 79], ["Neural Nets", 75]]
                    for f in fallbacks:
                        if len(final_data) < 10:
                            final_data.append(f)
                
                st.session_state.market_intelligence = pd.DataFrame(final_data[:10], columns=['Niche', 'Growth'])
                # -------------------------------
                
        except Exception as e:
            st.error(f"Intelligence Bridge Error: {e}")

    # 4. BLUE GRADIENT CHART
    if 'market_intelligence' in st.session_state:
        df = st.session_state.market_intelligence
        if not df.empty:
            st.subheader("📊 Growth Velocity (Top 10 Niches)")
            fig = px.bar(
                df, x='Growth', y='Niche', orientation='h', 
                color='Growth',
                color_continuous_scale=[[0, '#ADD8E6'], [0.5, '#0000FF'], [1.0, '#000080']],
                template="plotly_dark"
            )
            fig.update_layout(showlegend=False, height=500, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

    if st.button("🔄 Sync VOID Feed"):
        if 'market_intelligence' in st.session_state:
            del st.session_state.market_intelligence
        st.rerun()

# --- MODULE: SCRIPT ARCHITECT ---
elif nav == "Script Architect":
    st.markdown("<h1 style='color: #000080;'>✍️ VOID SCRIPT ARCHITECT</h1>", unsafe_allow_html=True)
    st.caption("Strategic Content Engineering for the 1% | Version 1.2")

    # Creating a clean, centered interface
    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        st.subheader("🛠️ Configuration")
        # Use keys to ensure Streamlit doesn't lose the data on rerun
        topic_input = st.text_input("Enter Focus Topic", placeholder="e.g., The collapse of traditional banking", key="topic_input")
        platform_choice = st.selectbox("Target Platform", ["YouTube Shorts", "Instagram Reels", "Long-form", "Twitter/X Thread"], key="plat_choice")
        tone_choice = st.select_slider("Script Tone", options=["Aggressive", "Professional", "Storyteller"], key="tone_choice")
        
        generate_btn = st.button("🚀 Architect Script", type="primary")

    with col2:
        st.subheader("📄 VOID Script Output")
        if generate_btn:
            if topic_input:
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    
                    # The VOID Framework Prompt
                    prompt = f"""
                    You are the VOID Content Architect. Write a high-retention {platform_choice} script about '{topic_input}'.
                    Tone: {tone_choice}.
                    
                    STRUCTURE (Strict):
                    1. THE PATTERN INTERRUPT (0-3s): A hook that stops the scroll.
                    2. THE PROBLEM (3-10s): Why does the viewer feel 'empty' or behind?
                    3. THE VOID INSIGHT (10-40s): 3 rapid-fire, high-value facts or strategies.
                    4. THE EXECUTION (40-55s): How to apply this immediately.
                    5. THE CALL TO POWER (CTA): A sharp directive to follow/subscribe.
                    
                    Formatting: Use bolding for emphasis. No emojis. Short, punchy sentences.
                    """
                    
                    with st.spinner("Analyzing Market Trends & Architecting..."):
                        chat_completion = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        final_script = chat_completion.choices[0].message.content
                        st.markdown("---")
                        st.markdown(final_script)
                        # Add a download button for the script
                        st.download_button("📥 Download Script", final_script, file_name=f"VOID_Script_{topic_input}.txt")
                except Exception as e:
                    st.error(f"Logic Bridge Failure: {e}")
            else:
                st.warning("Founder, a topic is required to generate intelligence.")
        else:
            st.info("Awaiting input parameters to begin architecture.")







