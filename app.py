import streamlit as st
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ==================================
# 自動更新
# ==================================

st_autorefresh(interval=30000, key="refresh")

# ==================================
# 頁面設定
# ==================================

st.set_page_config(
    page_title="Home Dashboard",
    page_icon="🏠",
    layout="wide"
)

# ==================================
# 標題
# ==================================

st.title("🏠 Home Dashboard")

now = datetime.now().astimezone()

# ==================================
# 左右版面
# ==================================

col1, col2 = st.columns(2)

# ==================================
# 巴士區
# ==================================

with col1:

    st.subheader("🚌 Citybus 99")

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

        for i, bus in enumerate(buses, start=1):

            if not bus["eta"]:
                continue

            eta = datetime.fromisoformat(
                bus["eta"]
            )

            mins = int(
                (eta - now).total_seconds()/60
            )

            if mins < 0:
                mins = 0

            st.metric(
                label=f"第{i}班 ➜ {bus['dest_tc']}",
                value=f"{mins} 分鐘"
            )

            st.caption(
                eta.strftime("%H:%M:%S")
            )

    except:

        st.error("無法取得巴士資料")

# ==================================
# 銅鑼灣天氣
# ==================================

with col2:

    st.subheader("📍 銅鑼灣")

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

        temp = weather["temperature"]["data"][1]["value"]

        humidity = weather["humidity"]["data"][0]["value"]

        feels_like = round(
            temp + ((humidity - 40) / 10),
            1
        )

        st.metric(
            "🌡 氣溫",
            f"{temp}°C"
        )

        st.metric(
            "🥵 體感",
            f"{feels_like}°C"
        )

        st.metric(
            "💧 濕度",
            f"{humidity}%"
        )

        # ======================
        # 降雨機率
        # ======================

        if humidity >= 90:
            rain_prob = 80
        elif humidity >= 85:
            rain_prob = 60
        elif humidity >= 75:
            rain_prob = 40
        else:
            rain_prob = 20

        st.metric(
            "☂ 降雨機率",
            f"{rain_prob}%"
        )

        # ======================
        # 天氣警告
        # ======================

        warnings = weather.get(
            "warningMessage",
            []
        )

        warning_list = []

        for w in warnings:

            if "黃色" in w:
                warning_list.append("🟡 黃色暴雨")

            elif "紅色" in w:
                warning_list.append("🔴 紅色暴雨")

            elif "黑色" in w:
                warning_list.append("⚫ 黑色暴雨")

            elif "雷暴" in w:
                warning_list.append("⛈ 雷暴")

            elif "一號" in w:
                warning_list.append("🌀 1號風球")

            elif "三號" in w:
                warning_list.append("🌀 3號風球")

            elif "八號" in w:
                warning_list.append("🌀 8號風球")

        warning_list = list(set(warning_list))

        if warning_list:

            st.markdown("### ⚠ 天氣警告")

            for item in warning_list:
                st.error(item)

        # ======================
        # 出門建議
        # ======================

        advice = []

        if rain_prob >= 50:
            advice.append("☂ 帶雨傘")

        if feels_like >= 33:
            advice.append("🔥 天氣炎熱")

        if humidity >= 85:
            advice.append("💦 悶熱")

        if advice:

            st.markdown("### 🚶 出門建議")

            for item in advice:
                st.write(item)

        else:

            st.markdown("### 🚶 出門建議")
            st.write("✅ 天氣正常")

    except Exception:

        st.error("無法取得天氣資料")

# ==================================
# Footer
# ==================================

st.divider()

st.write(
    f"🕒 {now.strftime('%Y-%m-%d %H:%M:%S')}"
)

st.caption(
    "資料來源：Citybus API、香港天文台"
)
