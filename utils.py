import pandas as pd
from datetime import datetime
import pytz
import streamlit as st
from timezonefinder import TimezoneFinder
import urllib.request
import os

@st.cache_data
def load_airports(path="data/airports.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df.set_index("iata_code", inplace=True)
    return df

def get_timezone(iata: str, airports: pd.DataFrame):
    try:
        return pytz.timezone(airports.loc[iata]["time_zone"]) # pyright: ignore[reportArgumentType]
    except Exception:
        return None

def make_datetime(date_str: str, time_str: str, timezone) -> datetime | None:
    local = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    if timezone:
        return timezone.localize(local)
    return None

def compute_durations(df: pd.DataFrame, airports: pd.DataFrame) -> pd.DataFrame:
    durations = []
    transfers = {}

    for idx, row in df.iterrows():
        tz_dep = get_timezone(row["from"], airports)
        tz_arr = get_timezone(row["to"], airports)
        dt_dep = make_datetime(row["departure_date"], row["departure_time"], tz_dep)
        dt_arr = make_datetime(row["arrival_date"], row["arrival_time"], tz_arr)
        if dt_dep and dt_arr:
            utc_dep = dt_dep.astimezone(pytz.UTC)
            utc_arr = dt_arr.astimezone(pytz.UTC)
            duration = (utc_arr - utc_dep).total_seconds() / 60
        else:
            duration = None
        durations.append(duration)

        # Store arrival time for next leg transfer calculation
        trip = row["trip_name"]
        if trip not in transfers:
            transfers[trip] = []
        transfers[trip].append((idx, utc_arr if dt_arr else None)) # pyright: ignore[reportPossiblyUnboundVariable]

    df["flight_duration_minutes"] = durations

    # Transfer durations
    transfer_durations = [None] * len(df)
    for trip, stops in transfers.items():
        stops.sort()
        for i in range(len(stops) - 1):
            idx1, arr1 = stops[i]
            idx2, _ = stops[i + 1]
            if arr1 and df.loc[idx2, "departure_time"]:
                dt_next_dep = make_datetime(df.loc[idx2, "departure_date"], df.loc[idx2, "departure_time"], # pyright: ignore[reportArgumentType]
                                            get_timezone(df.loc[idx2, "from"], airports)) # pyright: ignore[reportArgumentType]
                if dt_next_dep:
                    utc_next_dep = dt_next_dep.astimezone(pytz.UTC)
                    transfer_durations[idx1] = (utc_next_dep - arr1).total_seconds() / 60
    df["transfer_duration_minutes"] = transfer_durations
    return df

def download_master_airports(
    download_url="https://davidmegginson.github.io/ourairports-data/airports.csv",
    output_path="data/airports_master.csv",
    force: bool = False) -> pd.DataFrame:
    """
    Downloads the latest airports.csv from OurAirports if it doesn't exist locally
    or if force=True. Saves it to data/airports_master.csv.
    Returns the DataFrame.
    """
    if not os.path.exists("data"):
        os.makedirs("data")
    
    if not os.path.isfile(output_path) or force:
        print("🔄 Downloading latest airports.csv from OurAirports...")
        urllib.request.urlretrieve(download_url, output_path)
        print("✅ Download complete.")
    else:
        print("✔️ Using cached airports_master.csv")

    return pd.read_csv(output_path)

def autofill_missing_airports(
    flights_path="data/my_flights.csv",
    airports_path="data/airports.csv",
    master_path="data/airports_master.csv"
) -> None:
    tf = TimezoneFinder()

    # Load data
    flights = pd.read_csv(flights_path)
    airports = pd.read_csv(airports_path).set_index("iata_code")
    master = pd.read_csv(master_path)

    # Get all IATA codes from 'from' and 'to' columns
    all_codes = pd.unique(flights[["from", "to"]].values.ravel())
    all_codes = [code for code in all_codes if isinstance(code, str) and len(code) == 3]

    # Identify missing codes
    missing = [code for code in all_codes if code not in airports.index]

    if not missing:
        print("✅ No missing airports.")
        return

    print(f"🛬 Missing {len(missing)} airport(s): {missing}")

    # Filter valid IATA airports
    master = master.rename(columns={"iso_country": "country"})
    master = master[master["iata_code"].apply(lambda x: isinstance(x, str) and len(x) == 3)]
    subset = master[master["iata_code"].isin(missing)][[
        "iata_code", "latitude_deg", "longitude_deg", "municipality", "country"
    ]].dropna(subset=["latitude_deg", "longitude_deg"]).drop_duplicates()

    if subset.empty:
        print("⚠️ No valid data found for missing airports.")
        return

    # Compute time zone from lat/lon
    subset["time_zone"] = subset.apply( # pyright: ignore[reportCallIssue]
        lambda row: tf.timezone_at(lat=row["latitude_deg"], lng=row["longitude_deg"]), # pyright: ignore[reportArgumentType]
        axis=1
    ) # pyright: ignore[reportCallIssue, reportCallIssue, reportCallIssue]

    # Fill missing time zones if any (fallback to `timezone_at_land`)
    subset["time_zone"] = subset.apply(
        lambda row: tf.closest_timezone_at(lat=row["latitude_deg"], lng=row["longitude_deg"])  # pyright: ignore[reportAttributeAccessIssue]
        if pd.isna(row["time_zone"]) else row["time_zone"],
        axis=1
    )

    # Combine and save
    updated_airports = pd.concat([airports.reset_index(), subset]).drop_duplicates(subset="iata_code")
    updated_airports.to_csv(airports_path, index=False)

    print(f"✅ Added {len(subset)} airport(s) with inferred time zones to {airports_path}.")