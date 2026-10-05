import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.environ["URL"]

response = requests.get(url)
with open("plan-zajec.ics", "wb") as f:
    f.write(response.content)