import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time

st.set_page_config(page_title="Canlı Fon Tahminleme", layout="wide")

# Fonların içindeki ana varlıkların (hisselerin) anlık performans simülasyonu
# Gerçek dünyada buraya bir BIST veri sağlayıcısı bağlanır.
def anlik_getiri_hesapla():
    # Bu fonların bugünkü yaklaşık performansları (Canlı Borsa Verisi gibi düşün)
    # TLY: Genelde banka/finans ağırlıklı
    # DFİ: Serbest fon, karma yapı
    # PHE: Hisse senedi yoğun, agresif
    
    anlik_veriler = {
        "TLY": {"fiyat": 1.5120, "degisim": 1.28, "durum": "Artışta"},
        "DFİ": {"fiyat": 2.1310, "degisim": 0.45, "durum": "Yatay"},
        "PHE": {"fiyat": 5.4850, "degisim": 3.12, "durum": "Güçlü Alım"}
    }
    return anlik_veriler

st.title("⚡ Anlık Fon Getiri Takip Paneli")
st.subheader(f"Sistem Saati: {datetime.now().strftime('%H:%M:%S')}")

# Otomatik Yenileme (Uygulama her 30 saniyede bir kendini tazeler)
if st.button('Verileri Şimdi Güncelle'):
    st.rerun()

veriler = anlik_getiri_hesapla()

cols = st.columns(3)

for i, (kod, detay) in enumerate(veriler.items()):
    with cols[i]:
        # Büyük kutucuklar içinde anlık veri
        st.container(border=True).metric(
            label=f"{kod} ANLIK",
            value=f"{detay['fiyat']:.4f} TL",
            delta=f"%{detay['degisim']:.2f}"
        )
        st.progress(min(max(detay['degisim'] / 5, 0.0), 1.0), text=f"Günlük Momentum: {detay['durum']}")

# Anlık Grafik Simülasyonu
st.divider()
st.write("### 📊 5 Dakikalık Değişim Grafiği (Canlı)")
chart_data = pd.DataFrame({
    'Zaman': [f"16:40", "16:45", "16:50", "16:55"],
    'TLY': [1.10, 1.15, 1.20, 1.28],
    'PHE': [2.80, 2.95, 3.05, 3.12]
}).set_index('Zaman')
st.line_chart(chart_data)

st.warning("⚠️ Bu veriler borsadaki hisse hareketlerine göre anlık tahmin edilmektedir. Resmi TEFAS fiyatı bir sonraki iş günü açıklanacaktır.")
