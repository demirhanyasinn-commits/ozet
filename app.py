import streamlit as st
import pandas as pd
import yfinance as yf
from tefas import Crawler
from datetime import datetime, timedelta
import pytz

st.set_page_config(page_title="Otomatik Fon Analiz", layout="wide")

def get_istanbul_now():
    return datetime.now(pytz.timezone('Europe/Istanbul'))

@st.cache_data(ttl=300) # Piyasa verilerini 5 dakikada bir tazeler
def fetch_market_data():
    try:
        # Tickers: BIST100, USD/TRY, Ons Altın
        tickers = {"BIST100": "XU100.IS", "USDTRY": "USDTRY=X", "Altın": "GC=F"}
        results = {}
        for name, ticker in tickers.items():
            stock = yf.Ticker(ticker)
            # Günlük değişim yüzdesini al
            hist = stock.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                current_price = hist['Close'].iloc[-1]
                change = ((current_price - prev_close) / prev_close) * 100
                results[name] = change
            else:
                results[name] = 0.0
        return results
    except:
        return {"BIST100": 0.0, "USDTRY": 0.0, "Altın": 0.0}

@st.cache_data(ttl=600)
def fetch_tefas_data(font_list):
    try:
        crawler = Crawler()
        today = get_istanbul_now()
        data = crawler.fetch((today - timedelta(days=5)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
        if data is not None and not data.empty:
            filtered = data[data['code'].isin(font_list)]
            return filtered[filtered['date'] == filtered['date'].max()]
        return None
    except: return None

def main():
    st.title("🚀 Otomatik Fon Tahmin Dashboard")
    
    # 1. CANLI PİYASA VERİLERİNİ ÇEK
    with st.sidebar:
        st.header("🌍 Canlı Piyasa")
        market = fetch_market_data()
        st.metric("BIST 100", f"%{market['BIST100']:.2f}")
        st.metric("USD/TRY", f"%{market['USDTRY']:.2f}")
        st.metric("Ons Altın", f"%{market['Altın']:.2f}")
        st.caption("Veriler Yahoo Finance üzerinden anlık alınmaktadır.")

    # 2. FON PORTFÖY DAĞILIMLARI (Burayı fonun içeriğine göre bir kez ayarla)
    # Örnek: TLY %90 Hisse, DFI %50 Döviz/Eurobond, PHE %80 Hisse gibi...
    portfoy_yapisi = {
        "TLY": {"Hisse": 0.90, "Döviz": 0.05, "Altın": 0.05},
        "DFI": {"Hisse": 0.10, "Döviz": 0.80, "Altın": 0.10},
        "PHE": {"Hisse": 0.85, "Döviz": 0.10, "Altın": 0.05}
    }

    my_funds = ["TLY", "DFI", "PHE"]
    df = fetch_tefas_data(my_funds)

    if df is not None and not df.empty:
        st.subheader("🔮 Bugünün Tahmini Getirileri")
        m_cols = st.columns(3)
        
        for i, code in enumerate(my_funds):
            row = df[df['code'] == code].iloc[0]
            dagilim = portfoy_yapisi[code]
            
            # Otomatik Tahmin Hesabı
            tahmini_getiri = (
                (dagilim["Hisse"] * market["BIST100"]) + 
                (dagilim["Döviz"] * market["USDTRY"]) + 
                (dagilim["Altın"] * market["Altın"])
            )
            
            with m_cols[i]:
                st.info(f"Fon: **{code}**")
                st.metric("Resmi (Dün)", f"{row['price']:.4f} TL", f"%{row['daily_return']:.2f}")
                st.metric("Tahmini (Bugün)", f"{(row['price'] * (1 + tahmini_getiri/100)):.4f} TL", f"%{tahmini_getiri:.2f}")
        
        st.divider()
        st.subheader("📋 TEFAS Detay Listesi")
        st.dataframe(df[['code', 'title', 'price', 'daily_return', 'date']], use_container_width=True, hide_index=True)
    
    else:
        st.warning("Veriler güncelleniyor, lütfen bekleyin...")

if __name__ == "__main__":
    main()
