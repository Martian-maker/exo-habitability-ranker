import pandas as pd
import pandas as pd
import numpy as np
import os
import pathlib

def process_exoplanets(input_path):
    df = pd.read_csv(input_path)

    # Keep & rename only the columns we need
    df = df.rename(columns={
        "pl_name": "pl_name",
        "pl_rade": "radius",
        "pl_eqt": "temp",
        "st_teff": "star_temp",
        "st_lum": "star_lum",
        "pl_orbsmax": "orb_distance"
    })

    # Drop rows with missing required fields
    df.dropna(subset=["pl_name", "radius", "temp", "star_temp", "star_lum", "orb_distance"], inplace=True)
    
    # Compute incident flux (relative to Earth)
    df["flux"] = (df["star_lum"]) / (df["orb_distance"]**2)
    #star_lum here is a logarithmic tar luminosity relative to the sun so antiloging first

    # Prepare for TOPSIS
    features = ["radius", "temp", "flux"]
    X = df[features]
    X = (X - X.mean()) / X.std()   # z-score

    # TOPSIS function
    def topsis(matrix, weights, benefit):
        norm = matrix / np.sqrt((matrix ** 2).sum(axis=0))
        weighted = norm * weights
        ideal = np.where(benefit, weighted.max(0), weighted.min(0))
        nadir = np.where(benefit, weighted.min(0), weighted.max(0))
        d_pos = np.linalg.norm(weighted - ideal, axis=1)
        d_neg = np.linalg.norm(weighted - nadir, axis=1)
        score = d_neg / (d_pos + d_neg)
        return score

    weights = np.array([0.4, 0.3, 0.3])      # radius, temp, flux
    benefit = np.array([False, False, True]) # flux is “more is better”

    df["habit_score"] = topsis(X.values, weights, benefit)
    return df.sort_values("habit_score", ascending=False)


