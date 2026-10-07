# ============================================================
# USGS EARTHQUAKE MINI PROJECT
# Python Data Collection and MySQL Storage
# ============================================================


# ============================================================
# 1. IMPORT LIBRARIES
# ============================================================

# requests is used to communicate with the USGS API
import requests

# pandas is used to create and work with the DataFrame
import pandas as pd

# datetime is used to define the project date range
from datetime import datetime

# pymysql is used to connect Python with MySQL
import pymysql

# SQLAlchemy is used to insert the Pandas DataFrame into MySQL
from sqlalchemy import create_engine


# ============================================================
# 2. USGS API ENDPOINT
# ============================================================

# This is the USGS Earthquake API endpoint.
# Our Python program sends earthquake data requests to this URL.
api_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"


# ============================================================
# 3. PROJECT DATE RANGE
# ============================================================

# Project starts on 25 September 2021
project_start = datetime(2021, 9, 25)

# Project ends on 25 September 2026
project_end = datetime(2026, 9, 25)


# ============================================================
# 4. CREATE EMPTY LIST
# ============================================================

# Each earthquake will be stored as one dictionary
# inside this list.
all_earthquakes = []


# ============================================================
# 5. COLLECT DATA MONTH BY MONTH
# ============================================================

# Start from the project start date
current_date = project_start


# Continue until the project end date is reached
while current_date < project_end:

    # --------------------------------------------------------
    # Find the beginning of the next month
    # --------------------------------------------------------

    if current_date.month == 12:

        next_date = datetime(
            current_date.year + 1,
            1,
            1
        )

    else:

        next_date = datetime(
            current_date.year,
            current_date.month + 1,
            1
        )


    # Do not go beyond the project end date
    if next_date > project_end:
        next_date = project_end


    # --------------------------------------------------------
    # API PARAMETERS
    # --------------------------------------------------------

    # These parameters tell the USGS API what data we want.
    api_parameters = {

        # Request data in GeoJSON format
        "format": "geojson",

        # Start date of this API request
        "starttime": current_date.strftime("%Y-%m-%d"),

        # End date of this API request
        "endtime": next_date.strftime("%Y-%m-%d"),

        # Include earthquakes with magnitude 0 or greater
        "minmagnitude": 0
    }


    # --------------------------------------------------------
    # SEND REQUEST TO USGS
    # --------------------------------------------------------

    response = requests.get(
        api_url,
        params=api_parameters
    )


    # --------------------------------------------------------
    # CHECK RESPONSE
    # --------------------------------------------------------

    # HTTP status code 200 means the request was successful
    if response.status_code != 200:

        print(
            "Request failed:",
            current_date.strftime("%Y-%m-%d"),
            response.status_code
        )

        # Move to the next month
        current_date = next_date

        continue


    # --------------------------------------------------------
    # CONVERT RESPONSE TO PYTHON DATA
    # --------------------------------------------------------

    try:

        # Convert JSON response into a Python dictionary
        earthquake_data = response.json()

    except Exception as error:

        print(
            "JSON error:",
            error
        )

        current_date = next_date

        continue


    # --------------------------------------------------------
    # EXTRACT EARTHQUAKE RECORDS
    # --------------------------------------------------------

    # "features" contains the individual earthquake records
    for earthquake in earthquake_data["features"]:

        # "properties" contains information such as
        # magnitude, place, time, alert, etc.
        properties = earthquake["properties"]

        # GeoJSON coordinates are:
        # [longitude, latitude, depth]
        coordinates = earthquake["geometry"]["coordinates"]


        # ----------------------------------------------------
        # STORE ONE EARTHQUAKE RECORD
        # ----------------------------------------------------

        all_earthquakes.append({

            # Unique earthquake ID
            "id": earthquake.get("id"),

            # Time when the earthquake occurred
            # USGS time is in milliseconds
            "time": pd.to_datetime(
                properties.get("time"),
                unit="ms"
            ),

            # Last updated time
            "updated": pd.to_datetime(
                properties.get("updated"),
                unit="ms"
            ),

            # Latitude
            "latitude": (
                coordinates[1]
                if coordinates
                else None
            ),

            # Longitude
            "longitude": (
                coordinates[0]
                if coordinates
                else None
            ),

            # Depth in kilometres
            "depth_km": (
                coordinates[2]
                if coordinates
                else None
            ),

            # Earthquake magnitude
            "mag": properties.get("mag"),

            # Magnitude calculation type
            "magType": properties.get("magType"),

            # Earthquake location
            "place": properties.get("place"),

            # Review status
            "status": properties.get("status"),

            # Tsunami indicator
            "tsunami": properties.get("tsunami"),

            # Significance score
            "sig": properties.get("sig"),

            # Reporting network
            "net": properties.get("net"),

            # Number of reporting stations
            "nst": properties.get("nst"),

            # Minimum distance to a station
            "dmin": properties.get("dmin"),

            # RMS travel-time residual
            "rms": properties.get("rms"),

            # Azimuthal gap
            "gap": properties.get("gap"),

            # Information about available products
            "types": properties.get("types"),

            # Event IDs
            "ids": properties.get("ids"),

            # Source identifiers
            "sources": properties.get("sources"),

            # Type of seismic event
            "type": properties.get("type"),

            # Magnitude error
            "magError": properties.get("magError"),

            # Depth error
            "depthError": properties.get("depthError"),

            # Number of stations used for magnitude
            "magNst": properties.get("magNst"),

            # Location source
            "locationSource": properties.get("locationSource"),

            # Magnitude source
            "magSource": properties.get("magSource"),

            # Number of people who reported feeling
            # the earthquake
            "felt": properties.get("felt"),

            # Community Internet Intensity
            "cdi": properties.get("cdi"),

            # Modified Mercalli Intensity
            "mmi": properties.get("mmi"),

            # Alert level
            "alert": properties.get("alert")
        })


    # --------------------------------------------------------
    # DISPLAY PROGRESS
    # --------------------------------------------------------

    print(
        "Collected:",
        current_date.strftime("%Y-%m-%d"),
        "to",
        next_date.strftime("%Y-%m-%d"),
        "-",
        len(earthquake_data["features"]),
        "earthquakes"
    )


    # Move to the next month
    current_date = next_date


