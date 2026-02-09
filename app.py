import streamlit as st
import pandas as pd
from groq import Groq

# --- CONFIG ---
st.set_page_config(page_title="Director Portal", layout="wide")

# --- DATABASE (The Global Pulse Data) ---
# We'll keep this local for now, then link your Google Sheet next.
# --- GOOGLE SHEET BRIDGE ---
# Replace the XXXXXX with the long ID from your Google Sheet URL
# Use this EXACT ID from your file
SHEET_ID = "163haIuPIna3pEY9IDxncPM2kFFsuZ76HfKsULcMu1y4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        
        # 1. Clean Headers
        df.columns = [c.strip().capitalize() for c in df.columns]
        
        # 2. THE FIX: Clean the 'Growth' column
        # This removes %, commas, or spaces and converts to a number
        if 'Growth' in df.columns:
            df['Growth'] = df['Growth'].astype(str).str.replace('%', '').str.replace(',', '').strip()
            df['Growth'] = pd.to_numeric(df['Growth'], errors='coerce').fillna(0)
            
        return df
    except Exception as e:
        st.error(f"⚠️ Connection Blocked: {e}")
        return pd.DataFrame({'Niche': ['Check Sheet'], 'Growth': [0], 'Status': ['Error']})
data = load_data()

# --- SIDEBAR & SEARCH ---
with st.sidebar:
    st.title("👤 Director Control")
    search_query = st.text_input("🔍 Instant Search", placeholder="e.g. AI Agents")
    st.divider()
    nav = st.radio("Intelligence Modules", ["Global Pulse", "Script Architect"])

# --- MODULE 1: GLOBAL PULSE ---
import plotly.express as px

if nav == "Global Pulse":
    st.header("📈 Market Momentum")
    
    # 1. THE SEARCH FILTER
    filtered_df = data[data['Niche'].str.contains(search_query, case=False)] if search_query else data
    
    if not filtered_df.empty:
        # 2. THE TOP METRICS BARS (Visual Summary)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Niches Tracked", len(filtered_df))
        with col2:
            avg_growth = filtered_df['Growth'].mean()
            st.metric("Avg Growth Score", f"{avg_growth:.1f}%")
        with col3:
            st.metric("Top Performer", filtered_df.iloc[0]['Niche'])

        st.divider()

        # 3. THE CHART (Replacing the 2nd table)
        fig = px.bar(
            filtered_df, 
            x='Niche', 
            y='Growth', 
            color='Status',
            text='Growth',
            title="Growth Velocity by Niche",
            template="plotly_dark", # Looks better for a "Director" portal
            color_discrete_map={'🔥 Rising': '#FF4B4B', '⚖️ Stable': '#00CC96', '📉 Dropping': '#636EFA'}
        )
        st.plotly_chart(fig, use_container_width=True)

        # 4. THE DATA TABLE (Keep only one, at the bottom for reference)
        with st.expander("📂 View Raw Data Source"):
            st.dataframe(filtered_df, use_container_width=True)
            
    else:
        st.warning("Director, no data found for that search. Check your Google Sheet!")
# --- THE MAIN CONTENT AREA ---
if nav == "Global Pulse":
    st.header("📈 Market Momentum")
    filtered_df = data[data['Niche'].str.contains(search_query, case=False)] if search_query else data
    st.dataframe(filtered_df, use_container_width=True)
elif nav == "Script Architect":
    st.header("💎 AI Strategy Generator")
    topic = st.text_input("Content Topic", value=search_query)
    
    if st.button("Generate Strategy"):
        try:
            final_key = st.secrets["GROQ_API_KEY"]
            client = Groq(api_key=final_key)
            
            with st.spinner("Groq is thinking..."):
                completion = client.chat.completions.create(
                    # WE UPDATED THIS LINE BELOW:
                    model="llama-3.1-8b-instant", 
                    messages=[{"role": "user", "content": f"Create a viral script for: {topic}"}]
                )
                st.markdown(completion.choices[0].message.content)
        except Exception as e:
            st.error(f"Error: {e}")







