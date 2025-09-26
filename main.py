import joblib
import requests
import pandas as pd
import pvlib
from pvlib.location import Location
from datetime import datetime, timedelta

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
from streamlit_folium import st_folium
import folium


model = joblib.load(r"artifacts\solar_power_prediction_model.pkl")

scaler = joblib.load(r"artifacts\standardscaler.pkl")

def get_weather_features(lat, lon, start_date, end_date):
    """
    Fetch and summarize weather data for a given location and date range.
    Returns a single-row DataFrame with features like temp, rainfall, humidity.
    """

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "pressure_msl",
            "precipitation",
            "snowfall",
            "cloud_cover",
            "cloud_cover_high",
            "cloud_cover_mid",
            "cloud_cover_low",
            "shortwave_radiation",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m"
        ],
        "timezone": "auto"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if 'hourly' not in data:
        print("⚠️ Weather data not available for this location/date.")
        return pd.DataFrame()

    df = pd.DataFrame(data['hourly'])

    # Aggregate features over the season
    features = {
        "temperature_2_m_above_gnd": df["temperature_2m"].mean(),
        "relative_humidity_2_m_above_gnd": df["relative_humidity_2m"].mean(),
        "mean_sea_level_pressure_MSL": df["pressure_msl"].mean(),
        "total_precipitation_sfc": df["precipitation"].mean(),
        "snowfall_amount_sfc": df["snowfall"].mean(),
        "total_cloud_cover_sfc": df["cloud_cover"].mean(),
        "high_cloud_cover_high_cld_lay": df["cloud_cover_high"].mean(),
        "medium_cloud_cover_mid_cld_lay": df["cloud_cover_mid"].mean(),
        "low_cloud_cover_low_cld_lay": df["cloud_cover_low"].mean(),
        "shortwave_radiation_backwards_sfc": df["shortwave_radiation"].mean(),
        "wind_speed_10_m_above_gnd": df["wind_speed_10m"].mean(),
        "wind_direction_10_m_above_gnd": df["wind_direction_10m"].mean(),
        "wind_gust_10_m_above_gnd": df["wind_gusts_10m"].mean()
    }

    return pd.DataFrame([features])


def get_solar_feature(latitude, longitude, timezone="Asia/Kolkata", panel_tilt = 30, panel_azimuth=180):
    site = Location(latitude, longitude, timezone)
    times = pd.date_range(start=pd.Timestamp.now(tz=timezone), periods=24, freq='h')
    solar_position = site.get_solarposition(times)

    azimuth = solar_position['azimuth']
    zenith = solar_position['zenith']
    aoi = pvlib.irradiance.aoi(
        surface_tilt=panel_tilt,
        surface_azimuth=panel_azimuth,
        solar_zenith=zenith,
        solar_azimuth=azimuth
    )

    return pd.DataFrame({
        'angle_of_incidence': [aoi.mean()],
        'zenith': [zenith.mean()],
        'azimuth': [azimuth.mean()]
        })

def get_default_dates():
    today = datetime.now()
    start_date = (today - timedelta(days=2)).strftime('%Y-%m-%d')
    end_date = (today - timedelta(days=1)).strftime('%Y-%m-%d')

    return start_date, end_date




st.set_page_config(page_title="🔋 Solar Power Generation Predictor", layout="centered")

st.title("☀️ Solar Power Prediction App")
st.markdown("Predict solar power output based on your location and panel settings.")

st.subheader("📍 Select Location on Map")

# Default location (India center)
default_location = [20.5937, 78.9629]
m = folium.Map(location=default_location, zoom_start=5)

# Let user click on map
click_map = st_folium(m, height=500, width=700)

# Check if user clicked
if click_map and click_map.get("last_clicked"):
    latitude = click_map["last_clicked"]["lat"]
    longitude = click_map["last_clicked"]["lng"]
    st.success(f"Selected Location: Latitude = {latitude:.6f}, Longitude = {longitude:.6f}")
    
    # Panel settings
    st.subheader("🔧 Panel Settings")
    panel_tilt = st.slider("Panel Tilt Angle (degrees)", 0, 90, 30)

    azimuth_options = {
        "North (0°)": 0,
        "North-East (45°)": 45,
        "East (90°)": 90,
        "South-East (135°)": 135,
        "South (180°)": 180,
        "South-West (225°)": 225,
        "West (270°)": 270,
        "North-West (315°)": 315
    }
    azimuth_label = st.selectbox("Azimuth (Panel Facing Direction)", list(azimuth_options.keys()), index=4)
    panel_azimuth = azimuth_options[azimuth_label]

    # Submit button
    if st.button("⚡ Predict Solar Power"):
        start_date, end_date = get_default_dates()
        st.info("Fetching weather data...")

        weather_df = get_weather_features(latitude, longitude, start_date, end_date)

        if weather_df.empty:
            st.error("Weather data could not be retrieved.")
        else:
            st.success("Weather data loaded.")
            solar_df = get_solar_feature(latitude, longitude, panel_tilt=panel_tilt, panel_azimuth=panel_azimuth)
            inference_data = pd.concat([weather_df, solar_df], axis=1)

            # Scale & predict
            data_scaled = scaler.transform(inference_data)
            prediction = model.predict(data_scaled)

            st.subheader("🔋 Predicted Solar Power Output")
            st.success(f"Estimated Output: **{prediction[0]:.2f} kW**")

else:
    st.warning("Please click on the map to select a location.")


