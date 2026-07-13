"""
data_prep.py

Loads the raw NDVI + precipitation panel (from Google Earth Engine) and
constructs the Rainfall Index (RI) used in the regression:

    RI_it = (Precip_it / mean(Precip_i)) * 100

This mirrors the construction of USDA RMA's actual Rainfall Index
product, where 100 = a county's own long-run average precipitation for
the period.
"""

import pandas as pd

DATA_PATH = "data/ndvi_precip_panel.csv"


def load_panel(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.rename(columns={"NAME": "county"})
    return df


def build_rainfall_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    county_avg_precip = df.groupby("county")["precip_mm"].transform("mean")
    df["rainfall_index"] = (df["precip_mm"] / county_avg_precip) * 100
    return df


if __name__ == "__main__":
    panel = load_panel()
    panel = build_rainfall_index(panel)
    print(panel.head(10))
    print(f"\n{len(panel)} county-year observations")
    print(f"{panel['county'].nunique()} counties, "
          f"{panel['year'].nunique()} years")
