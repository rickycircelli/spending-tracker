import os
import json
from datetime import date, timedelta
from dotenv import load_dotenv

from plaid.api import plaid_api
from plaid import Configuration, ApiClient
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions

from database import save_json_to_supabase

# Load credentials from .env
load_dotenv()

# Setup Plaid client
configuration = Configuration(
    host=f"https://{os.getenv('PLAID_ENV')}.plaid.com",
    api_key={
        "clientId": os.getenv("PLAID_CLIENT_ID"),
        "secret": os.getenv("PLAID_SECRET"),
    }
)
api_client = ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# Set date range (1 year back)
end_date = date.today()
start_date = end_date - timedelta(days=365)

def fetch_all_data(access_token=None):
    if access_token is None:
        print("No access token provided")
        pass
    access_token = os.getenv(access_token)

    # Get total transactions count to paginate
    all_transactions = []
    count = 500
    offset = 0

    # Initial fetch
    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date,
        options=TransactionsGetRequestOptions(count=count, offset=offset)
    )
    response = client.transactions_get(request)
    total_transactions = response.total_transactions
    all_transactions.extend(response.transactions)

    # Paginate if needed
    while len(all_transactions) < total_transactions:
        offset += count
        request.options.offset = offset
        paged_response = client.transactions_get(request)
        all_transactions.extend(paged_response.transactions)

    # Get account info (real-time balances, metadata)
    account_request = AccountsGetRequest(access_token=access_token)
    account_response = client.accounts_get(account_request)

    # Convert all objects to serializable dicts
    transactions_json = [t.to_dict() for t in all_transactions]
    accounts_json = [a.to_dict() for a in account_response.accounts]

    return {
        "transactions": transactions_json,
        "accounts_full": accounts_json,
        "item": account_response.item.to_dict()
    }

if __name__ == "__main__":
    data_credit= fetch_all_data("PLAID_ACCESS_TOKEN_CREDIT")
    data_saving_checking = fetch_all_data("PLAID_ACCESS_TOKEN")
    os.makedirs("data", exist_ok=True)

    # Save to database
    filename_saving_checking = f"saving_checking_{date.today().strftime('%Y%m%d')}"
    save_json_to_supabase(data_saving_checking, filename_saving_checking)

    filename_credit = f"credit_{date.today().strftime('%Y%m%d')}"
    save_json_to_supabase(data_credit, filename_credit)
    
    print(f"Saved data to {filename_saving_checking} and {filename_credit}")



