import streamlit as st
import pandas as pd
import requests
import os
import datetime

# Configuration
API_URL = os.getenv("API_BASE_URL", "https://traffic-tracker.onrender.com")
# print(f"API_URL: {API_URL}")  # Debugging line

# --- Setup ---
st.set_page_config(page_title="📈 Visitor Tracker Dashboard", layout="wide")
st.title("🔍 Web Traffic Dashboard")

# --- Helper Functions ---
def register_website(api_url):
    st.title("📋 Website Registration")
    with st.form("register_form"):
        name = st.text_input("Website Name")
        domain = st.text_input("Website Domain (e.g., example.com)")
        submitted = st.form_submit_button("Register")

        if submitted:
            try:
                response = requests.post(f"{api_url}/register", json={"name": name, "domain": domain})
                resp = response.json()
                st.success(resp.get("message", "Done"))

                if resp.get("status") == "registered":
                    st.code(resp.get("script"), language="javascript")
                    st.info("Copy and paste this script into the <head> of your website")
                    st.session_state["script_activated"] = True

                elif resp.get("status") == "exists":
                    st.warning("Website already registered. Please try another name or domain.")
            except Exception as e:
                st.error(f"Registration failed: {e}")
        else:
            st.info("Fill in the form to register your website and get the tracking script.")

def fetch_websites(api_url):
    try:
        websites = requests.get(f"{api_url}/websites").json()
        return {w['name']: w['domain'] for w in websites}
    except:
        return {}

def display_tracking_script(api_url, selected_name, selected_domain):
    st.subheader("📎 Tracking Script")
    script = f'<script async src="{api_url}/tracker" data-site="{selected_domain}"></script>'
    st.code(script, language="javascript")
    st.info("Copy this into the <head> of your site if you haven't yet.")

def show_chart(df):
    if df.empty:
        st.warning("No visit data avialable.")
        return
    st.metric("Total Visits", len(df))
    st.metric("Unique Visitor", df['ip'].nunique())

    df['date'] = pd.to_datetime(df['time']).dt.date
    st.subheader("📈 Visits Over Time")
    st.line_chart(df.groupby('date').size())
    st.subheader("🌍 Top Cities")
    st.bar_chart(df["city"].value_counts())
    st.subheader("🌐 Top Countries")
    st.bar_chart(df["country"].value_counts())

def display_traffic_data(api_url, selected_name):
    try:
        data = requests.get(f"{api_url}/data/{selected_name}").json()
        if data and isinstance(data, list):
            df = pd.DataFrame(data)
            df = df.drop(columns=['_sa_instance_state'], errors='ignore')
            st.write(f"Showing live data for: `{selected_name}`")
            st.dataframe(df, use_container_width=True)
            show_chart(df)
        else:
            st.info("No visitor data yet.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")

def show_dashboard(api_url):
    
    domain_options = fetch_websites(api_url)

    if domain_options:
        selected_name = st.selectbox("Select Website", list(domain_options.keys()))
        selected_domain = domain_options[selected_name]

        if selected_name:
            display_tracking_script(api_url, selected_name, selected_domain)
            display_traffic_data(api_url, selected_name)

    else:
        st.warning("No websites registered yet.")

# --- Main App Logic ---
def main():
    register_website(API_URL)
    show_dashboard(API_URL)

if __name__ == "__main__":
    main()
    st.rerun()