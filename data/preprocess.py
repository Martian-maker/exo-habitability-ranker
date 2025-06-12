import pandas as pd
import pandas as pd
import numpy as np
import os
import pathlib

def process_exoplanets(input_path):
    df = pd.read_csv(input_path)

    # === Filter and rename relevant columns ===
    df = df[["pl_name", "pl_rade", "pl_eqt", "st_teff", "st_lum"]].copy()
    df.columns = ["pl_name", "radius", "temp", "star_temp", "star_lum"]
    df = df.dropna()

    # === Approximate flux from star_lum and star_temp ===
    df["flux"] = df["star_lum"] / ((df["star_temp"] / 5778) ** 2)

    # === TOPSIS Calculation ===
    features = ["radius", "temp", "flux"]
    X = df[features].copy()

    # Z-score normalization
    X = (X - X.mean()) / X.std()

    # TOPSIS Scoring
    def topsis(matrix, weights, benefit):
        norm = matrix / np.sqrt((matrix ** 2).sum(axis=0))
        weighted = norm * weights
        ideal = np.where(benefit, weighted.max(0), weighted.min(0))
        nadir = np.where(benefit, weighted.min(0), weighted.max(0))
        d_pos = np.linalg.norm(weighted - ideal, axis=1)
        d_neg = np.linalg.norm(weighted - nadir, axis=1)
        score = d_neg / (d_pos + d_neg)
        return score

    weights = np.array([0.4, 0.3, 0.3])     # radius, temp, flux
    benefit = np.array([False, False, True])

    df["habit_score"] = topsis(X.values, weights, benefit)

    return df.sort_values("habit_score", ascending=False)

