**Flight Logger**
================

A web-based flight logger application built using Streamlit, Pydeck, and Pandas.

**Overview**
------------

This project is a flight logger that allows users to visualize their flight data on a map. The application reads in flight data from a CSV file, processes the data, and displays it on a globe using Pydeck. The application also provides various statistics and metrics about the flights.

**Features**
------------

* Visualize flight data on a globe using Pydeck
* Display flight statistics and metrics, including:
	+ Total flights
	+ Delayed flights
	+ Cancelled flights
	+ Average flight duration
	+ Total flight time
	+ Average transfer time
	+ Total transfer time
* Filter out cancelled flights for calculations
* Display unique cities visited

**Requirements**
---------------

* Python 3.x
* Streamlit
* Pydeck
* Pandas
* Pytz
* Geopy

**Usage**
-----

1. Input your flight data CSV file to the application
2. Install the required libraries using `pip install -r requirements.txt`
3. Run the application using `streamlit run main.py`

**Data Format**
-------------

Input your flight details in [`my_flights.csv`](data/my_flights.csv). The flight data CSV file should have the following columns:

* `from`: departure iata airport code (str (3 char))
* `to`: arrival iata airport code (str (3 char))
* `departure_date`: departure date in YYYY-MM-DD format
* `departure_time`: departure time in HH:MM format
* `arrival_date`: arrival date in YYYY-MM-DD format
* `arrival_time`: arrival time in HH:MM format
* `from_city`: departure city name (str)
* `to_city`: arrival city name (str)
* `airline`: airline name (str)
* `flight_number`: flight number (int)
* `arrival_transfer`: if the arrival airport is a transfer flight (0 or 1)
* `delayed`: how long the flight was delayed (float)
* `cancelled`: how many times the flight was cancelled (int)
* `trip_name`: trip name (str)
* `notes`: any additional info (any)

**Airports Data**
----------------

The airports data is stored in a CSV file named [`airports.csv`](data/airports.csv) in the `data` directory. This file should have the following columns:

This info is generated using the [`airports_master`](data/airports_master.csv) file from [David Megginson's GitHub](https://davidmegginson.github.io/ourairports-data/)

**Notes**
-------

* This project uses the `pytz` library to handle time zones. If a time zone is not specified for an airport, the application will use the default time zone.
* The application assumes that the flight data is in the same time zone as the departure airport.
* The application uses the `geopy` library to geocode airport codes. If an airport code is not found, the application will use the default coordinates.