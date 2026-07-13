import streamlit as st
import requests
import pandas as pd
import io

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

        weather_url = (
