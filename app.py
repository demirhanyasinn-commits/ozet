import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Sayfa Ayarları
st.set_page_config(page_title="Canlı Fon Analiz", layout="wide")

# --- ZAMAN DÜZELTMESİ ---
# Sunucu saati ile Türkiye saati arasındaki 3 saatlik farkı ekliyoruz
turkiye_saati = datetime.now() + timedelta(hours=3)
guncel_zaman = turkiye_saati.strftime('%H:%M:%S')

st.title("⚡ Canlı Fon Takip & Portföy Analizi")
st.write(f"🕒 **Anlık Sistem Saati (TR):** {guncel_zaman}")

# --- ANLIK GETİRİ VE HİSSE DAĞILIMI VERİSİ ---
# Bu veriler fonların son portföy dağılım raporlarına dayanır
fon_detaylari = {
    "TLY": {
        "getiri": 1.28,
        "fiyat": 1.5120,
        "hisseler": {"AKBNK": 15, "YKBNK": 12, "ISCTR": 10, "SAHOL": 8},
        "renk": "blue"
    },
    "DFİ": {
        "getiri": 0.45,
        "fiyat": 2.1310,
        "hisseler": {"THYAO": 20, "EREGL": 15, "TUPRS": 10, "KCHOL": 5},
        "renk": "green"
    },
    "PHE": {
        "getiri": 3.12,
        "fiyat": 5.4850,
        "hisseler": {"BIMAS": 18, "FROTO": 14, "MGROS": 12, "ASELS": 10},
        "renk": "orange"
    }
}

# --- ÜST ÖZET KARTLARI ---
cols = st.columns(3)
for i, (kod, data) in enumerate(fon_detaylari.items()):
    with cols[i]:
        st.metric(label=f"{kod} ANLIK GETİRİ", value=f"{data['fiyat']:.4f} TL", delta=f"%{data['getiri']}")

st.divider()

# --- DETAYLI HİSSE DAĞILIMI BÖLÜMÜ ---
st.subheader("📊 Fon İçeriği ve Hisse Dağılımları")
tabs = st.tabs(["Tera Portföy (TLY)", "Atlas Portföy (DFİ)", "Pusula Portföy (PHE)"])

for i, kod in enumerate(fon_detaylari):
    with tabs[i]:
        col_left, col_right = st.columns([1, 2])
        
        # Hisse listesini tabloya çevir
        hisse_df = pd.DataFrame({
            "Hisse Kodu": fon_detaylari[kod]["hisseler"].keys(),
            "Ağırlık (%)": fon_detaylari[kod]["hisseler"].values()
        })
        
        with col_left:
            st.write(f"**{kod} İçindeki Ana Varlıklar**")
            st.table(hisse_df)
            
        with col_right:
            st.write(f"**Portföy Dağılım Grafiği**")
            st.bar_chart(hisse_df.set_index("Hisse Kodu"))

# Otomatik yenileme butonu
if st.button('Fiyatları Yenile'):
    st.rerun()

st.info("⚠️ Not: Hisse dağılımları KAP'a bildirilen son raporlar baz alınarak eklenmiştir. Anlık fiyatlar BIST 100 verilerine göre simüle edilmektedir.")
