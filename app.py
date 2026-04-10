import streamlit as st
import pandas as pd
import yfinance as yf
from tefas import Crawler
from datetime import datetime, timedelta
import pytz

st.set_page_config(page_title="Fon Tahmin Dashboard", layout="wide")

def get_istanbul_now():
    return datetime.now(pytz.timezone('Europe/Istanbul'))

@st.cache_data(ttl=300)
def fetch_market_data():
    try:
        # Tickers: BIST100, USD/TRY, Ons Altın
        tickers = {"BIST100": "XU100.IS", "USDTRY": "USDTRY=X", "Altın": "GC=F"}
        results = {}
        for name, ticker in tickers.items():
            stock = yf.Ticker(ticker)
            hist = stock.history(period="3d")
            if len(hist) >= 2:
                # En son kapanış ve bir önceki kapanış arasındaki fark
                current = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                results[name] = ((current - prev) / prev) * 100
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
        start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")
        data = crawler.fetch(start, end)
        if data is not None and not data.empty:
            filtered = data[data['code'].isin(font_list)]
            if not filtered.empty:
                return filtered[filtered['date'] == filtered['date'].max()]
        return None
    except: return None

def main():
    st.title("🚀 Canlı Fon Tahmin ve Analiz")
    
    # 1. PİYASA VERİLERİ (SOL PANEL)
    market = fetch_market_data()
    with st.sidebar:
        st.header("🌍 Canlı Piyasa")
        st.metric("BIST 100", f"%{market['BIST100']:.2f}")
        st.metric("USD/TRY", f"%{market['USDTRY']:.2f}")
        st.metric("Ons Altın", f"%{market['Altın']:.2f}")
        st.divider()
        st.caption("Veriler yfinance üzerinden anlık çekilir.")

    # 2. FON DAĞILIMLARI (Buradaki oranları fonuna göre bir kez güncelle)
    portfoy_yapisi = {
        "TLY": {"Hisse": 0.90, "Döviz": 0.05, "Altın": 0.05},
        "DFI": {"Hisse": 0.20, "Döviz": 0.70, "Altın": 0.10},
        "PHE": {"Hisse": 0.85, "Döviz": 0.10, "Altın": 0.05}
    }

    my_funds = ["TLY", "DFI", "PHE"]
    df = fetch_tefas_data(my_funds)

    if df is not None and not df.empty:
        # Sütun isimlerindeki hatayı önlemek için otomatik bulma
        cols = df.columns.tolist()
        p_col = next((c for c in ['price', 'birim_fiyat'] if c in cols), None)
        r_col = next((c for c in ['daily_return', 'getiri', 'return'] if c in cols), None)

        st.subheader("🔮 Bugünün Tahmini Getirileri")
        m_cols = st.columns(3)
        
        for i, code in enumerate(my_funds):
            fund_row = df[df['code'] == code]
            if not fund_row.empty:
                row = fund_row.iloc[0]
                dagilim = portfoy_yapisi[code]
                
                # Fiyat ve Getiri değerlerini güvenli çek
                old_price = float(row[p_col]) if p_col else 0.0
                old_return = float(row[r_col]) if r_col else 0.0
                
                # Tahmin Hesaplama
                tahmini_yuzde = (
                    (dagilim["Hisse"] * market["BIST100"]) + 
                    (dagilim["Döviz"] * market["USDTRY"]) + 
                    (dagilim["Altın"] * market["Altın"])
                )
                tahmini_fiyat = old_price * (1 + tahmini_yuzde / 100)
                
                with m_cols[i]:
                    st.info(f"Fon: **{code}**")
                    st.metric("Resmi (Dün)", f"{old_price:.4f} TL", f"%{old_return:.2f}")
                    st.metric("TAHMİNİ (Bugün)", f"{tahmini_fiyat:.4f} TL", f"%{tahmini_yuzde:.2f}", delta_color="normal")
        
        st.divider()
        st.subheader("📊 TEFAS Kayıtları")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("Veriler şu an TEFAS'tan çekilemiyor, lütfen bekleyin.")

    if st.button("🔄 Verileri Şimdi Güncelle"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()
