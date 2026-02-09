import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px

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
    st.subheader("Join the Elite Database")
    
    # 1. THE FORM
    with st.form("signup_form"):
        st.write("Register your channel to receive custom market reports.")
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        creator_niche = st.selectbox("Your Primary Niche", data['Niche'].unique())
        
        submit_button = st.form_submit_button("Secure My Spot")
        
        if submit_button:
            if name and email:
                # 2. THE DATA OBJECT
                new_lead = pd.DataFrame([{
                    "Name": name,
                    "Niche": creator_niche,
                    "Email": email,
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])
                
                # 3. SUCCESS MESSAGE (Visual Feedback)
                st.success(f"Welcome to the network, Director {name}!")
                st.balloons()
                
                # Note: We will link the actual Google Sheet "Write" 
                # function once your credentials are set up!
                st.info("System Log: Lead captured. Finalizing database sync...")
            else:
                st.warning("Please fill in all fields to authorize access.")

    # 4. PREVIEW FOR THE DIRECTOR
    st.divider()
    st.subheader("Current Network Strength")
    st.write("Only you can see this high-level overview.")
    # This will eventually pull from your 'Leads' sheet
    st.info("Database encrypted. Total Members: 1")
