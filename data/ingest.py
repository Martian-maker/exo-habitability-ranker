
# data/ingest.py
"""
Download the most-recent Planetary Systems Compiled Parameters (pscomppars) table
from the NASA Exoplanet Archive and save it as ps_latest.csv next to this script.

Usage:
    from ingest import download_nasa_data
    csv_path = download_nasa_data()
"""

import os
import datetime as dt
import pandas as pd

URL = (
    "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?"
    "query=select+*+from+pscomppars&format=csv"
)

def download_nasa_data():
    """Download the archive CSV (once per day) and return the local file path."""
    dir_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(dir_path, "ps_latest.csv")

    # Skip download if we fetched it today already
    if os.path.exists(csv_path):
        mtime = dt.datetime.fromtimestamp(os.path.getmtime(csv_path))
        if mtime.date() == dt.date.today():
            return csv_path  # up-to-date

    # Download via pandas (handles gzip automatically)
    print("🔄 Downloading latest exoplanet table …")
    df = pd.read_csv(URL)
    df.to_csv(csv_path, index=False)
    print(f"✅ Saved {len(df):,} rows to {csv_path}")
    return csv_path


# When run directly: grab the file and report size
if __name__ == "__main__":
    p = download_nasa_data()
    print("Local file:", p)

