import pandas as pd
from datetime import datetime

def transformar(df):
    df = df[["external", "cheapest"]].copy()
    df["cheapest"] = df["cheapest"].astype(float)
    df["fecha_extraccion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = df.sort_values("cheapest")
    return df