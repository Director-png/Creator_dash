
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from groq import Groq
import feedparser
import re

# --- PAGE CONFIG ---
st.set_page_config(page_title="VOID OS", page_icon="🌑", layout="wide")

# --- DATABASE CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- AUTHENTICATION LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

def login_user(username, password):
    # Fetch user data from Google Sheets
    data = conn.read(worksheet="Users")
    user_row = data[(data['username'] == username) & (data['password'] == password)]
    if not user_row.empty:
        st.session_state.logged_in = True
        st.session_state.user_role = user_row.iloc[0]['role'] # 'admin' or 'user'
        st.session_state.username = username
        return True
    return False

# --- LOGIN / REGISTRATION UI ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.title("🌑 VOID LOGIN")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Enter The Void"):
            if login_user(u, p):
                st.success(f"Welcome, {u}")
                st.rerun()
            else:
                st.error("Invalid Credentials")
                
    with tab2:
        st.title("📜 REGISTER")
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            # Add logic here to append to GSheet
            st.info("Registration requires Admin Approval.")
    st.stop() # Prevents showing the dashboard until logged in

# --- AUTHORIZED SIDEBAR ---
with st.sidebar:
    st.markdown(f"**User:** {st.session_state.username} | **Role:** {st.session_state.user_role}")
    
    # DYNAMIC NAVIGATION based on Role
    nav_options = ["Dashboard", "VOID Intelligence", "Script Architect", "Settings"]
    
    # ONLY SHOW CLIENT PITCHER TO ADMIN
    if st.session_state.user_role == 'admin':
        nav_options.insert(3, "Client Pitcher")
    
    nav = st.radio("COMMAND CENTER", nav_options)
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

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





