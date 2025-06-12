import pandas as pd
import pandas as pd
import numpy as np
import os
import pathlib

def process_exoplanets(input_path):
    df = pd.read_csv(input_path)

    # Keep & rename only the columns we need
    df = df[["pl_name", "pl_rade", "pl_eqt", "st_teff", "st_lum"]].copy()
    df.columns = ["pl_name", "radius", "temp", "star_temp", "star_lum"]
    df = df.dropna()

    # Compute incident flux (relative to Earth)
    df["flux"] = df["star_lum"] / ((df["star_temp"] / 5778) ** 2)

    # Prepare for TOPSIS
    features = ["radius", "temp", "flux"]
    X = df[features]
    X = (X - X.mean()) / X.std()   # z-score

    # TOPSIS function
    def topsis(matrix, weights, benefit):
        norm = matrix / np.sqrt((matrix ** 2).sum(axis=0))
        wtd = norm * weights
        ideal = np.where(benefit, wtd.max(0), wtd.min(0))
        nadir = np.where(benefit, wtd.min(0), wtd.max(0))
        d_pos = np.linalg.norm(wtd - ideal, axis=1)
        d_neg = np.linalg.norm(wtd - nadir, axis=1)
        return d_neg / (d_pos + d_neg)

    weights = np.array([0.4, 0.3, 0.3])      # radius, temp, flux
    benefit = np.array([False, False, True]) # flux is “more is better”

    df["habit_score"] = topsis(X.values, weights, benefit)
    return df.sort_values("habit_score", ascending=False)


