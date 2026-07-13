import streamlit as st
import requests
import pandas as pd

from datetime import datetime
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh

# ==================================
# Auto Refresh
# ==================================

st_autorefresh(
    interval=30000,
    key="refresh"
)

# ==================================
# Page Config
# ==================================

st.set_page_config(
    page_title="Home Dashboard",
    page_icon="🏠",
    layout="wide"
)

# ==================================
# Hong Kong Time
# ==================================

hk_now = datetime.now(
    ZoneInfo("Asia/Hong_Kong")
)

# ==================================
# Helper
# ==================================

def rain_text(mm):

    if mm <= 0:
        return "無降雨"

    elif mm < 0.5:
        return "微雨"

    elif mm < 2:
        return "小雨"

    elif mm < 10:
        return "中雨"

    else:
        return "大雨"


# ==================================
# Title
# ==================================

st.title("🏠 Home Dashboard")

# ==================================
# Layout
# ==================================

col1, col2 = st.columns(2)

# ==================================
# BUS
# ==================================

with col1:

    st.header("🚌 Citybus 99")

    try:

        bus_url = (
            "https://rt.data.gov.hk/v2/transport/"
            "citybus/eta/CTB/002212/99"
        )

        bus_data = requests.get(
            bus_url,
            timeout=10
        ).json()

        buses = bus_data["data"][:3]

        for bus in buses:

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
                f"🚌 {mins} 分鐘"
            )

    except:

        st.error("無法取得巴士資料")

# ==================================
# WEATHER
# ==================================

with col2:

    st.header("📍 銅鑼灣")

    try:

        weather_url = (
            "https://data.weather.gov.hk/"
            "weatherAPI/opendata/weather.php"
            "?dataType=rhrread&lang=tc"
        )

        weather = requests.get(
            weather_url,
            timeout=10
        ).json()

        # 跑馬地最接近銅鑼灣

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

        # ==========================
        # Rainfall Nowcast
        # ==========================

        st.subheader("☂ 未來兩小時")

        try:

            csv_url = (
                "https://data.weather.gov.hk/"
                "weatherAPI/hko_data/csdi/dataset/"
                "gridded_rainfall_nowcast.csv"
            )

            df = pd.read_csv(csv_url)

            lat_col = df.columns[8]
            lon_col = df.columns[9]
            rain_col = df.columns[7]

            causeway_bay_lat = 22.2803
            causeway_bay_lon = 114.1849

            df["distance"] = (
                (df[lat_col] - causeway_bay_lat) ** 2 +
                (df[lon_col] - causeway_bay_lon) ** 2
            )

            nearest = df.sort_values(
                "distance"
            )

            nearest_point = nearest.iloc[0]

            point_lat = nearest_point[lat_col]
            point_lon = nearest_point[lon_col]

            rain_forecast = df[
                (df[lat_col] == point_lat)
                &
                (df[lon_col] == point_lon)
            ].head(4)

            for _, row in rain_forecast.iterrows():

                hh = int(row.iloc[3])
                mm = int(row.iloc[4])

                rain_mm = float(
                    row[rain_col]
                )

                st.write(
                    f"{hh:02d}:{mm:02d}"
                )

                st.write(
                    rain_text(rain_mm)
                )

        except:

            st.write("無法取得降雨預報")

        # ==========================
        # Warning
        # ==========================

        warning_text = []

        warn_url = (
            "https://data.weather.gov.hk/"
            "weatherAPI/opendata/weather.php"
            "?dataType=warnsum&lang=tc"
        )

        warn_data = requests.get(
            warn_url,
            timeout=10
        ).json()

        code_map = {

            "WHOT": "🔥 酷熱天氣",

            "WRAINY": "🟡 黃色暴雨",

            "WRAINR": "🔴 紅色暴雨",

            "WRAINB": "⚫ 黑色暴雨",

            "WTS": "⛈ 雷暴",

            "WTCSGNL1": "🌀 1號風球",

            "WTCSGNL3": "🌀 3號風球",

            "WTCSGNL8": "🌀 8號風球"
        }

        for code in warn_data.keys():

            if code in code_map:

                warning_text.append(
                    code_map[code]
                )

        if warning_text:

            st.subheader("⚠ 天氣警告")

            for item in warning_text:

                st.write(item)

        # ==========================
        # Advice
        # ==========================

        st.subheader("🚶 出門建議")

        advice = []

        if feels_like >= 33:

            advice.append(
                "🔥 天氣炎熱"
            )

        has_rain = False

        try:

            for _, row in rain_forecast.iterrows():

                if float(row[rain_col]) > 0:

                    has_rain = True
                    break

        except:
            pass

        if has_rain:

            advice.append(
                "☂ 帶雨傘"
            )

        if not advice:

            advice.append(
                "✅ 天氣正常"
            )

        for item in advice:

            st.write(item)

    except Exception:

        st.error("無法取得天氣資料")

# ==================================
# Footer
# ==================================

st.divider()

st.write(
    hk_now.strftime(
        "%Y-%m-%d %H:%M:%S HKT"
    )
)
