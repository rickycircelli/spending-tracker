# add all dashbaord functions here
from database import fetch_latest_json
import json  


latest_saving_checking = fetch_latest_json("saving_checking")
latest_credit = fetch_latest_json("credit")

print("✅ Latest saving_checking JSON:")
print(json.dumps(latest_saving_checking, indent=2))

print("✅ Latest credit JSON:")
print(json.dumps(latest_credit, indent=2))


