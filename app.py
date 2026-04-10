import streamlit as st
import pandas as pd
from tefas import Crawler
from datetime import datetime, timedelta
import pytz

# Sayfa Ayarları
st.set_page_config(page_title="Fon Takip Paneli", layout="wide")

def get_istanbul_now():
    return datetime.now(pytz.timezone('Europe/Istanbul'))

@st.cache_data(ttl=600)
def fetch_tefas_data(font_list):
    try:
        crawler = Crawler()
        today = get_istanbul_now()
        start_date = (today - timedelta(days=5)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        
        data = crawler.fetch(start_date, end_date)
        
        if data is not None and not data.empty:
            filtered = data[data['code'].isin(font_list)]
            if not filtered.empty:
                latest_date = filtered['date'].max()
                return filtered[filtered['date'] == latest_date]
        return None
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        return None

def main():
    st.title("📈 Canlı Fon Takip Paneli")
    st.write(f"Son Güncelleme: **{get_istanbul_now().strftime('%d.%m.%Y %H:%M:%S')}**")

    my_funds = ["TLY", "DFI", "PHE"]
    
    with st.spinner('TEFAS verileri işleniyor...'):
        df = fetch_tefas_data(my_funds)

    if df is not None and not df.empty:
        # Sütun isimlerini kontrol et
        cols_in_df = df.columns.tolist()
        ret_col = 'daily_return' if 'daily_return' in cols_in_df else ('return' if 'return' in cols_in_df else None)
        price_col = 'price' if 'price' in cols_in_df else ('birim_fiyat' if 'birim_fiyat' in cols_in_df else None)

        # Metrik Kartları
        m_cols = st.columns(3)
        for i, code in enumerate(my_funds):
            fund_row = df[df['code'] == code]
            if not fund_row.empty:
                row = fund_row.iloc[0]
                
                # Değerleri güvenli çek
                price_val = float(row[price_col]) if price_col else 0.0
                ret_val = float(row[ret_col]) if ret_col else 0.0
                
                # Parantez hatasının düzeltildiği kısım burası
                m_cols[i].metric(
                    label=f"Fon: {code}", 
                    value=f"{price_val:.4f} TL", 
                    delta=f"%{ret_val:.2f}"
                )
        
        st.divider()
        st.subheader("📋 Veri Tablosu")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Şu an TEFAS'tan veri alınamadı. Lütfen 'Yenile' butonuna basınız.")

    if st.button("🔄 Verileri Yenile"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()
