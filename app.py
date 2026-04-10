import streamlit as st
import pandas as pd
import time

# Sayfa Genişliği ve Başlık
st.set_page_config(page_title="Fon Takip Paneli", layout="wide")

# 1. VERİ KAYNAĞI (Burayı veri değiştikçe güncelleyebilirsiniz veya bir API'ye bağlayabilirsiniz)
def get_data():
    # Bu kısım normalde bir veritabanından veya canlı bir API'den gelebilir.
    # Örnek sabit veri yapısı:
    data = {
        "Fon Kodu": ["TLY", "DFI", "PHE"],
        "Fon Adı": ["TLY Fonu", "DFI Fonu", "PHE Fonu"],
        "Güncel Getiri (%)": [1.25, -0.45, 2.10], # Örnek veriler
        "Son Güncelleme": [time.strftime("%H:%M:%S")] * 3
    }
    return pd.DataFrame(data)

def main():
    st.title("📈 Canlı Fon Takip Ekranı")
    st.write(f"Son Güncelleme: **{time.strftime('%d.%m.%Y %H:%M:%S')}**")
    
    # Veriyi çek
    df = get_data()

    # 2. ÜST ÖZET KUTUCUKLARI (Metric)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="TLY", value=f"%{df.iloc[0]['Güncel Getiri (%)']}", delta="0.05%")
    
    with col2:
        st.metric(label="DFI", value=f"%{df.iloc[1]['Güncel Getiri (%)']}", delta="-0.02%", delta_color="normal")
        
    with col3:
        st.metric(label="PHE", value=f"%{df.iloc[2]['Güncel Getiri (%)']}", delta="0.12%")

    st.markdown("---")

    # 3. VERİ TABLOSU
    st.subheader("Güncel Fon Detayları")
    st.dataframe(df, use_container_width=True)

    # 4. OTOMATİK YENİLEME BUTONU (Opsiyonel)
    if st.button('Verileri Şimdi Güncelle'):
        st.rerun()

if __name__ == "__main__":
    main()
