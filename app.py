import streamlit as st
from tefas import Crawler
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Canlı Fon Analiz", layout="wide")

# TEFAS'tan güncel verileri çeken fonksiyon
@st.cache_data(ttl=3600) # Veriyi 1 saat saklar, her saniye interneti yormaz
def canlı_verileri_getir():
    crawler = Crawler()
    # Bugünün ve 1 hafta öncesinin tarihini alalım (Hafta sonuna denk gelirse diye)
    bitis = datetime.now().strftime('%Y-%m-%d')
    baslangic = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    # Verileri çek
    try:
        data = crawler.fetch(start=baslangic, end=bitis, columns=["注文", "Kodu", "Adı", "Fiyat", "Tarih"])
        return data
    except:
        return pd.DataFrame()

st.title("📈 Canlı Fon Portföy Takip")

# Veriyi çekelim
df = canlı_verileri_getir()

if not df.empty:
    hedef_fonlar = ["TLY", "DFİ", "PHE"]
    cols = st.columns(3)
    
    for i, kod in enumerate(hedef_fonlar):
        # Sadece o fonun son iki günkü verisini al
        fon_data = df[df["Kodu"] == kod].sort_values("Tarih", ascending=False)
        
        if len(fon_data) >= 2:
            guncel_fiyat = fon_data.iloc[0]["Fiyat"]
            eski_fiyat = fon_data.iloc[1]["Fiyat"]
            # Getiri hesapla
            yuzde_degisim = ((guncel_fiyat - eski_fiyat) / eski_fiyat) * 100
            
            with cols[i]:
                st.metric(label=f"{kod} Getiri", 
                          value=f"{guncel_fiyat:.4f} TL", 
                          delta=f"%{yuzde_degisim:.2f}")
                st.caption(fon_data.iloc[0]["Adı"])
        else:
            cols[i].error(f"{kod} verisi yüklenemedi.")
else:
    st.warning("TEFAS'tan veri şu an çekilemiyor. Lütfen biraz sonra tekrar deneyin.")

st.info("Not: Fon fiyatları her iş günü sabah 10:00 civarı TEFAS tarafından güncellenir.")
