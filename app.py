import streamlit as st
import pandas as pd

# Sayfa Konfigürasyonu
st.set_page_config(page_title="Fon Takip Portalı", layout="wide")

st.markdown("## 📈 Borsa İstanbul Fon Takip Sistemi")
st.write("Seçili fonların günlük performans verileri aşağıdadır.")

# Temsili Veri Seti (Gerçek uygulamada API'den gelir)
fon_verileri = {
    "TLY": {"ad": "Tera Portföy Birinci Serbest", "getiri": 1.25, "fiyat": 1.458},
    "DFİ": {"ad": "Atlas Portföy Serbest", "getiri": -0.42, "fiyat": 2.102},
    "PHE": {"ad": "Pusula Portföy Hisse Senedi", "getiri": 2.18, "fiyat": 5.341}
}

# Yan yana 3 kolon oluşturma
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("TLY Getiri", f"{fon_verileri['TLY']['fiyat']}", f"{fon_verileri['TLY']['getiri']}%")
    st.caption(fon_verileri['TLY']['ad'])

with col2:
    st.metric("DFİ Getiri", f"{fon_verileri['DFİ']['fiyat']}", f"{fon_verileri['DFİ']['getiri']}%", delta_color="normal")
    st.caption(fon_verileri['DFİ']['ad'])

with col3:
    st.metric("PHE Getiri", f"{fon_verileri['PHE']['fiyat']}", f"{fon_verileri['PHE']['getiri']}%")
    st.caption(fon_verileri['PHE']['ad'])

st.divider()
st.info("Not: Veriler TEFAS üzerinden günlük olarak güncellenmektedir.")
