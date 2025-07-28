import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import date, datetime
import json  
from pprint import pprint

load_dotenv()  

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def make_json_safe(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_safe(item) for item in obj]
    else:
        return obj


from datetime import datetime, date
from decimal import Decimal
import json

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



if __name__ == "__main__":
    # test usage
    log_refresh_time()
    last_refresh = pull_last_refresh()
    print(f"Last refresh time: {last_refresh}")
