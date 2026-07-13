import streamlit as st
import requests

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
# HK Time
# ==================================

hk_now = datetime.now(
    ZoneInfo("Asia/Hong_Kong")
)

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

        BUS_URL = (
            "https://rt.data.gov.hk/v2/transport/"
            "citybus/eta/CTB/002212/99"
        )

        bus_data = requests.get(
            BUS_URL,
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
                f"🚌 {mins} 分鐘 ({eta.strftime('%H:%M')})"
            )

    except Exception as e:

        st.error(
            f"巴士資料錯誤: {e}"
        )

# ==================================
# WEATHER
# ==================================

with col2:

    st.header("📍 銅鑼灣")

    try:

        WEATHER_URL = (
            "https://data.weather.gov.hk/"
            "weatherAPI/opendata/weather.php"
            "?dataType=rhrread&lang=tc"
        )

        weather = requests.get(
            WEATHER_URL,
            timeout=10
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

        # ==================================
        # Rain Forecast
        # ==================================

        st.subheader("☂ 未來兩小時")

        st.write("請先修復 Rainfall Nowcast")

        # ==================================
        # Warnings
        # ==================================

        WARN_URL = (
            "https://data.weather.gov.hk/"
            "weatherAPI/opendata/weather.php"
            "?dataType=warnsum&lang=tc"
        )

        warn_data = requests.get(
            WARN_URL,
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

        warnings = []

        for code in warn_data.keys():

            if code in code_map:

                warnings.append(
                    code_map[code]
                )

        if warnings:

            st.subheader("⚠ 天氣警告")

            for w in warnings:

                st.write(w)

        # ==================================
        # Advice
        # ==================================

        st.subheader("🚶 出門建議")

        advice = []

        if feels_like >= 33:

            advice.append(
                "🔥 天氣炎熱"
            )

        if "WRAINY" in warn_data \
           or "WRAINR" in warn_data \
           or "WRAINB" in warn_data:

            advice.append(
                "☂ 帶雨傘"
            )

        if not advice:

            advice.append(
                "✅ 天氣正常"
            )

        for item in advice:

            st.write(item)

    except Exception as e:

        st.error(
            f"天氣資料錯誤: {e}"
        )

# ==================================
# Footer
# ==================================

st.divider()

st.write(
    hk_now.strftime(
        "%Y-%m-%d %H:%M:%S HKT"
    )
)
