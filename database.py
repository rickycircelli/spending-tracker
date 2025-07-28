import os
from supabase import create_client, Client
from dotenv import load_dotenv
import json  
from pprint import pprint
from datetime import datetime, date
from decimal import Decimal
import pandas as pd

load_dotenv()  

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def make_json_safe(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_safe(item) for item in obj]
    else:
        return obj

def save_json_to_supabase(json_data: dict, name: str):
    safe_data = make_json_safe(json_data)

    data = {
        "name": str(name),
        "content": safe_data,
        "timestamp": datetime.now().isoformat()
    }

    response = supabase.table("json_data").insert(data).execute()

    if not response.data:
        print("❌ Supabase insert failed!")
    else:
        print("✅ Supabase insert successful!")

    return response

def log_refresh_time():
    now = datetime.now().isoformat()
    supabase.table("refresh_log").insert({"clicked_at": now}).execute()

def pull_last_refresh():
        response = supabase.table("refresh_log").select("*").order("clicked_at", desc=True).limit(1).execute()
        if response.data:
            return response.data[0]["clicked_at"]
        return None

def fetch_latest_json(prefix: str):
    response = supabase.table("json_data") \
        .select("*") \
        .ilike("name", f"{prefix}%") \
        .order("timestamp", desc=True) \
        .limit(1) \
        .execute()

    if response.data:
        return response.data[0]["content"]
    else:
        print(f"No data found for prefix '{prefix}'")
        return None

def transfrom_data():
    latest_saving_checking = fetch_latest_json("saving_checking")
    latest_credit = fetch_latest_json("credit")

    # --- saving and checking ---

    savings_balance = 0
    checking_balance = 0
    saving_checking_accounts = []

    for acct in latest_saving_checking.get("accounts_full", []):
        subtype = acct.get("subtype")
        balance = acct.get("balances", {}).get("current", 0)
        if subtype == "savings":
            savings_balance += balance
        elif subtype == "checking":
            checking_balance += balance
        saving_checking_accounts.append({
            "account_id": acct.get("account_id", "acc_saving_checking"),
            "name": acct.get("name", "Unnamed Account"),
            "subtype": subtype,
            "balance": balance,
        })

    pd.DataFrame(saving_checking_accounts).to_csv("data/saving_checking_accounts.csv", index=False)
    print("Saving and checking accounts saved to saving_checking_accounts.csv")

    checking_txns = []
    for txn in latest_saving_checking.get("transactions", []):
        pf_cat = txn.get("personal_finance_category", {})
        cat_list = [pf_cat.get("primary", ""), pf_cat.get("detailed", "")]
        cat_str = str([c for c in cat_list if c])
        
        checking_txns.append({
            "account_id": txn.get("account_id", "acc_credit"),
            "date": txn.get("date"),
            "name": txn.get("name"),
            "amount": txn.get("amount", 0),
            "category": cat_str,
            "transaction_type": txn.get("transaction_type", "unknown"),
            "merchant_name": txn.get("merchant_name", ""),
        })

    pd.DataFrame(checking_txns).to_csv("data/checking_transactions.csv", index=False)
    print("Checking transactions saved to checking_transactions.csv")

    # --- credit ---

    credit_txns = []
    for txn in latest_credit.get("transactions", []):
        pf_cat = txn.get("personal_finance_category", {})
        cat_list = [pf_cat.get("primary", ""), pf_cat.get("detailed", "")]
        cat_str = str([c for c in cat_list if c])
        
        credit_txns.append({
            "account_id": txn.get("account_id", "acc_credit"),
            "date": txn.get("date"),
            "name": txn.get("name"),
            "amount": txn.get("amount", 0),
            "category": cat_str,
            "transaction_type": txn.get("transaction_type", "unknown"),
            "merchant_name": txn.get("merchant_name", ""),
        })

    pd.DataFrame(credit_txns).to_csv("data/credit_transactions.csv", index=False)
    print("Credit transactions saved to credit_transactions.csv")

if __name__ == "__main__":
    # test usage
    log_refresh_time()
    last_refresh = pull_last_refresh()
    print(f"Last refresh time: {last_refresh}")
    transfrom_data()

