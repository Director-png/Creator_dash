import streamlit as st

st.title("🛡️ Director's Portal")

# Direct bypass to check if the server is alive
st.write("---")
st.header("System Status: ONLINE")
st.info("Director, if you can see this message, the connection is fixed.")

search = st.text_input("Test the Instant Search bar here:")
if search:
    st.write(f"You searched for: **{search}**")
    st.success("The logic is working perfectly.")

st.write("---")
st.warning("Once this screen appears, tell me, and we will add the AI back in one piece at a time.")
