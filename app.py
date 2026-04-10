import streamlit as st
import pandas as pd
from tefas import Crawler
from datetime import datetime, timedelta
import pytz

# Sayfa Ayarları
st.set_page_config(page_title="TEFAS Canlı Fon Takip", layout="wide")

def get_istanbul_now():
    return datetime.now(pytz.timezone('Europe/Istanbul'))

@st.cache_data(ttl=3600)
def fetch_tefas_data(font_list):
    try:
        crawler = Crawler()
        # TEFAS verileri genellikle 1 gün geriden gelir
        # Son 7 günlük veriyi çekip en günceli filtreliyoruz
        end_date = get_istanbul_now().strftime("%Y-%m-%d")
        start_date = (get_istanbul_now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        data = crawler.fetch(start_date, end_date)
        
        if data is not None and not data.empty:
            # Sadece listedeki fonları al
            filtered_df = data[data['code'].isin(font_list)]
            # En güncel tarihi bul ve o tarihteki verileri getir
            latest_date = filtered_df['date'].max()
            final_df = filtered_df[filtered_df['date'] == latest_date]
            return final_df
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def main():
    st.title("📈 TEFAS Canlı Fon Takip")
    
    su_an = get_istanbul_now().strftime('%d.%m.%Y %H:%M:%S')
    st.info(f"Son Güncelleme (İstanbul): **{su_an}**")

    my_funds = ["TLY", "DFI", "PHE"]
    
    df = fetch_tefas_data(my_funds)

    if not df.empty:
        # Metrik Kartları
        cols = st.columns(len(my_funds))
        for i, fund_code in enumerate(my_funds):
            fund_row = df[df['code'] == fund_code]
            if not fund_row.empty:
                price = fund_row.iloc[0]['price']
                # Günlük getiriyi yüzdeye çevirerek göster
                ret = fund_row.iloc[0]['daily_return']
                cols[i].metric(label=fund_code, value=f"{price:.4f} TL", delta=f"%{ret:.2f}")

        st.divider()
        st.subheader("Detaylı Fon Tablosu")
        # Tabloyu daha şık gösterelim
        st.dataframe(
            df[['code', 'title', 'price', 'daily_return', 'date']], 
            column_config={
                "code": "Fon Kodu",
                "title": "Fon Adı",
                "price": "Birim Fiyat",
                "daily_return": "Günlük Getiri (%)",
                "date": "Veri Tarihi"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.error("Veriler şu an çekilemiyor. Lütfen requirements.txt dosyasını kontrol edip uygulamayı yeniden başlatın.")

    if st.button("Verileri Yenile"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()
