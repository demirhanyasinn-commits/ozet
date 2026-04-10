import streamlit as st
import pandas as pd
from tefas import Crawler
from datetime import datetime, timedelta
import pytz

# 1. Ayarlar ve Sayfa Yapısı
st.set_page_config(page_title="TEFAS Canlı Fon Takip", layout="wide")

# İstanbul saat dilimi ayarı
def get_istanbul_now():
    return datetime.now(pytz.timezone('Europe/Istanbul'))

# 2. TEFAS'tan Veri Çekme Fonksiyonu
@st.cache_data(ttl=3600) # Veriyi 1 saat önbelleğe alır, performansı artırır
def fetch_tefas_data(font_list):
    crawler = Crawler()
    # TEFAS verileri genellikle bir gün geriden gelir veya akşam güncellenir
    # En güncel veriyi almak için dünün tarihini baz alıyoruz
    end_date = get_istanbul_now().strftime("%Y-%m-%d")
    start_date = (get_istanbul_now() - timedelta(days=5)).strftime("%Y-%m-%d")
    
    try:
        data = crawler.fetch(start_date, end_date)
        # Sadece bizim istediğimiz fonları filtrele
        filtered_df = data[data['code'].isin(font_list)]
        # En son güne ait verileri al
        latest_data = filtered_df.sort_values('date', ascending=False).drop_duplicates('code')
        return latest_data
    except Exception as e:
        st.error(f"TEFAS verisi çekilirken hata oluştu: {e}")
        return pd.DataFrame()

def main():
    st.title("📊 TEFAS Anlık Fon Analiz Paneli")
    st.write(f"Son Güncelleme (İstanbul): **{get_istanbul_now().strftime('%d.%m.%Y %H:%M:%S')}**")
    
    # Takip edilecek fonlar
    my_funds = ["TLY", "DFI", "PHE"]
    
    with st.spinner('TEFAS verileri güncelleniyor...'):
        df = fetch_tefas_data(my_funds)

    if not df.empty:
        # 3. Üst Metrik Kartları
        cols = st.columns(len(my_funds))
        
        for i, fund_code in enumerate(my_funds):
            fund_row = df[df['code'] == fund_code]
            if not fund_row.empty:
                price = fund_row.iloc[0]['price']
                daily_return = fund_row.iloc[0]['daily_return']
                
                cols[i].metric(
                    label=f"Fiyat: {fund_code}",
                    value=f"{price:.4f} TL",
                    delta=f"%{daily_return:.2f} (Günlük)"
                )
        
        st.divider()

        # 4. Detaylı Tablo
        st.subheader("Fon Detayları")
        display_df = df[['code', 'title', 'price', 'daily_return', 'date']].copy()
        display_df.columns = ['Fon Kodu', 'Fon Adı', 'Birim Fiyat', 'Günlük Getiri (%)', 'Veri Tarihi']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
    else:
        st.error("Veriler şu anda TEFAS'tan çekilemiyor. Lütfen daha sonra tekrar deneyin.")

    # Yenileme butonu
    if st.button("Verileri Zorla Güncelle"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()
