import streamlit as st
import pandas as pd
from groq import Groq

# --- CONFIG ---
st.set_page_config(page_title="Director Portal", layout="wide")

# --- DATABASE (The Global Pulse Data) ---
# We'll keep this local for now, then link your Google Sheet next.
# --- GOOGLE SHEET BRIDGE ---
# Replace the XXXXXX with the long ID from your Google Sheet URL
SHEET_ID = "163haIuPIna3pEY9IDxncPM2kFFsuZ76HfKsULcMu1y4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/163haIuPIna3pEY9IDxncPM2kFFsuZ76HfKsULcMu1y4/edit?usp=sharing"

@st.cache_data(ttl=600)  # This saves your data for 10 mins so it's lightning fast
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        return df
    except Exception as e:
        st.error(f"Spreadsheet Error: {e}")
        return pd.DataFrame() # Return empty if it fails

data = load_data()
})

# --- SIDEBAR & SEARCH ---
with st.sidebar:
    st.title("👤 Director Control")
    search_query = st.text_input("🔍 Instant Search", placeholder="e.g. AI Agents")
    st.divider()
    nav = st.radio("Intelligence Modules", ["Global Pulse", "Script Architect"])

# --- MODULE 1: GLOBAL PULSE ---
if nav == "Global Pulse":
    st.header("📈 Market Momentum")
    
    # Instant search filtering
    filtered_df = data[data['Niche'].str.contains(search_query, case=False)] if search_query else data
    
    # A clean, simple table view for now (we can add charts once this is stable)
    st.dataframe(filtered_df, use_container_width=True)
    
    if search_query and filtered_df.empty:
        st.warning(f"No data found for '{search_query}'. Try 'AI' or 'SaaS'.")

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


