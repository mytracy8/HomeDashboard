import streamlit as st
import requests
from datetime import datetime

st.set_page_config(
    page_title="99號巴士",
    page_icon="🚌",
    layout="centered"
)

st.title("🚌 Citybus 99")
st.subheader("📍 漁安苑（利東邨道）")

url = "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/002212/99"

data = requests.get(url).json()

now = datetime.now().astimezone()

for i, bus in enumerate(data["data"][:3], start=1):

    if bus["eta"]:

        eta = datetime.fromisoformat(bus["eta"])

        mins = int((eta - now).total_seconds() / 60)

        destination = bus["dest_tc"]

        st.metric(
            label=f"第{i}班 → {destination}",
            value=f"{mins} 分鐘"
        )

        st.caption(
            f"到站時間：{eta.strftime('%H:%M:%S')}"
        )

st.divider()

st.write(
    f"最後更新：{now.strftime('%Y-%m-%d %H:%M:%S')}"
)