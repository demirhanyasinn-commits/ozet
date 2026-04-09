import streamlit as st
import pandas as pd
from tefas import Crawler
from datetime import datetime, timedelta

st.set_page_config(page_title="Canlı Fon Takip", layout="wide")

def verileri_cek():
    crawler = Crawler()
    # Son 10 günü tarayalım ki araya hafta sonu/tatil girse bile veri bulalım
    bitis = datetime.now()
    baslangic = bitis - timedelta(days=10)
    
    try:
        # Veriyi çekmeye çalış
        data = crawler.fetch(
            start=baslangic.strftime('%Y-%m-%d'),
            end=bitis.strftime('%Y-%m-%d')
        )
        return data
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        return pd.DataFrame()

st.title("📈 Canlı Fon Portföy Takip")

with st.spinner('TEFAS verileri güncelleniyor...'):
    df = verileri_cek()

if not df.empty:
    # İlgilendiğimiz fonlar
    kodlar = ["TLY", "DFİ", "PHE"]
    cols = st.columns(3)
    
    for i, kod in enumerate(kodlar):
        # Fonun verilerini filtrele ve en yeni tarihe göre sırala
        fon_df = df[df['Kodu'] == kod].sort_values('Tarih', ascending=False)
        
        if not fon_df.empty and len(fon_df) >= 2:
            guncel_fiyat = fon_df.iloc[0]['Fiyat']
            onceki_fiyat = fon_df.iloc[1]['Fiyat']
            degisim = ((guncel_fiyat - onceki_fiyat) / onceki_fiyat) * 100
            
            with cols[i]:
                st.metric(
                    label=f"{kod} Portföy",
                    value=f"{guncel_fiyat:.4f} TL",
                    delta=f"%{degisim:.2f}"
                )
                st.caption(fon_df.iloc[0]['Adı'])
        elif not fon_df.empty:
            # Sadece tek günlük veri varsa
            with cols[i]:
                st.metric(label=f"{kod} Portföy", value=f"{fon_df.iloc[0]['Fiyat']:.4f} TL")
                st.write("Değişim verisi bekleniyor...")
        else:
            cols[i].warning(f"{kod} kodu bulunamadı.")
else:
    st.warning("Veri çekilemedi. TEFAS sunucusu yanıt vermiyor olabilir veya kütüphane kurulumu tamamlanmadı.")

st.divider()
st.caption("Veriler TEFAS üzerinden otomatik çekilmektedir. Her iş günü 10:00'dan sonra güncellenir.")
