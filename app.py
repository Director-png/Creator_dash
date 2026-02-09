import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# --- CONFIG ---
st.set_page_config(page_title="Director Portal", layout="wide")
GEMINI_API_KEY = "AIzaSyDPwcKpNTwJ-Gi2dyMMW-reTl01rm-61L4"
genai.configure(api_key=GEMINI_API_KEY)
# This is the most stable way to call the model in 2026
model = genai.GenerativeModel('gemini-1.5-flash')


# --- SIDEBAR: SEARCH & NAVIGATION ---
with st.sidebar:
    st.title("🛡️ Command Center")
    # THE INSTANT SEARCH TAB
    search_query = st.text_input("🔍 Instant Search", placeholder="Search niche (e.g., SaaS)...").strip()
    
    if search_query:
        st.subheader("⚡ Quick Strategy")
        st.caption(f"Keywords: #{search_query.replace(' ','')}, #Viral2026")
        st.write(f"**Hook:** 'Stop scrolling if you care about {search_query}...'")

    nav = st.radio("Navigation", ["Global Pulse", "Comparison Hub", "Script Architect"])

# --- DATABASE (MOCK DATA FOR VISUALS) ---
# This data feeds the charts and tables
market_data = pd.DataFrame({
    'Niche': ['AI Agents', 'SaaS', 'Bio-Hacking', 'E-com', 'Fitness'],
    'Growth': [98, 85, 45, 62, 77],
    'Status': ['🔥 Rising', '🔥 Rising', '📉 Dropping', '⚖️ Stable', '⚖️ Stable']
})

# --- MODULES ---

if nav == "Global Pulse":
    st.header("📈 Global Pulse Trends")
    
    # Filtering logic for Search
    filtered_df = market_data[market_data['Niche'].str.contains(search_query, case=False)] if search_query else market_data
    
    # Displaying Metrics & Labels (Rising, Stable, etc.)
    cols = st.columns(len(filtered_df))
    for i, (idx, row) in enumerate(filtered_df.iterrows()):
        cols[i].metric(row['Niche'], f"{row['Growth']}%", row['Status'])

    # THE CHART
    fig = px.bar(filtered_df, x='Niche', y='Growth', color='Status', 
                 title="Market Momentum Analysis", template="plotly_dark",
                 color_discrete_map={'🔥 Rising': '#00FF00', '⚖️ Stable': '#00BFFF', '📉 Dropping': '#FF4B4B'})
    st.plotly_chart(fig, use_container_width=True)

elif nav == "Script Architect":
    st.header("💎 AI Script Architect")
    topic = st.text_input("Video Topic", value=search_query)
    
    if st.button("Generate Master Strategy"):
        try:
            # EXPLICIT MODEL PATHING
            model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
            prompt = f"Develop a viral script for {topic}. Include 3 hooks and SEO keywords."
            response = model.generate_content(prompt)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"API Error: {e}")
            st.info("Ensure your requirements.txt is updated to google-generativeai>=0.8.3")

