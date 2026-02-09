import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
from datetime import datetime


# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="Creator Director Portal", layout="wide")

# Custom CSS to make it look "Pro"
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE GOOGLE SHEET BRIDGE ---
# Using your verified Sheet ID
SHEET_ID = "163haIuPIna3pEY9IDxncPM2kFFsuZ76HfKsULcMu1y4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        # Standardize headers
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        
        # Clean numeric growth column
        if 'Growth' in df.columns:
            df['Growth'] = df['Growth'].astype(str).str.replace('%', '').str.replace(',', '').str.strip()
            df['Growth'] = pd.to_numeric(df['Growth'], errors='coerce').fillna(0)
        return df
    except Exception as e:
        # Fallback if Google Sheet is unreachable
        return pd.DataFrame({'Niche': ['Check Sheet Share Settings'], 'Growth': [0], 'Status': ['🔴']})

data = load_data()

# --- 3. SIDEBAR NAVIGATION & SEARCH ---
with st.sidebar:
    st.title("🛡️ Director HQ")
    search_query = st.text_input("Global Search", placeholder="Search niche...")
    nav = st.radio("Intelligence Modules", ["Global Pulse", "Script Architect", "User Database"])
    st.divider()
    st.info("Bridge Status: Connected ✅")

# --- 4. MODULE: GLOBAL PULSE ---
if nav == "Global Pulse":
    st.header("📈 Market Momentum")
    
    # Filter logic
    filtered_df = data[data['Niche'].str.contains(search_query, case=False)] if search_query else data
    
    if not filtered_df.empty:
        # Top Metrics
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Niches", len(filtered_df))
        with c2:
            st.metric("Avg Growth", f"{filtered_df['Growth'].mean():.1f}%")
        with c3:
            st.metric("Top Performer", filtered_df.iloc[0]['Niche'])

        # Plotly Chart
        fig = px.bar(
            filtered_df, 
            x='Niche', 
            y='Growth', 
            color='Status',
            text_auto='.2s',
            title="Niche Growth Velocity",
            template="plotly_dark",
            color_discrete_map={'🔥 Rising': '#FF4B4B', '⚖️ Stable': '#00CC96', '📉 Dropping': '#636EFA'}
        )
        st.plotly_chart(fig, use_container_width=True)

        # Raw Data Table (Starting from 1)
        with st.expander("📂 View Raw Intelligence Feed"):
            display_df = filtered_df.copy()
            display_df.index = range(1, len(display_df) + 1)
            st.dataframe(display_df, use_container_width=True)
    else:
        st.warning(f"No data found for '{search_query}'.")

# --- 5. MODULE: SCRIPT ARCHITECT ---
elif nav == "Script Architect":
    st.header("💎 AI Strategy Generator")
    topic = st.text_input("Content Topic", value=search_query)
    
    if st.button("Generate Strategy"):
        try:
            # Pulling your secret key from Streamlit Cloud
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            with st.spinner("Llama-3.1 is analyzing..."):
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant", 
                    messages=[{"role": "user", "content": f"Create a viral video script for: {topic}. Include a hook, 3 value points, and a CTA."}]
                )
                st.markdown("### Output Script")
                st.write(completion.choices[0].message.content)
        except Exception as e:
            st.error(f"AI Connection Error: {e}")


# --- 6. MODULE: USER DATABASE ---
elif nav == "User Database":
    st.header("👥 Creator Intelligence Network")
    
    # Visual Progress Bar (makes the form feel more professional)
    st.write("Complete your registration to unlock advanced analytics.")
    st.progress(65) 
    
    st.markdown("---")

    # Creating two columns: One for the form, one for a "Why Join" info box
    col1, col2 = st.columns([2, 1])

    with col1:
        with st.form("signup_form", clear_on_submit=True):
            st.subheader("Registration Portal")
            
            name = st.text_input("Full Name", placeholder="e.g. Director Smith")
            email = st.text_input("Email Address", placeholder="director@agency.com")
            
            # Pulling niche options directly from your Google Sheet data!
            niche_list = data['Niche'].unique().tolist()
            creator_niche = st.selectbox("Your Primary Niche", options=niche_list)
            
            experience = st.select_slider(
                "Experience Level",
                options=["Newbie", "Growing", "Professional", "Elite"]
            )
            
            submit_button = st.form_submit_button("Secure My Spot In Database")
            
            if submit_button:
                if name and email:
                    # This part simulates the save logic
                    st.success(f"✅ Protocol Initiated! Welcome, {name}.")
                    st.balloons()
                    
                    # Logic Preview (What will be sent to Google Sheets later)
                    st.code(f"""
                    SENDING TO DATABASE:
                    --------------------
                    User: {name}
                    Niche: {creator_niche}
                    Level: {experience}
                    Time: {datetime.now().strftime("%H:%M:%S")}
                    """)
                else:
                    st.error("Missing Credentials. Please fill in Name and Email.")

    with col2:
        st.info("### 🛡️ Why Register?")
        st.write("""
        - **Early Access:** Get the Global Pulse trends 24h early.
        - **AI Credits:** 50 free Script Architect generations/month.
        - **Network:** Connect with other 'Elite' level creators.
        """)
        st.image("https://cdn-icons-png.flaticon.com/512/6596/6596121.png", width=100)
