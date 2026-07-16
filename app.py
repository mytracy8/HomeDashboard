import streamlit as st
import requests
import pandas as pd
import zipfile
import io

from datetime import datetime
from zoneinfo import ZoneInfo

# ==================================
# Page Config
# ==================================

st.set_page_config(
    page_title="Today",
    page_icon="☀",
    layout="wide"
)

# ==================================
# CSS
# ==================================

st.markdown("""
<style>

.main-title {
    font-size:48px;
    font-weight:700;
    margin-bottom:20px;
}

.bus-text {
    font-size:28px;
    font-weight:600;
    line-height:1.3;
}

.weather-text {
    font-size:24px;
    line-height:1.4;
}

.rain-text {
    font-size:22px;
    line-height:1.6;
}

.footer-text {
    color:gray;
    font-size:14px;
}

</style>
""", unsafe_allow_html=True)

# ==================================
# Time
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

st.markdown(
    '<div class="main-title">☀ Today</div>',
    unsafe_allow_html=True
)

# ==================================
# Layout
# ==================================

col1, col2 = st.columns(2)

# ==================================
# Bus
# ==================================

with col1:

    st.markdown("## 🚌 Citybus 99")

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

            st.markdown(
                f"""
                <div class="bus-text">
                {mins}分鐘 ({eta.strftime('%H:%M')})
                </div>
                """,
                unsafe_allow_html=True
            )

    except Exception as e:

        st.error(
            f"巴士資料錯誤: {e}"
        )

# ==================================
# Weather
# ==================================

with col2:

    st.markdown("## 📍 銅鑼灣天氣")

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

        st.markdown(
            f"""
            <div class="weather-text">
            🌡 {temp}°C<br>
            🥵 體感 {feels_like}°C<br>
            💧 {humidity}%
            </div>
            """,
            unsafe_allow_html=True
        )

# ==================================
# Rainfall
# ==================================

st.markdown("## ☂ 銅鑼灣降雨")

try:

    zip_url = (
        "https://data.weather.gov.hk/"
        "weatherAPI/hko_data/csdi/dataset/"
        "gridded_rainfall_nowcast.zip"
    )

    response = requests.get(
        zip_url,
        timeout=30
    )

    response.raise_for_status()

    z = zipfile.ZipFile(
        io.BytesIO(response.content)
    )

    csv_name = z.namelist()[0]

    with z.open(csv_name) as csv_file:

        df = pd.read_csv(csv_file)

    # 正確欄位
    rain_col = df.columns[7]
    lat_col = df.columns[8]
    lon_col = df.columns[9]

    end_hour_col = df.columns[3]
    end_min_col = df.columns[4]

    causeway_bay_lat = 22.2803
    causeway_bay_lon = 114.1849

    df["distance"] = (
        (df[lat_col] - causeway_bay_lat) ** 2 +
        (df[lon_col] - causeway_bay_lon) ** 2
    )

    # 取最近格點
    nearest_row = df.loc[
        df["distance"].idxmin()
    ]

    target_lat = nearest_row[lat_col]
    target_lon = nearest_row[lon_col]

    forecast = df[
        (df[lat_col] == target_lat)
        &
        (df[lon_col] == target_lon)
    ].copy()

    forecast["forecast_time"] = (
        forecast[end_hour_col]
        .astype(int)
        .astype(str)
        .str.zfill(2)
        + ":"
        +
        forecast[end_min_col]
        .astype(int)
        .astype(str)
        .str.zfill(2)
    )

    forecast = forecast.sort_values(
        by=[end_hour_col, end_min_col]
    )

    forecast = forecast.drop_duplicates(
        subset=["forecast_time"]
    )

    forecast = forecast.head(4)

    if len(forecast) == 0:

        st.write("無降雨預報資料")

    else:

        for _, row in forecast.iterrows():

            forecast_time = row["forecast_time"]

            rain_mm = float(
                row[rain_col]
            )

            st.markdown(
                f"""
                <div class="rain-text">
                {forecast_time} {rain_text(rain_mm)}
                </div>
                """,
                unsafe_allow_html=True
            )

except Exception as e:

    st.error(
        f"Rainfall Error: {e}"
    )

        # ==================================
        # Warning
        # ==================================

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

        warnings = []

        for code in warn_data.keys():

            if code in code_map:

                warnings.append(
                    code_map[code]
                )

        if warnings:

            st.markdown("## ⚠ 天氣警告")

            for w in warnings:

                st.write(w)

    except Exception as e:

        st.error(
            f"天氣資料錯誤: {e}"
        )

# ==================================
# Footer
# ==================================

st.divider()

st.markdown(
    f"""
    <div class="footer-text">
    {hk_now.strftime('%H:%M HKT')}
    </div>
    """,
    unsafe_allow_html=True
)
