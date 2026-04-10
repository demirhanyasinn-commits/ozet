import streamlit as st
import pandas as pd
from tefas import Crawler
from datetime import datetime, timedelta
import pytz

# Sayfa Ayarları
st.set_page_config(page_title="TEFAS Canlı Fon Takip", layout="wide")

def get_istanbul_now():
    return datetime.now(pytz.timezone('Europe/Istanbul'))

# Veri çekme işlemini optimize ettik
@st.cache_data(ttl=600) # 10 dakikada bir yenilenir
def fetch_tefas_data(font_list):
    try:
        crawler = Crawler()
        # Sadece son 3 günü sorgulayarak işlemi hızlandırıyoruz
        end_date = get_istanbul_now().strftime("%Y-%m-%d")
        start_date = (get_istanbul_now() - timedelta(days=3)).strftime("%Y-%m-%d")
        
        data = crawler.fetch(start_date, end_date)
        
        if data is not None and not data.empty:
            filtered_df = data[data['code'].isin(font_list)]
            if not filtered_df.empty:
                # En güncel tarihi al
                latest_date = filtered_df['date'].max()
                return filtered_df[filtered_df['date'] == latest_date]
        return None
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        return None

def main():
    st.title("📈 TEFAS Canlı Fon Takip")
    
    su_an = get_istanbul_now().strftime('%d.%m.%Y %H:%M:%S')
    st.write(f"🕒 Son Güncelleme: **{su_an}**")

    my_funds = ["TLY", "DFI", "PHE"]
    
    # Veri yüklenirken dönen halka
    with st.spinner('Piyasadan veriler alınıyor, lütfen bekleyin...'):
        df = fetch_tefas_data(my_funds)

    if df is not None and not df.empty:
        # Metrik Kartları
        cols = st.columns(len(my_funds))
        for i, fund_code in enumerate(my_funds):
            fund_row = df[df['code'] == fund_code]
            if not fund_row.empty:
                row = fund_row.iloc[0]
                cols[i].metric(
                    label=f"Fon: {fund_code}", 
                    value=f"{row['price']:.4f} TL", 
                    delta=f"%{row['daily_return']:.2f}"
                )
        
        st.divider()
        st.subheader("📋 Detaylı Liste")
        st.dataframe(df[['code', 'title', 'price', 'daily_return', 'date']], use_container_width=True, hide_index=True)
    else:
        # Veri gelmezse kullanıcıyı bilgilendir
        st.warning("Şu an TEFAS'tan veri alınamıyor. Piyasalar kapalı olabilir veya bağlantı yavaştır. Lütfen 'Yenile' butonuna basınız.")

    if st.button("🔄 Verileri Şimdi Yenile"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()
