import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# Sayfa Ayarları
st.set_page_config(page_title="Fon Takip Sistemi", layout="wide")

# 1. SAAT FONKSİYONU (İstanbul saatine göre)
def get_istanbul_time():
    istanbul_tz = pytz.timezone('Europe/Istanbul')
    return datetime.now(istanbul_tz).strftime('%d.%m.%Y %H:%M:%S')

# 2. VERİ KAYNAĞI (TLY, DFI, PHE)
def get_fon_verileri():
    # Buradaki rakamları güncel verilerinizle değiştirebilirsiniz
    ist_saati = get_istanbul_time()
    data = {
        "Fon Kodu": ["TLY", "DFI", "PHE"],
        "Birim Fiyat": [150.45, 230.12, 110.75],  # Örnek fiyatlar
        "Günlük Getiri (%)": [1.2, -0.5, 2.8],    # Örnek yüzdeler
        "Son Güncelleme": [ist_saati] * 3
    }
    return pd.DataFrame(data)

def main():
    # Başlık ve İstanbul Saati
    st.title("📈 Canlı Fon Takip Paneli")
    
    # Üst Bilgi Çubuğu
    su_an = get_istanbul_time()
    st.info(f"Sistem Saati (İstanbul): **{su_an}**")

    # Verileri Çek
    df = get_fon_verileri()

    # 3. METRİK GÖRÜNÜMÜ (TLY - DFI - PHE)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="TLY Getiri", value=f"%{df.iloc[0]['Günlük Getiri (%)']}", delta="Pozitif")
        
    with col2:
        st.metric(label="DFI Getiri", value=f"%{df.iloc[1]['Günlük Getiri (%)']}", delta="-Negatif", delta_color="normal")
        
    with col3:
        st.metric(label="PHE Getiri", value=f"%{df.iloc[2]['Günlük Getiri (%)']}", delta="Pozitif")

    st.divider()

    # 4. TABLO GÖRÜNÜMÜ
    st.subheader("Güncel Fon Listesi")
    st.table(df) # Veya st.dataframe(df, use_container_width=True)

    # Otomatik Güncelleme simülasyonu için buton
    if st.button("Verileri Yenile"):
        st.rerun()

if __name__ == "__main__":
    main()
