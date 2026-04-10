import streamlit as st
import pandas as pd
import yfinance as yf
from tefas import Crawler
from datetime import datetime, timedelta
import pytz

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="PRO Fon Simülatörü", layout="wide", initial_sidebar_state="collapsed")

# 2. Premium Tasarım CSS (image_2665ca.png ve mobil uyum referanslı)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { background-color: #0e0e0e; font-family: 'Inter', sans-serif; }
    
    /* Üst Ticker Navigasyon */
    .ticker-container {
        background-color: #161616; padding: 12px 20px; border-radius: 12px;
        display: flex; justify-content: space-between; align-items: center;
        border: 1px solid #262626; margin-bottom: 25px; overflow-x: auto;
    }
    .ticker-item { text-align: center; min-width: 120px; padding: 0 15px; border-right: 1px solid #333; }
    .ticker-item:last-child { border-right: none; }
    .ticker-label { color: #888; font-size: 0.7rem; font-weight: 600; }
    .ticker-value { color: #fff; font-size: 0.95rem; font-weight: 700; display: block; }
    .delta-up { color: #00ff88; font-size: 0.8rem; }
    .delta-down { color: #ff4b4b; font-size: 0.8rem; }

    /* Fon Kartları */
    .fund-card {
        background-color: #161616; border-left: 4px solid #007bff;
        border-radius: 12px; padding: 20px; margin-bottom: 20px;
        border: 1px solid #262626; border-left: 4px solid #007bff;
    }
    .fund-title { color: #fff; font-size: 1.3rem; font-weight: 700; }
    .fund-subtitle { color: #666; font-size: 0.75rem; margin-bottom: 15px; }
    .est-label { color: #999; font-size: 0.75rem; }
    .est-value { color: #00ff88; font-size: 2rem; font-weight: 800; }
    
    /* Streamlit Metrik Düzenleme */
    [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
    </style>
    """, unsafe_allow_html=True)

def get_istanbul_now():
    # IndentationError burada düzeldi
    return datetime.now(pytz.timezone('Europe/Istanbul'))

@st.cache_data(ttl=60)
def fetch_market_data():
    symbols = {
        "USDTRY": "USDTRY=X", "BIST100": "XU100.IS", "BIST30": "XU030.IS",
        "BTCUSD": "BTC-USD", "GOLD": "GC=F", "SILVER": "SI=F"
    }
    results = {}
    for name, sym in symbols.items():
        try:
            t = yf.Ticker(sym)
            h = t.history(period="2d")
            if len(h) >= 2:
                last = h['Close'].iloc[-1]
                prev = h['Close'].iloc[-2]
                pct = ((last - prev) / prev) * 100
                results[name] = {"val": last, "pct": pct}
        except: continue
    return results

@st.cache_data(ttl=600)
def fetch_tefas_data(font_list):
    try:
        crawler = Crawler()
        today = get_istanbul_now()
        data = crawler.fetch((today - timedelta(days=7)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
        if data is not None and not data.empty:
            return data[data['code'].isin(font_list)].drop_duplicates('code', keep='last')
    except: return None

def main():
    market = fetch_market_data()
    
    # 3. Üst Ticker Navigasyonu
    if market:
        t_html = '<div class="ticker-container">'
        for k, v in market.items():
            color = "delta-up" if v['pct'] >= 0 else "delta-down"
            val_f = f"{int(v['val']):,}" if "BTC" in k else f"{v['val']:.2f}"
            t_html += f"""
                <div class="ticker-item">
                    <span class="ticker-label">{k}</span>
                    <span class="ticker-value">{val_f}</span>
                    <span class="ticker-delta {color}">%{v['pct']:.2f}</span>
                </div>"""
        t_html += '</div>'
        st.markdown(t_html, unsafe_allow_html=True)

    # 4. Fon Simülasyon Kartları
    my_funds = ["TLY", "DFI", "PHE", "PBR"]
    portfoy_yapisi = {
        "TLY": {"H": 0.88, "D": 0.07, "desc": "Tera Portföy Birinci Serbest Fon"},
        "DFI": {"H": 0.15, "D": 0.75, "desc": "Atlas Portföy Serbest Fon"},
        "PHE": {"H": 0.85, "D": 0.10, "desc": "Pusula Portföy Hisse Fonu"},
        "PBR": {"H": 0.40, "D": 0.40, "desc": "Pusula Portföy Birinci Değişken"}
    }

    df = fetch_tefas_data(my_funds)
    if df is not None:
        grid = st.columns(len(my_funds))
        bist = market.get("BIST100", {"pct":0})["pct"]
        usd = market.get("USDTRY", {"pct":0})["pct"]

        for i, code in enumerate(my_funds):
            f_data = df[df['code'] == code]
            if not f_data.empty:
                row = f_data.iloc[0]
                conf = portfoy_yapisi[code]
                est = (conf["H"] * bist) + (conf["D"] * usd) + 0.12 # +0.12 günlük repo/faiz tahmini
                
                with grid[i]:
                    st.markdown(f"""
                        <div class="fund-card">
                            <div class="fund-title">{code}</div>
                            <div class="fund-subtitle">{conf['desc']}</div>
                            <div class="est-label">AKŞAM BEKLENTİ</div>
                            <div class="est-value">%{est:+.2f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    st.metric("Simüle Fiyat", f"{float(row['price'])*(1+est/100):.4f}", f"{est:.2f}%")

    st.markdown(f"<p style='text-align:center; color:#444; margin-top:30px;'>{get_istanbul_now().strftime('%H:%M:%S')} - Canlı Veri Akışı Aktif</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
