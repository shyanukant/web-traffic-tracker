import streamlit as st
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="📈 Visitor Tracker Dashboard", layout="wide")
st.title("🔍 Web Traffic Dashboard")

st.title("📋 Website Registration")
with st.form("register_form"):
    name = st.text_input("Website Name")
    domain = st.text_input("Website Domain (e.g., example.com)")
    submitted = st.form_submit_button("Register")

    if submitted:
        resp = requests.post("http://localhost:8000/register", json={"name": name, "domain": domain})
        st.success(resp.json().get("message", "Done"))
        st.rerun()  # 🔁 Refresh to pull updated websites list



st.title("📊 Your Website Visitors")
# 🔁 Autorefresh every 5 seconds (adjust if needed)
st_autorefresh(interval=5000, limit=None, key="refresh")

# Fetch list of websites
try:
    websites = requests.get("http://localhost:8000/websites").json()
    domain_options = {w['name']: w['domain'] for w in websites}
except:
    domain_options = {}

# Dropdown to select website
# Dropdown to select website
if domain_options:
    selected_name = st.selectbox("Select Website", list(domain_options.keys()))
    selected_domain = domain_options[selected_name]
    
    # Fetch traffic data for selected website by name
    try:
        data = requests.get(f"http://localhost:8000/data/{selected_name}").json()
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