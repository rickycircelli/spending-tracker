#import libraries
import json
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from plaid import ApiClient, Configuration
from plaid.api.plaid_api import PlaidApi
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from datetime import datetime, timedelta


# load .env 
load_dotenv()
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV")

# plaid client
configuration = Configuration(
    host=f"https://{PLAID_ENV}.plaid.com",
    api_key={
        "clientId": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
    },
)
api_client = ApiClient(configuration)
client = PlaidApi(api_client)

# load saved access token
with open("access_token.json", "r") as f:
    access_token = json.load(f)["access_token"]

# fetch account balances
def fetch_account_balances(access_token):
    request = AccountsBalanceGetRequest(access_token=access_token)
    response = client.accounts_balance_get(request)
    accounts = response["accounts"]
    return [
        {
            "name": account["name"],
            "current": account["balances"]["current"],
            "currency": account["balances"]["iso_currency_code"]
        }
        for account in accounts
    ]

# fetch transactions (last 30 days)
def fetch_transactions(access_token):
    start_date = datetime.now().date() - timedelta(days=30)
    end_date = datetime.now().date()
    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date,
        options=TransactionsGetRequestOptions(count=10, offset=0)
    )
    response = client.transactions_get(request)
    transactions = response["transactions"]
    return [
        {"date": txn["date"], "name": txn["name"], "amount": txn["amount"]}
        for txn in transactions
    ]

# fetch real sandbox data
balances = fetch_account_balances(access_token)
transactions = fetch_transactions(access_token)

# ---------- dashboard Layout -----------
st.title("Personal Spending Tracker")

# account balances 
st.header("Account Balances")
for account in balances:
    st.write(f"{account['name']}: {account['current']} {account['currency']}")

# transactions 
st.header("Recent Transactions")
transactions_df = pd.DataFrame(transactions)
st.dataframe(transactions_df)

# spending summary 
st.header("Spending Summary")
total_spent = sum(txn["amount"] for txn in transactions)
st.metric("Total Spent (Last 30 Days)", f"${total_spent:,.2f}")

# spending by merchant -> bar chart
st.header("Spending by Merchant")
merchant_spending = transactions_df.groupby("name")["amount"].sum().sort_values(ascending=False)

st.bar_chart(merchant_spending)

# spending over time -> line chart
st.header("Spending Over Time")
transactions_df["date"] = pd.to_datetime(transactions_df["date"])
daily_spending = transactions_df.groupby("date")["amount"].sum()

st.line_chart(daily_spending)
