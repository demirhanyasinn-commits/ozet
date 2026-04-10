import streamlit as st
import pandas as pd
from tefas import Crawler
from datetime import datetime, timedelta
import pytz

st.set_page_config(page_title="Fon Analiz Paneli", layout="wide")

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
                return filtered[filtered['date'] == filtered['date'].max()]
        return None
    except: return None

def main():
    st.title("📈 Fon Tahmin ve Analiz Paneli")
    
    # 1. PİYASA VERİLERİ (Tahmin için kullanıcıdan veya API'den gelen veriler)
    st.sidebar.header("📊 Anlık Piyasa Hareketleri")
    hisse_degisim = st.sidebar.slider("BIST 100 Değişim (%)", -5.0, 5.0, 1.2)
    dolar_degisim = st.sidebar.slider("USD/TRY Değişim (%)", -5.0, 5.0, 0.5)
    ons_degisim = st.sidebar.slider("Ons Altın Değişim (%)", -5.0, 5.0, -0.2)

    # 2. FON PORTFÖY DAĞILIMLARI (Örnek Oranlar)
    # Bu oranları fonun KAP bildirimine göre güncelleyebilirsin
    portfoy_yapisi = {
        "TLY": {"Hisse": 0.80, "Döviz": 0.10, "Faiz": 0.10},
        "DFI": {"Hisse": 0.40, "Döviz": 0.50, "Faiz": 0.10},
        "PHE": {"Hisse": 0.10, "Döviz": 0.80, "Faiz": 0.10}
    }

    my_funds = ["TLY", "DFI", "PHE"]
    df = fetch_tefas_data(my_funds)

    if df is not None and not df.empty:
        m_cols = st.columns(3)
        
        for i, code in enumerate(my_funds):
            row = df[df['code'] == code].iloc[0]
            
            # --- TAHMİN HESAPLAMA MANTIĞI ---
            dagilim = portfoy_yapisi[code]
            tahmini_getiri = (
                (dagilim["Hisse"] * hisse_degisim) + 
                (dagilim["Döviz"] * dolar_degisim) + 
                (dagilim["Faiz"] * 0.15) # Günlük sabit faiz getirisi varsayımı
            )
            
            with m_cols[i]:
                st.subheader(f"Fon: {code}")
                st.metric("Dünkü Kapanış", f"{row['price']:.4f} TL", f"%{row['daily_return']:.2f}")
                st.metric("BUGÜN TAHMİNİ", f"{(row['price'] * (1 + tahmini_getiri/100)):.4f} TL", f"%{tahmini_getiri:.2f}", delta_color="normal")
                
                # Küçük bir ilerleme çubuğu ile dağılımı göster
                st.caption(f"Dağılım: Hisse %{dagilim['Hisse']*100:.0f} | Döviz %{dagilim['Döviz']*100:.0f}")

        st.divider()
        st.subheader("📋 Güncel TEFAS Verileri")
        st.dataframe(df[['code', 'title', 'price', 'daily_return', 'date']], use_container_width=True, hide_index=True)
    
    else:
        st.warning("Veriler yüklenemedi, lütfen yenileyin.")

if __name__ == "__main__":
    main()
