# ✈️ Flight Logger

A flight logger application built using Streamlit, Pydeck, and Pandas.

## 🌍 Overview

This project lets you log and visualize personal flight history on a 3D globe. It reads flight data from a CSV file, fills in missing airport information, and displays all your flights using arcs on an interactive globe.

## 🚀 Features

- Visualize flights on a globe using Pydeck + Carto basemaps
- Automatically fills missing airports from the [OurAirports](https://davidmegginson.github.io/ourairports-data/) database
- Computes and displays key statistics:
  - Total flights
  - Delayed flights
  - Cancelled flights
  - Transfers
  - Countries and cities visited
  - Total and average flight durations
  - Transfer time metrics
- Colored arcs per `trip_name` for visual grouping
- Time zone-aware calculations using `pytz`

## 🛠 Requirements

Install via `pip install -r requirements.txt`. Main packages:

- Python 3.8+
- `streamlit`
- `pydeck`
- `pandas`
- `numpy`
- `matplotlib`
- `pytz`
- `geopy`
- `timezonefinder`

## 📦 Usage

1. Place your flight log in `data/my_flights.csv` using the format below.
2. Run:

   ```bash
   streamlit run main.py
   ```

📄 Data Format

Your [data/my_flights.csv](data/my_flights.csv) should follow this schema:

Column	Description
from	IATA code of origin airport (e.g., LAX)
to	IATA code of destination airport (e.g., JFK)
departure_date	Departure date in YYYY-MM-DD
departure_time	Departure time in HH:MM
arrival_date	Arrival date in YYYY-MM-DD
arrival_time	Arrival time in HH:MM
from_city	City name of origin
to_city	City name of destination
airline	Airline name
flight_number	Flight number (can be string or int)
arrival_transfer	1 if this flight ends in a transfer, else 0
delayed	Delay duration in minutes
cancelled	1 if cancelled, else 0
trip_name	Name of the trip for grouping
notes	Freeform notes field

🗺 Airports Data
- Your app reads [data/airports.csv](data/airports.csv), which is auto-updated from OurAirports
- If new airports are found in your flights, they are fetched from a cached master file: data/airports_master.csv
- The master file includes all known public-use airports and heliports with IATA codes.

⏱ Time Zone Handling
- Time zone data is derived using timezonefinder and pytz.
- The app uses each airport’s geolocation to infer its time zone for accurate duration and transfer calculations.
- If a time zone cannot be determined, UTC is used as a fallback.
