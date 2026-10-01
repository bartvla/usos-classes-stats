import os

import requests
from dotenv import load_dotenv

load_dotenv()

url = "https://usosapps.put.poznan.pl/services/tt/upcoming_ical"
params = {
    "lang": "pl",
    "user_id": os.environ["USOS_USER_ID"],
    "key": os.environ["USOS_API_KEY"],
}
response = requests.get(url, params=params)
response.raise_for_status()

with open("plan-zajec.ics", "wb") as f:
    f.write(response.content)
