import streamlit as st
import pandas as pd
from plaid.api import plaid_api
from datetime import datetime
from database import log_refresh_time, pull_last_refresh

st.title("Personal Spending Tracker")

# password protection
if "authenticated" not in st.session_state:
    password = st.text_input("Password", type="password")
    if st.button("Login") and password == st.secrets["dashboard_password"]:
        st.session_state["authenticated"] = True
    else:
        st.stop()

# function to format currency 
def format_currency(amount):
    return f"${amount:,.2f}"

# --------- pages ---------
page = st.sidebar.selectbox("Choose a page", ["Home", "Dashboard", "Subscriptions"])

# button to resync data (with confirmation)
if st.button("Refresh Data"):
    log_refresh_time()
    # Call function to fetch data
    # Call function to save data to database
    # Call function to transform data
        
last_refresh = pull_last_refresh()
st.caption(f"Last Refresh Time: {last_refresh}")

# --- page 1 ---
if page == "Home":
    st.title("Home")

    # credit card vs checking balance
    st.subheader("Credit Card vs Checking Balance")
    
    # net worth
    st.subheader("Net Worth")

# --- page 2 ---

elif page == "Dashboard":
    st.title("Dashboard")

    # Spending by Category
    st.subheader("Spending by Category (last 30 days)")
    

    # Spending by Merchant
    st.subheader("Spending by Merchant (last 30 days)")
   

    # Income vs Expenses
    st.subheader("Monthly Income vs Expenses")

    # spending per month
    st.subheader("Monthly Spending")
  

# --- page 3 ---

elif page == "Subscriptions":
    st.title("Subscriptions")





