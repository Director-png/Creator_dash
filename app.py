import streamlit as st
import pandas as pd

st.set_page_config(page_title="Creator Strategy Suite", layout="wide")

st.title("📈 Weekly Content Pulse")
st.write("If you see this, your app is officially working!")

# --- MOCK DATA (To bypass the 429 error for now) ---
data = {
    'Trend Name': ["Cotton Kurti", "Sunscreen", "Travel Vlogs", "Aesthetic Room"],
    'Velocity': [85, 92, 45, 78],
    'Status': ["🔥 Exploding", "🚀 Rising", "Stable", "🔥 Exploding"]
}
df = pd.DataFrame(data)

# --- DASHBOARD UI ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Current Market Hot-List")
    st.table(df)

with col2:
    st.subheader("Growth Analysis")
    st.bar_chart(df.set_index('Trend Name'))

st.success("Internal Server: ACTIVE")