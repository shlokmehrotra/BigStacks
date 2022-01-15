import requests

URL = "http://127.0.0.1:3000/connections"
PARAMS = {"room": "room"}
# PARAMS = {}

r = requests.get(url = URL, params = PARAMS)
print(r.json())
