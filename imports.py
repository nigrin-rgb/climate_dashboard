import streamlit as st
import pandas as pd
from pathlib import Path
from matplotlib import pyplot as plt
import plotly.express as px
import numpy as np
import calendar


@st.cache_data
def load_gc():
    csv_path = Path(__file__).parent / "data" / "global_climate_events_economic_impact_2020_2025.csv"
    df = pd.read_csv(csv_path)

    df["year"] = df["year"].astype(int)
    df["month"] = pd.to_numeric(df.get("month"), errors="coerce")
    df["severity"] = pd.to_numeric(df["severity"], errors="coerce")
    df["economic_impact_million_usd"] = pd.to_numeric(df["economic_impact_million_usd"], errors="coerce")

    # Remove partial year 2025
    df = df[df["year"] < 2025].copy()

    return df