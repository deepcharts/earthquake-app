import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import pytz

# Function to fetch earthquake data
def fetch_earthquake_data(url):
    response = requests.get(url)
    data = response.json()
    
    # Parse the data
    features = data['features']
    earthquakes = []
    for feature in features:
        properties = feature['properties']
        geometry = feature['geometry']
        utc_time = pd.to_datetime(properties['time'], unit='ms')
        local_time = utc_time.tz_localize('UTC').tz_convert(pytz.timezone('America/Los_Angeles'))  # Convert to local timezone
        earthquakes.append({
            "place": properties['place'],
            "magnitude": properties['mag'],
            "time_utc": utc_time,
            "time_local": local_time,
            "latitude": geometry['coordinates'][1],
            "longitude": geometry['coordinates'][0]
        })
    
    return pd.DataFrame(earthquakes)

# Fetch real-time earthquake data
realtime_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
realtime_earthquake_data = fetch_earthquake_data(realtime_url)

# Fetch historical earthquake data
historical_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
historical_earthquake_data = fetch_earthquake_data(historical_url)

# Streamlit app layout
st.title("Real-Time Earthquake Monitoring Webapp")
st.markdown("This app visualizes real-time and historical earthquake data from the US Geological Survey (USGS).")

# Filter by magnitude
min_magnitude = st.slider("Minimum Magnitude", min_value=0.0, max_value=10.0, value=1.0, step=0.1)
filtered_realtime_data = realtime_earthquake_data[realtime_earthquake_data["magnitude"] >= min_magnitude]
filtered_historical_data = historical_earthquake_data[historical_earthquake_data["magnitude"] >= min_magnitude]

# Create a Plotly map for real-time earthquakes
fig_realtime = px.scatter_mapbox(
    filtered_realtime_data,
    lat="latitude",
    lon="longitude",
    size="magnitude",
    color="magnitude",
    hover_name="place",
    hover_data={"time_utc": True, "time_local": True, "magnitude": True},
    zoom=1,
    height=600,
    title="Recent Earthquakes (Last Hour)"
)

# Create a Plotly map for historical earthquakes
fig_historical = px.scatter_mapbox(
    filtered_historical_data,
    lat="latitude",
    lon="longitude",
    size="magnitude",
    color="magnitude",
    hover_name="place",
    hover_data={"time_utc": True, "time_local": True, "magnitude": True},
    zoom=1,
    height=600,
    title="Historical Earthquakes (Last Month)"
)

fig_realtime.update_layout(mapbox_style="open-street-map")
fig_historical.update_layout(mapbox_style="open-street-map")

# Display the maps
st.plotly_chart(fig_realtime)
st.plotly_chart(fig_historical)

# Display the filtered raw data
st.subheader("Filtered Real-Time Earthquake Data")
st.write(filtered_realtime_data)

st.subheader("Filtered Historical Earthquake Data")
st.write(filtered_historical_data)

# Additional Information
st.sidebar.subheader("About This App")
st.sidebar.info(
    """
    This application fetches real-time and historical earthquake data from the USGS API and visualizes it on interactive maps.
    Use the slider to filter earthquakes by magnitude. The times are displayed in both UTC and local time.
    """
)
