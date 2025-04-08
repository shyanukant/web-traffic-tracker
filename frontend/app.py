import streamlit as st
import requests

# Set this to your Codespace public URL or localhost
BACKEND_URL = "https://automatic-journey-xx7xvp79qrpfpr5p-8000.app.github.dev/data"

st.title("📊 Visitor Analytics Demo")

st.info("Showing live tracking data from backend...")

try:
    res = requests.get(BACKEND_URL)
    data = res.json()

    st.metric("Total Visitors", len(data))
    st.table(data[::-1])  # show latest first
except Exception as e:
    st.error(f"Error connecting to backend: {e}")
