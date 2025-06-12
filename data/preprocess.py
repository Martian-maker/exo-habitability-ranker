import pandas as pd
import numpy as np
import pathlib
import os

def process_exoplanets(input_path):
    df = pd.read_csv(input_path)
    df = df[["pl_name", "pl_rade", "pl_eqt", "st_teff", "st_lum"]].copy()
    df.columns = ["pl_name", "radius", "temp", "star_temp", "star_lum"]
    df = df.dropna()
    
    # Calculate habitability score using TOPSIS
    data = df[["radius", "temp", "star_temp", "star_lum"]].values
    norm = data / np.sqrt((data ** 2).sum(axis=0))
    weights = np.array([0.3, 0.3, 0.2, 0.2])
    ideal = norm.max(axis=0)
    anti_ideal = norm.min(axis=0)
    dist_pos = np.sqrt(((norm - ideal) ** 2 * weights).sum(axis=1))
    dist_neg = np.sqrt(((norm - anti_ideal) ** 2 * weights).sum(axis=1))
    scores = dist_neg / (dist_pos + dist_neg)
    df["habit_score"] = scores

    return df.sort_values("habit_score", ascending=False)
