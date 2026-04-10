import streamlit as st
import pandas as pd

# Sayfa ayarları (Opsiyonel)
st.set_page_config(page_title="Özet Uygulaması", layout="wide")

def main():
    st.title("📊 Veri Özetleme Paneli")
    st.write("Dosyanızı yükleyin ve analiz sonuçlarını görün.")

    # 1. Dosya Yükleme Alanı (Line 45 civarı)
    uploaded_file = st.file_uploader("Bir CSV veya Excel dosyası seçin", type=["csv", "xlsx"])

    if uploaded_file is not None:
        # Dosya tipine göre okuma yapalım
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # 2. Hata Aldığınız Kısım (Line 47 - Kontrol Bloğu)
            if not df.empty:
                st.success("Dosya başarıyla yüklendi!")
                
                # Veri Önizleme
                st.subheader("Veri Önizlemesi")
                st.dataframe(df.head())

                # Özet İstatistikler
                st.subheader("Veri Özeti")
                st.write(df.describe())
                
                # Buraya eklemek istediğiniz diğer analiz kodlarını yazabilirsiniz
            else:
                st.warning("Yüklenen dosya boş görünüyor.")

        except Exception as e:
            st.error(f"Dosya okunurken bir hata oluştu: {e}")
    
    else:
        st.info("Lütfen işlem yapmak için bir dosya yükleyin.")

if __name__ == "__main__":
    main()
