import pandas as pd
import numpy as np
import pathlib
import os


# === Load latest CSV ===
data_dir = pathlib.Path("data")
latest_csv = sorted(data_dir.glob("ps_*.csv"))[-1]  # get the most recent file
df = pd.read_csv(latest_csv)

# === Keep only needed columns ===
cols_needed = ["pl_name", "pl_rade", "pl_eqt", "st_teff", "st_lum"]
df = df[cols_needed].dropna()

# === Rename for convenience ===
df = df.rename(columns={
    "pl_rade": "radius",
    "pl_eqt": "temp",
    "st_teff": "star_temp",
    "st_lum": "star_lum"
})

# === Compute incident flux (F = L / a²) ===
# Approximate semi-major axis using Stefan-Boltzmann scaling
# Not super accurate but good enough when 'a' is not given
# F_earth = 1 → so F relative = star_lum / approx_dist²
df["flux"] = df["star_lum"] / ((df["star_temp"] / 5778) ** 2)

# === Normalize features for TOPSIS ===
features = ["radius", "temp", "flux"]
X = df[features].copy()

# Z-score normalization
X = (X - X.mean()) / X.std()

# === TOPSIS scoring ===
def topsis(matrix, weights, benefit):
    norm = matrix / np.sqrt((matrix ** 2).sum(axis=0))
    weighted = norm * weights
    ideal = np.where(benefit, weighted.max(0), weighted.min(0))
    nadir = np.where(benefit, weighted.min(0), weighted.max(0))
    d_pos = np.linalg.norm(weighted - ideal, axis=1)
    d_neg = np.linalg.norm(weighted - nadir, axis=1)
    score = d_neg / (d_pos + d_neg)
    return score

# Define weights and benefit directions
weights = np.array([0.4, 0.3, 0.3])  # radius, temp, flux
benefit = np.array([False, False, True])  # smaller radius/temp = better; higher flux = better

df["habit_score"] = topsis(X.values, weights, benefit)

# === Sort and save output ===
df_sorted = df.sort_values("habit_score", ascending=False)
# Get the current script directory (data/)
dir_path = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(dir_path, "ranked_planets.csv")

df_sorted.to_csv(output_path, index=False)

# === Save pretty version as .txt for better readability ===
with open("ranked_planets_pretty.txt", "w") as f:
    f.write(df_sorted.to_string(index=False, float_format="%.3f"))


print(f"✅ Scored {len(df_sorted)} planets. Output saved to ranked_planets.csv")
