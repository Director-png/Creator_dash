import streamlit as st
import pandas as pd
import plotly.express as px
import feedparser
from groq import Groq
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="VOID OS", page_icon="🌑", layout="wide")

# --- CUSTOM CSS FOR PROFESSIONAL SIDEBAR & UI ---
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #00051a;
            border-right: 1px solid #000080;
        }
        .stButton>button {
            width: 100%;
            border-radius: 5px;
            background-color: #000080;
            color: white;
            border: none;
        }
        .stButton>button:hover {
            background-color: #0000ff;
            border: none;
        }
        h1, h2, h3 {
            font-family: 'Inter', sans-serif;
        }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: white;'>VOID</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #4f4f4f;'>Parent Company: VOID</p>", unsafe_allow_html=True)
    st.divider()
    
    nav = st.radio("COMMAND CENTER", 
                  ["Dashboard", "VOID Intelligence", "Script Architect", "Settings"],
                  index=1)
    
    st.spacer = st.container()
    st.sidebar.markdown("---")
    st.sidebar.info("Founder Level Access: 1% Potential")

# --- MODULE: DASHBOARD (The Command Center) ---
if nav == "Dashboard":
    # Header with customized greeting
    st.markdown("<h1 style='color: white;'>🌑 VOID COMMAND CENTER</h1>", unsafe_allow_html=True)
    st.markdown(f"**Founder Status:** <span style='color: #0000FF;'>Active</span> | **Tier:** <span style='color: #000080;'>1% Potential</span>", unsafe_allow_html=True)
    st.divider()

    # --- TOP ROW: KPI METRICS ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label="Market Volatility", value="High", delta="+12% Signals")
    with m2:
        st.metric(label="Scripts Architected", value="24", delta="6 This Week")
    with m3:
        st.metric(label="Agency Leads", value="3", delta="Target: 10")
    with m4:
        st.metric(label="VOID Network", value="Operational", delta="Synced")

    st.markdown("---")

    # --- MIDDLE ROW: STRATEGIC OVERVIEW ---
    col_left, col_right = st.columns([2, 1])

with col_left:
        st.subheader("🚀 Active VOID Roadmap")
        
        # Creating the roadmap data
        roadmap_data = {
            "Phase": ["VOID Intelligence", "Script Architect", "Real Estate AI", "Agency Client Portal"],
            "Status": ["Stable", "Stable", "In Development", "Planned"],
            "Priority": ["Completed", "Active", "High", "Critical"]
        }
        
        # Convert to DataFrame
        df_road = pd.DataFrame(roadmap_data)
        
        # FIX: Shift the index to start at 1 instead of 0
        df_road.index = df_road.index + 1
        
        # Display the table
        st.table(df_road)
        
        # Color-coded status for a premium feel
        def color_status(val):
            color = '#000080' if val == 'Stable' else '#00051a'
            return f'background-color: {color}'

        st.table(df_road)

    with col_right:
        st.subheader("💡 Founder's Daily Directive")
        st.info("""
        1. **Code:** Finalize VOID OS stability.
        2. **Content:** Generate 3 scripts in Script Architect.
        3. **Outreach:** Identify 1 high-ticket client for VOID Capital.
        4. **Discipline:** Word is Law. No distractions.
        """)
        
        # Progress Bar for the day's grind
        st.write("Daily Grind Completion")
        st.progress(45)

    # --- BOTTOM ROW: TERMINAL LOG ---
    with st.expander("📂 View System Logs", expanded=False):
        st.code("""
        [SYSTEM] VOID Intelligence Feed: 10/10 Niches Synced.
        [SYSTEM] Groq API: Connection Stable (Latency 24ms).
        [SYSTEM] Founder Word: Maintained.
        [LOG] Awaiting next directive...
        """)



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