# ============================================================
# 6. CREATE PANDAS DATAFRAME
# ============================================================

# Convert the list of dictionaries into a DataFrame
earthquake_df = pd.DataFrame(
    all_earthquakes
)


# Display number of rows
print(
    "Rows:",
    earthquake_df.shape[0]
)


# Display number of columns
print(
    "Columns:",
    earthquake_df.shape[1]
)


# Display first five rows
print(
    earthquake_df.head()
)


# ============================================================
# 7. MYSQL CONNECTION DETAILS
# ============================================================

# MySQL server
mysql_host = "localhost"

# MySQL username
mysql_user = "root"

# MySQL password
mysql_password = "2000"

# MySQL database name
mysql_database = "earthquake_db"


# ============================================================
# 8. TEST MYSQL CONNECTION
# ============================================================

try:

    # Connect to MySQL
    mysql_connection = pymysql.connect(

        host=mysql_host,

        user=mysql_user,

        password=mysql_password,

        database=mysql_database,

        cursorclass=pymysql.cursors.DictCursor
    )

    print(
        "Connected to MySQL successfully!"
    )


except Exception as error:

    print(
        "X Connection failed:",
        error
    )


# ============================================================
# 9. CREATE SQLALCHEMY ENGINE
# ============================================================

# SQLAlchemy allows Pandas to communicate with MySQL
mysql_engine = create_engine(
    f"mysql+pymysql://"
    f"{mysql_user}:{mysql_password}"
    f"@{mysql_host}/{mysql_database}"
)


# ============================================================
# 10. INSERT DATA INTO MYSQL
# ============================================================

# Insert the DataFrame into the MySQL table named EQ
earthquake_df.to_sql(

    # MySQL table name
    name="EQ",

    # SQLAlchemy connection
    con=mysql_engine,

    # Append means add the records to the table
    # without replacing existing records
    if_exists="append",

    # Do not create the Pandas index as a SQL column
    index=False
)


# ============================================================
# 11. FINAL PROJECT INFORMATION
# ============================================================

print(
    "Data inserted successfully!"
)

print(
    "Total earthquake records:",
    len(earthquake_df)
)

print(
    "Total columns:",
    len(earthquake_df.columns)
)