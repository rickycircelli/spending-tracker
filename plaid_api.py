# import libraries
import os
from dotenv import load_dotenv
from plaid import ApiClient, Configuration
from plaid.api.plaid_api import PlaidApi
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

# Load API keys from .env
load_dotenv()
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV")

# Configure Plaid client
configuration = Configuration(
    host=f"https://{PLAID_ENV}.plaid.com",
    api_key={
        "clientId": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
    },
)

api_client = ApiClient(configuration)
client = PlaidApi(api_client)

# Create Link Token
def create_link_token():
    request = LinkTokenCreateRequest(
        user=LinkTokenCreateRequestUser(
            client_user_id="ricky_personal"
        ),
        client_name="Personal Spending Tracker",
        products=[Products("transactions")],  
        country_codes=[CountryCode("US")],    
        language="en",
    )
    response = client.link_token_create(request)
    return response["link_token"]

if __name__ == "__main__":
    link_token = create_link_token()
    print("Link Token:", link_token)

