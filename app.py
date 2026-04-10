import streamlit as st
import pandas as pd
import random
import time
import plotly.express as px

st.set_page_config(page_title="Fon Takip", layout="wide")

st.title("📊 Profesyonel Fon Takip Terminali")

# 🔄 Auto refresh
count = st.experimental_rerun if False else None

# Fake veri (şimdilik)
def get_data():
    return {
        "TLY": {
            "price": round(random.uniform(1.4, 1.6), 4),
            "history": {
                "d1": 1.45,
                "w1": 1.40,
                "m1": 1.30
            },
            "distribution": {
                "Nakit": 50,
                "Hisse": 20,
                "Tahvil": 15,
                "Diğer": 15
            }
        },
        "PHE": {
            "price": round(random.uniform(5.0, 5.6), 4),
            "history": {
                "d1": 5.2,
                "w1": 5.0,
                "m1": 4.5
            },
            "distribution": {
                "Hisse": 60,
                "Nakit": 10,
                "Tahvil": 20,
                "Diğer": 10
            }
        }
    }

def calc_change(current, past):
    return ((current - past) / past) * 100

data = get_data()

# 📦 Fon Kartları
cols = st.columns(len(data))

for i, (fon, val) in enumerate(data.items()):
    with cols[i]:
        change = calc_change(val["price"], val["history"]["d1"])

        color = "green" if change > 0 else "red"

        st.markdown(f"### {fon}")
        st.markdown(f"<h1 style='color:{color}'>{change:.2f}%</h1>", unsafe_allow_html=True)
        st.markdown(f"<p>{val['price']} TL</p>", unsafe_allow_html=True)

        # 👇 DETAY
        with st.expander("Detayları Gör"):
            d1 = calc_change(val["price"], val["history"]["d1"])
            w1 = calc_change(val["price"], val["history"]["w1"])
            m1 = calc_change(val["price"], val["history"]["m1"])

            st.write(f"📅 1 Gün: %{d1:.2f}")
            st.write(f"📅 1 Hafta: %{w1:.2f}")
            st.write(f"📅 1 Ay: %{m1:.2f}")

            # 📊 Grafik
            df = pd.DataFrame({
                "Kategori": list(val["distribution"].keys()),
                "Oran": list(val["distribution"].values())
            })

            fig = px.pie(df, names="Kategori", values="Oran", title="Varlık Dağılımı")
            st.plotly_chart(fig, use_container_width=True)

# 🔄 Auto refresh
time.sleep(10)
st.rerun()
