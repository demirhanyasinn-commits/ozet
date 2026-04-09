import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fon Analiz Terminali", layout="wide")

# Sol menüden fon seçimi
secilen_fon = st.sidebar.selectbox("Detaylı İncelemek İstediğiniz Fonu Seçin", ["Genel Bakış", "TLY", "DFİ", "PHE"])

if secilen_fon == "Genel Bakış":
    st.title("📈 Fon Portföy Takip")
    # Ana kartları buraya koyuyoruz
    col1, col2, col3 = st.columns(3)
    col1.metric("TLY Getiri", "1.458 TL", "%1.08")
    col2.metric("DFİ Getiri", "2.102 TL", "-%0.42")
    col3.metric("PHE Getiri", "5.341 TL", "%2.18")

elif secilen_fon == "TLY":
    st.title("🔵 TLY - Tera Portföy Birinci Serbest Fon")
    
    # Üst Bilgi Kartları
    c1, c2 = st.columns(2)
    c1.info("**Toplam Portföy Değeri:** ₺75.398.509.680")
    c2.success("**Günlük Getiri:** +%1,08")

    # Detaylı Tablo (Görüntündeki "En Çok Kazandıranlar" kısmı gibi)
    st.subheader("📊 En Çok Kazandıran Hisseler (TL)")
    hisse_data = {
        "Hisse": ["TERA", "TRHOL", "PEKGY", "HMV", "SVGYO"],
        "Fark %": ["+%5,37", "+%8,74", "+%1,89", "+%2,24", "+%2,99"],
        "Etki %": ["%1,22", "%0,49", "%0,12", "%0,03", "%0,01"]
    }
    st.table(pd.DataFrame(hisse_data))

    # Portföy Dağılım Grafiği (Basit bir pasta grafik ekleyebiliriz)
    st.write("### Portföy Dağılımı")
    st.bar_chart({"Hisse": 85, "VİOP": 10, "Nakit": 5})
