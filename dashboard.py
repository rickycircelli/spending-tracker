import streamlit as st
import pandas as pd
from plaid.api import plaid_api
from datetime import datetime
from database import log_refresh_time, pull_last_refresh, save_json_to_supabase, make_json_safe, transfrom_data
from dash_functions import net_worth, spending_per_cat, spending_per_cat_pie, spending_per_month, supscriptions, income_expenses, credit_checking, spending_per_merchant
from fetcher import fetch_and_save

st.title("Personal Spending Tracker")

# password protection
if "authenticated" not in st.session_state:
    password = st.text_input("Password", type="password")
    if st.button("Login") and password == st.secrets["dashboard_password"]:
        st.session_state["authenticated"] = True
    else:
        st.stop()

# make sure we have latest data uploaded and saved in data folder
if "data_loaded" not in st.session_state:
    transfrom_data()
    st.session_state["data_loaded"] = True
    print("Data transformed and saved to data folder")

# function to format currency 
def format_currency(amount):
    return f"${amount:,.2f}"

# --------- pages ---------
page = st.sidebar.selectbox("Choose a page", ["Home", "Dashboard", "Subscriptions"])

# button to resync data (with confirmation)
if st.button("Resync Data"):
    log_refresh_time()
    fetch_and_save() 
    transfrom_data() # stored locally in data folder
        
last_refresh = pull_last_refresh()
st.caption(f"Last Refresh Time: {last_refresh}")

# --- page 1 ---
if page == "Home":
    st.title("Home")

    # credit card vs checking balance
    st.subheader("Credit Card vs Checking Balance")
    credit_checking()
    
    # net worth
    st.subheader("Net Worth")
    net_worth()

# --- page 2 ---

elif page == "Dashboard":
    st.title("Dashboard")

    # Spending by Category
    st.subheader("Spending by Category (last 30 days)")
    spending_per_cat()
    spending_per_cat_pie()

    # Spending by Merchant
    st.subheader("Spending by Merchant (last 30 days)")
    spending_per_merchant()
   
    # Income vs Expenses
    st.subheader("Monthly Income vs Expenses")
    income_expenses()

    # spending per month
    st.subheader("Monthly Spending")
    spending_per_month()
  

# --- page 3 ---

elif page == "Subscriptions":
    st.title("Subscriptions")
    supscriptions()





