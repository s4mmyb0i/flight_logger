import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
from utils import load_airports, compute_durations, autofill_missing_airports, download_master_airports
import matplotlib.pyplot as plt

st.set_page_config(page_title="Flight Logger", layout="wide")
st.title("✈️ Samvit's Flights Since August 2019")
st.subheader("(When he moved to the United States)")

# Load data
download_master_airports()
autofill_missing_airports()
airports = load_airports()
flights = pd.read_csv("data/my_flights.csv")
flights["delayed"] = flights["delayed"].fillna(False).astype(bool)
flights["cancelled"] = flights["cancelled"].fillna(False).astype(bool)
flights = compute_durations(flights, airports)

# Map coordinates
def get_coords(code):
    try:
        row = airports.loc[code]
        return row["longitude_deg"], row["latitude_deg"]
    except:
        return None, None

flights["from_lon"], flights["from_lat"] = zip(*flights["from"].map(get_coords))
flights["to_lon"], flights["to_lat"] = zip(*flights["to"].map(get_coords))

# Filter out rows with missing coordinates
flights = flights.dropna(subset=["from_lon", "from_lat", "to_lon", "to_lat"])

# Arc attributes
trip_codes = flights["trip_name"].astype("category").cat.codes
cmap = plt.get_cmap("tab20")
flights["color"] = [
    [int(c * 255) for c in cmap(code % 20)[:3]]
    for code in trip_codes
]
flights["width"] = flights.apply(lambda r: 0.8 if r["delayed"] else (0.4 if r["cancelled"] else 1.5), axis=1)

# Assign a color per trip using a proper colormap
trip_codes = flights["trip_name"].astype("category").cat.codes
cmap = plt.get_cmap("tab20")  # or "tab10", "Set3", etc.

# ArcLayer
arc_layer = pdk.Layer(
    "ArcLayer",
    data=flights,
    get_source_position=["from_lon", "from_lat"],
    get_target_position=["to_lon", "to_lat"],
    get_width="width",
    get_source_color="color",
    get_target_color="color",
    pickable=True,
    auto_highlight=True,
)

# View and map
view = pdk.ViewState(latitude=20, longitude=0, zoom=1)
tooltip = {
    "html": "<b>{from} → {to}</b><br>{airline} {flight_number}<br>Duration: {flight_duration_minutes:.1f} mins",
    "style": {"color": "white"},
}

st.pydeck_chart(pdk.Deck(
    layers=[arc_layer],
    initial_view_state=view,
    tooltip=tooltip, # pyright: ignore[reportArgumentType]
    map_provider="carto",
    map_style="dark",
    parameters={"projection": "globe"}
))

unique_cities = pd.unique(flights.loc[~flights["cancelled"], ["from_city", "to_city"]].values.ravel())

# Dashboard
st.subheader("📊 Flight Stats")
col1, col2, col3 = st.columns(3)

# Filter out cancelled flights for calculations
valid_flights = flights[~flights["cancelled"]]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Flights", len(flights))
    st.metric("Delayed Flights", valid_flights["delayed"].astype(bool).sum())
    st.metric("Cumulative Delay (min)", int(valid_flights["delayed"].fillna(0).sum()))
    st.metric("Cancelled Flights", flights["cancelled"].sum())
    st.metric("Transfers", int(flights["arrival_transfer"].fillna(0).sum()))

with col2:
    st.metric("Countries Visited", flights.loc[~flights["cancelled"], "to_city"].nunique())
    st.metric("Cities Visited", len(unique_cities))
    if not flights["airline"].dropna().empty:
        st.metric("Favorite Airline", flights["airline"].mode().iloc[0])
    else:
        st.metric("Favorite Airline", "N/A")

with col3:
    avg = valid_flights["flight_duration_minutes"].mean()
    total = valid_flights["flight_duration_minutes"].sum()
    st.metric("Avg Duration (hrs)", f"{avg / 60:.1f}" if not np.isnan(avg) else "N/A")
    st.metric("Total Flight Time", f"{total / 60:.1f} hrs ({total / 60 / 24:.2f} days)")
    
    if "transfer_duration_minutes" in valid_flights:
        tavg = valid_flights["transfer_duration_minutes"].dropna().mean()
        tsum = valid_flights["transfer_duration_minutes"].dropna().sum()
        st.metric("Avg Transfer (hrs)", f"{tavg / 60:.1f}")
        st.metric("Total Transfer Time", f"{tsum / 60:.1f} hrs ({tsum / 60 / 24:.2f} days)")
