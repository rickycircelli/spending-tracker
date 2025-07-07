#import libraries
import os
import json
from dotenv import load_dotenv
from plaid import ApiClient, Configuration
from plaid.api.plaid_api import PlaidApi
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from datetime import datetime, timedelta


# load api keys from .env
load_dotenv()
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV")

# set up plaid client
configuration = Configuration(
    host=f"https://{PLAID_ENV}.plaid.com",
    api_key={
        "clientId": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
    },
)
api_client = ApiClient(configuration)
client = PlaidApi(api_client)

# simulate a bank account connection in sandbox 
def create_public_token():
    request = SandboxPublicTokenCreateRequest(
        institution_id="ins_109508",  # First Platypus Bank
        initial_products=[Products("transactions")]
    )
    response = client.sandbox_public_token_create(request)
    return response["public_token"]

# exchange the public token for a permanent access token
def exchange_public_token(public_token):
    """Exchange a public_token for a permanent access_token."""
    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request)
    access_token = response["access_token"]
    item_id = response["item_id"]
    return access_token, item_id


# fetch account balances for the item
def get_account_balances(access_token):
    request = AccountsBalanceGetRequest(access_token=access_token)
    response = client.accounts_balance_get(request)
    return response["accounts"]



# fetch transactions for the past 30 days
def get_transactions(access_token, count=10):
    start_date = (datetime.now() - timedelta(days=30)).date()
    end_date = datetime.now().date()
    
    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date,
        options=TransactionsGetRequestOptions(
            count= count, 
            offset=0
        )
    )
    response = client.transactions_get(request)
    return response["transactions"]


# save access token to a file
def save_access_token(access_token):
    with open("access_token.json", "w") as f:
        json.dump({"access_token": access_token}, f)

# load access token from file
def load_access_token():
    with open("access_token.json", "r") as f:
        data = json.load(f)
    return data["access_token"]


# ------ Analyze Transactions ------

# Summarize total spending 
def summarize_transactions(transactions):
    total_spent = 0
    for txn in transactions:
        total_spent += txn["amount"]
    print(f"\nTotal Spent in Last 30 Days: {total_spent} USD")

# Summarize spending by category
def summarize_spending_by_category(transactions):
    category_totals = {}
    
    for txn in transactions:
        # Get the main category 
        category = txn["category"][0] if txn["category"] else "Uncategorized"
        amount = txn["amount"]
        
        # Sum amounts by category
        category_totals[category] = category_totals.get(category, 0) + amount
    
    # Print summary
    print("\nSpending by Category:")
    for category, total in category_totals.items():
        print(f"{category}: {total:.2f} USD")




if __name__ == "__main__":
    
    # Check if access token already exists
    try:
        # Try loading saved token first
        access_token = load_access_token()
        print("Loaded saved access token.")
    except FileNotFoundError:
        
        # exchange the public token for an access token
        public_token = create_public_token()
        access_token, item_id = exchange_public_token(public_token)
        
        # save the access token for future use
        save_access_token(access_token)

        print("Access token saved.")

    # get account balances
    balances = get_account_balances(access_token)
    print("\nAccount Balances:")
    for account in balances:
        print(f"{account['name']}: {account['balances']['current']} {account['balances']['iso_currency_code']}")

    # get transactions
    transactions = get_transactions(access_token)
    print("\nRecent Transactions:")
    for txn in transactions:
        print(f"{txn['date']} - {txn['name']}: {txn['amount']} {txn['iso_currency_code']}")
    
    # summarize transactions
    summarize_transactions(transactions)

    # summarize spending by category
    summarize_spending_by_category(transactions)


