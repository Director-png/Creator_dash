import plotly.express as px
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
        # Clean up column names: remove spaces and make Title Case
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        
        if 'Growth' in df.columns:
            # Fix: Added .str before .strip()
            df['Growth'] = df['Growth'].astype(str).str.replace('%', '').str.replace(',', '').str.strip()
            df['Growth'] = pd.to_numeric(df['Growth'], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        return pd.DataFrame({'Niche': [f"Error: {e}"], 'Growth': [0], 'Status': ['🔴']})

data = load_data()

# --- SIDEBAR & SEARCH ---
with st.sidebar:
    st.title("👤 Director Control")
    search_query = st.text_input("🔍 Instant Search", placeholder="e.g. AI Agents")
    st.divider()
    nav = st.radio("Intelligence Modules", ["Global Pulse", "Script Architect"])

# --- CONTENT AREA ---
if nav == "Global Pulse":
    st.header("📈 Market Momentum") # This is your ONLY header
    
    filtered_df = data[data['Niche'].str.contains(search_query, case=False)] if search_query else data
    
    if not filtered_df.empty:
        # 1. TOP METRICS
        c1, c2 = st.columns(2)
        c1.metric("Total Niches", len(filtered_df))
        c2.metric("Avg Growth", f"{filtered_df['Growth'].mean():.1f}%")

        # 2. THE CHART (Visual)
        fig = px.bar(filtered_df, x='Niche', y='Growth', color='Status', template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
        # 3. THE DATA (Hidden in an expander)
        with st.expander("📂 View Raw Intelligence Feed"):
            st.dataframe(filtered_df, use_container_width=True)
           
            # 2. The Chart
            fig = px.bar(
                filtered_df, 
                x='Niche', 
                y='Growth', 
                color='Status',
                title="Real-Time Market Heat",
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 3. The Table
            st.subheader("Raw Intelligence Feed")
            st.dataframe(filtered_df, use_container_width=True)
    else:
            st.warning(f"No results found for '{search_query}'. Try clearing the search bar!")

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











