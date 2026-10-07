import streamlit as st
import pandas as pd
import pymysql
from sqlalchemy import create_engine


# MySQL database details

db_host = "localhost"
db_user = "root"
db_password = "YOUR_MYSQL_PASSWORD"
db_name = "earthquake_db"


# Create connection between Python and MySQL

engine = create_engine(
    f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}"
)


# Streamlit page title

st.title("Global Seismic Trends: Data-Driven Earthquake Insights")


# Task 1: Find the top 10 strongest earthquakes

query = """
SELECT
    id,
    time,
    place,
    mag,
    depth_km,
    magType
FROM earthquakes
ORDER BY mag DESC
LIMIT 10;
"""


# Execute the SQL query and store the result in a Pandas DataFrame

result = pd.read_sql(query, engine)


# Display the result in Streamlit

st.subheader("Top 10 Strongest Earthquakes")
st.dataframe(result)

