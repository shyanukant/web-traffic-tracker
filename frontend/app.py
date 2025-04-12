import streamlit as st
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh
import os
# API_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
API_URL = "https://traffic-tracker.onrender.com/"
print(f"API_URL: {API_URL}")  # Debugging line to check the API URL
  # Adjust this if your API is hosted elsewhere
st.set_page_config(page_title="📈 Visitor Tracker Dashboard", layout="wide")
st.title("🔍 Web Traffic Dashboard")

st.title("📋 Website Registration")
with st.form("register_form"):
    name = st.text_input("Website Name")
    domain = st.text_input("Website Domain (e.g., example.com)")
    submitted = st.form_submit_button("Register")

    if submitted:
        response = requests.post(f"{API_URL}/register", json={"name": name, "domain": domain})
        resp = response.json()
        st.success(resp.get("message", "Done"))
        if resp.get("status") == "registered":
            st.code(resp.get("script"), language="javascript")
            st.info("Copy and paste this script into the <head> of your website")
            st.session_state["script_activated"] = True  # ✅ set flag for auto-refresh

        elif resp.get("status") == "exists":
            st.warning("Website already registered. Please try another name or domain.")
        # st.rerun()  # 🔁 Refresh to pull updated websites list
    else:
        st.info("Fill in the form to register your website and get the tracking script.")



st.title("📊 Your Website Visitors")
# 🔁 Autorefresh every 15 seconds (adjust if needed)
if st.session_state.get("script_activated", False):
    # Only refresh if the user has script activated
    st_autorefresh(interval=15000, limit=None, key="refresh")


# Fetch list of websites
try:
    websites = requests.get(f"{API_URL}/websites").json()
    domain_options = {w['name']: w['domain'] for w in websites}
except:
    domain_options = {}

# Dropdown to select website
if domain_options:
    selected_name = st.selectbox("Select Website", list(domain_options.keys()))
    selected_domain = domain_options[selected_name]
    if selected_name:
        st.subheader("📎 Tracking Script")
        script = f'<script async src="{API_URL}/tracker.js" data-site="{selected_domain}"></script>'
        st.code(script, language="javascript")
        st.info("Copy this into the <head> of your site if you haven't yet.")
    
    # Fetch traffic data for selected website by name
    try:
        data = requests.get(f"{API_URL}/data/{selected_name}").json()
        if data and isinstance(data, list):
            df = pd.DataFrame(data)
            df = df.drop(columns=['_sa_instance_state'], errors='ignore')
            st.write(f"Showing live data for: `{selected_name}`")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No visitor data yet.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")

else:
    st.warning("No websites registered yet.")