import streamlit as st
import requests
import zipfile
import io

from datetime import datetime
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=30000, key="refresh")

st.set_page_config(
    page_title="Home Dashboard",
    page_icon="🏠",
    layout="wide"
)

hk_now = datetime.now(
    ZoneInfo("Asia/Hong_Kong")
)

st.title("🏠 Home Dashboard")

col1, col2 = st.columns(2)

# =====================
# BUS
# =====================

with col1:

    st.header("🚌 Citybus 99")

    try:

        url = (
            "https://rt.data.gov.hk/v2/transport/"
            "citybus/eta/CTB/002212/99"
        )

        data = requests.get(url, timeout=10).json()

        for bus in data["data"][:3]:

            if not bus["eta"]:
                continue

            eta = datetime.fromisoformat(
                bus["eta"]
            )

            mins = int(
                (eta - hk_now).total_seconds() / 60
            )

            if mins < 0:
                mins = 0

            st.write(
                f"{mins} 分鐘 ({eta.strftime('%H:%M')})"
            )

    except Exception as e:

        st.error(e)

# =====================
# WEATHER
# =====================

with col2:

    st.header("📍 銅鑼灣")

    try:

        weather = requests.get(
            "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=tc"
        ).json()

        temp = None

        for station in weather["temperature"]["data"]:

            if station["place"] == "跑馬地":

                temp = station["value"]
                break

        humidity = weather["humidity"]["data"][0]["value"]

        feels_like = round(
            temp + ((humidity - 40) / 10),
            1
        )

        st.write(f"🌡 {temp}°C")
        st.write(f"🥵 {feels_like}°C")
        st.write(f"💧 {humidity}%")

        st.subheader("☂ 未來兩小時")

        try:

            zip_url = (
                "https://data.weather.gov.hk/"
                "weatherAPI/hko_data/csdi/dataset/"
                "gridded_rainfall_nowcast.zip"
            )

            r = requests.get(
                zip_url,
                timeout=30
            )

            st.write(
                f"HTTP Status: {r.status_code}"
            )

            z = zipfile.ZipFile(
                io.BytesIO(r.content)
            )

            st.write("ZIP內容:")

            for name in z.namelist():

                st.write(name)

        except Exception as e:

            st.error(
                f"Rainfall Error: {e}"
            )

    except Exception as e:

        st.error(e)

st.divider()

st.write(
    hk_now.strftime(
        "%Y-%m-%d %H:%M:%S HKT"
    )
)
