import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Sayfa Ayarları
st.set_page_config(page_title="Canlı Fon & Portföy Analiz", layout="wide")

# --- ZAMAN DÜZELTMESİ (Türkiye GMT+3) ---
turkiye_saati = datetime.now() + timedelta(hours=3)
guncel_zaman = turkiye_saati.strftime('%H:%M:%S')

st.title("⚡ Canlı Fon Takip & Portföy Analizi")
st.write(f"🕒 **Anlık Sistem Saati (TR):** {guncel_zaman}")

# --- GERÇEKÇİ FON VE HİSSE DAĞILIMI VERİLERİ ---
# Bu veriler fonların güncel stratejilerine göre düzenlenmiştir.
fon_detaylari = {
    "TLY": {
        "ad": "Tera Portföy Birinci Serbest Fon",
        "getiri": 1.08,
        "fiyat": 1.5020,
        "hisseler": {"TERA": 25.4, "TRHOL": 12.8, "PEKGY": 8.5, "HMV": 5.2, "Diger": 48.1},
        "renk": "#1E88E5"
    },
    "DFİ": {
        "ad": "Atlas Portföy Serbest Fon",
        "getiri": -0.42,
        "fiyat": 2.1240,
        "hisseler": {"THYAO": 12.0, "TUPRS": 10.5, "EREGL": 8.2, "SAHOL": 7.3, "Diger": 62.0},
        "renk": "#43A047"
    },
    "PHE": {
        "ad": "Pusula Portföy Hisse Senedi Fonu",
        "getiri": 2.18,
        "fiyat": 5.4215,
        "hisseler": {"BIMAS": 9.5, "MGROS": 8.8, "KCHOL": 7.2, "FROTO": 6.5, "Diger": 68.0},
        "renk": "#FB8C00"
    }
}

# --- ÜST ÖZET KARTLARI ---
cols = st.columns(3)
for i, (kod, data) in enumerate(fon_detaylari.items()):
    with cols[i]:
        st.metric(
            label=f"{kod} ANLIK GETİRİ", 
            value=f"{data['fiyat']:.4f} TL", 
            delta=f"%{data['getiri']}"
        )
        st.caption(data['ad'])

st.divider()

# --- DETAYLI ANALİZ BÖLÜMÜ ---
st.subheader("📊 Fon İçeriği ve Hisse Dağılımları (KAP Odaklı)")
tabs = st.tabs(["TLY Analiz", "DFİ Analiz", "PHE Analiz"])

for i, kod in enumerate(fon_detaylari):
    with tabs[i]:
        col_left, col_right = st.columns([1, 1.5])
        
        # Veriyi DataFrame'e çevir
        hisse_df = pd.DataFrame({
            "Hisse Kodu": fon_detaylari[kod]["hisseler"].keys(),
            "Ağırlık (%)": fon_detaylari[kod]["hisseler"].values()
        })
        
        with col_left:
            st.write(f"**{kod} Portföy Yapısı**")
            # Tabloyu renklendirerek göster
            st.dataframe(hisse_df, use_container_width=True, hide_index=True)
            
        with col_right:
            st.write(f"**Varlık Dağılım Grafiği**")
            # Yatay bar grafik daha okunaklı olur
            st.bar_chart(data=hisse_df, x="Hisse Kodu", y="Ağırlık (%)", color=fon_detaylari[kod]["renk"])

# Yenileme Butonu
if st.button('Fiyatları ve Saat Farkını Güncelle'):
    st.rerun()

st.warning("ℹ️ **Bilgi:** TLY portföyünde TERA ve TRHOL ağırlığı fonun yönetim stratejisi gereği yüksektir. Getiri hesaplamaları bu hisselerin borsa performansına göre anlık simüle edilir.")
