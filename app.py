import streamlit as st
import pandas as pd
import yfinance as yf
from tefas import Crawler
from datetime import datetime, timedelta
import pytz

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="PRO Fon Simülatörü", layout="wide", initial_sidebar_state="collapsed")

# 2. Premium Navigasyon ve Kart Tasarımı (image_2665ca.png referanslı)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { background-color: #0e0e0e; font-family: 'Inter', sans-serif; }
    
    .ticker-container {
        background-color: #161616; padding: 12px 20px; border-radius: 12px;
        display: flex; justify-content: space-between; align-items: center;
        border: 1px solid #262626; margin-bottom: 25px; overflow-x: auto;
    }
    .ticker-item { text-align: center; min-width: 125px; padding: 0 15px; border-right: 1px solid #333; }
    .ticker-item:last-child { border-right: none; }
    .ticker-label { color: #888; font-size: 0.7rem; font-weight: 600; }
    .ticker-value { color: #fff; font-size: 0.95rem; font-weight: 700; display: block; }
    .delta-up { color: #00ff88; font-size: 0.8rem; }
    .delta-down { color: #ff4b4b; font-size: 0.8rem; }

    .fund-card {
        background-color: #161616; border-radius: 12px; padding: 22px; 
        margin-bottom: 20px; border: 1px solid #262626; border-left: 5px solid #007bff;
    }
    .fund-title { color: #fff; font-size: 1.4rem; font-weight: 700; margin-bottom: 5px; }
    .fund-subtitle { color: #666; font-size: 0.75rem; margin-bottom: 15px; height: 32px; }
    .est-label { color: #999; font-size: 0.75rem; text-transform: uppercase; }
    .est-value { color: #00ff88; font-size: 2.2rem; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

def get_istanbul_now():
    return datetime.now(pytz.timezone('Europe/Istanbul'))

@st.cache_data(ttl=60)
def fetch_market_data():
    symbols = {"USDTRY": "USDTRY=X", "BIST100": "XU100.IS", "BTCUSD": "BTC-USD", "GOLD": "GC=F"}
    results = {}
    for name, sym in symbols.items():
        try:
            t = yf.Ticker(sym)
            h = t.history(period="2d")
            if len(h) >= 2:
                last, prev = h['Close'].iloc[-1], h['Close'].iloc[-2]
                results[name] = {"val": last, "pct": ((last - prev) / prev) * 100}
        except: continue
    return results

@st.cache_data(ttl=600)
def fetch_tefas_data(font_list):
    try:
        crawler = Crawler()
        today = get_istanbul_now()
        # Veri boşluğunu önlemek için 10 günlük veri çekiyoruz
        data = crawler.fetch((today - timedelta(days=10)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
        if data is not None and not data.empty:
            return data[data['code'].isin(font_list)].sort_values('date').drop_duplicates('code', keep='last')
    except: return None

def main():
    market = fetch_market_data()
    my_funds = ["TLY", "DFI", "PHE", "PBR"]
    
    # 3. Üst Ticker Navigasyonu
    if market:
        t_html = '<div class="ticker-container">'
        for k, v in market.items():
            color = "delta-up" if v['pct'] >= 0 else "delta-down"
            val_f = f"{int(v['val']):,}" if "BTC" in k else f"{v['val']:.2f}"
            t_html += f'<div class="ticker-item"><span class="ticker-label">{k}</span><span class="ticker-value">{val_f}</span><span class="ticker-delta {color}">%{v['pct']:.2f}</span></div>'
        t_html += '</div>'
        st.markdown(t_html, unsafe_allow_html=True)

    # 4. Kalibre Edilmiş Hesaplama Motoru (image_26de41.jpg referanslı)
    # Hisse ağırlıkları profesyonel tablodaki etki oranlarına göre güncellendi
    portfoy_yapisi = {
        "TLY": {"H": 0.84, "D": 0.05, "S": 0.11, "n": "Tera Portföy Birinci Serbest Fon"},
        "DFI": {"H": 0.12, "D": 0.78, "S": 0.10, "n": "Atlas Portföy Serbest Fon"},
        "PHE": {"H": 0.86, "D": 0.04, "S": 0.10, "n": "Pusula Portföy Hisse Fonu"},
        "PBR": {"H": 0.38, "D": 0.42, "S": 0.20, "n": "Pusula Portföy Birinci Değişken"}
    }

    df = fetch_tefas_data(my_funds)
    if df is not None and market:
        grid = st.columns(len(my_funds))
        bist = market.get("BIST100", {"pct":0})["pct"]
        usd = market.get("USDTRY", {"pct":0})["pct"]

        for i, code in enumerate(my_funds):
            f_data = df[df['code'] == code]
            if not f_data.empty:
                row = f_data.iloc[0]
                c = portfoy_yapisi[code]
                
                # %0.25'lik fazlalığı gideren hassas hesaplama
                # Günlük repo/faiz etkisi (0.0012) eklendi ve toplam %2 oranında törpülendi
                est = ((c["H"] * bist) + (c["D"] * usd) + (c["S"] * 0.12)) * 0.98
                
                with grid[i]:
                    st.markdown(f"""
                        <div class="fund-card">
                            <div class="fund-title">{code}</div>
                            <div class="fund-subtitle">{c['n']}</div>
                            <div class="est-label">GÜN SONU TAHMİNİ</div>
                            <div class="est-value">%{est:+.2f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    # Fiyatı sayıya çevirerek KeyError ve Tip hatasını önlüyoruz
                    fiyat = pd.to_numeric(row['price'])
                    st.metric("Tahmini Fiyat", f"{fiyat * (1+est/100):.4f} TL", f"%{est:.2f}")

if __name__ == "__main__":
    main()
