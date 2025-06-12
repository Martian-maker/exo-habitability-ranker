import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

from ingest import download_nasa_data
from preprocess import process_exoplanets  # you can define this

# Step 1: Download fresh data
csv_path = download_nasa_data()

# Step 2: Preprocess it (returns DataFrame)
df = process_exoplanets(csv_path)


st.set_page_config(page_title="Exoplanet Habitability Dashboard", layout="wide")

# === Load scored CSV ===
@st.cache_data
def load_data():
    return pd.read_csv("ranked_planets.csv")

df = load_data()

# === Header ===
st.title("🪐 Exoplanet Habitability Dashboard")
st.markdown("""
This dashboard ranks known exoplanets by a machine-calculated habitability score using the **TOPSIS** method.
You can filter, explore, and download the results.
""")

# === Filter by score ===
score_min = st.slider("Minimum Habitability Score", 0.0, 1.0, 0.85, step=0.01)
filtered = df[df["habit_score"] >= score_min].reset_index(drop=True)

# === Table ===
st.markdown(f"### 🔍 {len(filtered)} Planets with Habitability ≥ {score_min}")
st.dataframe(
    filtered[["pl_name", "radius", "temp", "flux", "habit_score"]],
    use_container_width=True
)

normalize_by = st.radio(
    "Choose normalization method:",
    ["Dataset Range", "Earth Reference"],
    index=0,
    horizontal=True
)


# === Select planet for radar plot ===
planet_name = st.text_input("🔎 Type a planet name from the list as printed for its " \
"comparative radar plot. (Note: For dataset range Percent scales reflect position within the entire exoplanet dataset, " \
"not Earth-like scale. Extreme planets (e.g., hot Jupiters) shift the range. For Earth reference, percentage represent " \
"how similar it is to the Earth- relative to the earth (e.g., x percent of the earth's radius)).", placeholder="e.g. Kepler-22 b")

if planet_name:
    match = df[df["pl_name"].str.lower() == planet_name.strip().lower()]
    
    if match.empty:
        st.warning("Planet not found. Please check the name or spelling.")
    else:
        row = match.iloc[0]
        labels = ["radius", "temp", "flux"]
        values = [row[c] for c in labels]
        earth_values = [1.0, 288.0, 1.0]  # Earth baseline

        if normalize_by == "Dataset Range":
            # Normalize using min-max of dataset
            min_vals = df[labels].min().values
            max_vals = df[labels].max().values
            scaled_values = (np.array(values) - min_vals) / (max_vals - min_vals)
            scaled_earth = (np.array(earth_values) - min_vals) / (max_vals - min_vals)
        else:
            # Normalize relative to Earth
            scaled_values = np.array(values) / np.array(earth_values)
            scaled_earth = np.ones_like(scaled_values)
            # Cap all values at 2.0 (200%) to avoid chart overflow
            scaled_values = np.clip(scaled_values, 0, 2.0)

        # Radar prep
        scaled_values = np.append(scaled_values, scaled_values[0])
        scaled_earth = np.append(scaled_earth, scaled_earth[0])
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw={'polar': True})
        ax.plot(angles, scaled_values, label=row["pl_name"], linewidth=2)
        ax.fill(angles, scaled_values, alpha=0.3)
        ax.plot(angles, scaled_earth, label="Earth", linestyle="--", color="gray")
        ax.fill(angles, scaled_earth, alpha=0.1, color="gray")

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)

        # Show proper radial labels
        if normalize_by == "Dataset Range":
            ax.set_yticks([0.25, 0.5, 0.75, 1.0])
            ax.set_yticklabels(["25%", "50%", "75%", "100%"])
        else:
            ax.set_yticks([0.5, 1.0, 1.5, 2.0])
            ax.set_yticklabels(["50%", "100%", "150%", "200%"])

        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
        st.pyplot(fig)




# === Download CSV ===
st.markdown("### 📥 Download Full Dataset")
st.download_button("Download ranked_planets.csv", df.to_csv(index=False), file_name="ranked_planets.csv")
