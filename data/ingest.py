
# ingest.py
import requests
import pathlib
import datetime

URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+*+from+ps&format=csv"
today = datetime.date.today()
out_path = pathlib.Path("data") / f"ps_{today}.csv"
out_path.parent.mkdir(exist_ok=True)

print(f"Downloading exoplanet data to {out_path}")
resp = requests.get(URL, timeout=60)
out_path.write_bytes(resp.content)
print("✅ Done.")
