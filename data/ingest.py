
import pandas as pd
import os

def download_nasa_data():
    url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+*+from+pscomppars&format=csv"
    dir_path = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(dir_path, "ps_latest.csv")
    df = pd.read_csv(url)
    df.to_csv(output_path, index=False)
    return output_path

