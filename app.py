import streamlit as st
import pandas as pd
import yfinance as yf
from tefas import Crawler
from datetime import datetime, timedelta
import pytz

# 1. Sayfa Yapılandırması
st.set_page_config(page_title="PRO Fon Simülatörü", layout="wide", initial_sidebar_state="collapsed")

# 2. Premium Tasarım ve Navigasyon CSS (image_2665ca.png referans alınmıştır)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0f0f0f;
        font-family: 'Inter', sans-serif;
    }

    /* Üst Navigasyon Ticker Bar */
    .ticker-container {
        background-color: #1a1a1a;
        padding: 10px 20px;
        border-radius: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #2d2d2d;
        margin-bottom: 25px;
        overflow-x: auto;
    }
    .ticker-item {
        text-align: center;
        min-width: 120px;
        padding: 0 15px;
        border-right: 1px solid #333;
    }
    .ticker-item:last-child { border-right: none; }
    .ticker-label { color: #888; font-size: 0.75rem; font-weight: 600; }
    .ticker-value { color: #fff; font-size: 1rem; font-weight: 700; display: block; }
    .ticker-delta { font-size: 0.85rem; font-weight: 600; }
    .delta-up { color: #00ff88; }
    .delta-down { color: #ff4b4b; }

    /* Fon Kartları Tasarımı */
    .fund-card {
        background-color: #1a1a1a;
        border-left: 4px solid #007bff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border-top: 1px solid #2d2d2d;
        border-right: 1px solid #2d2d2d;
        border-bottom: 1px solid #2d2d2d;
        transition: all 0.3s ease;
    }
    .fund-card:hover {
        background-color: #222;
        transform: translateY(-3px);
    }
    .fund-title { color: #fff; font-size: 1.2rem; font-weight: 700; margin-bottom: 2px; }
    .fund-subtitle { color: #777; font-size: 0.8rem; margin-bottom: 15px; }
    .getiri-label { color: #888; font-size: 0.75rem; }
    .getiri-value { color: #00ff88; font-size: 1.8rem; font-weight: 700; }
    
    /* Metrik Gizleme (Default Streamlit metriklerini card içine uydurmak için) */
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

def get_istanbul_now():
    return datetime.now(pytz.timezone('Europe/Istanbul'))

@st.cache_data(ttl=60)
def fetch_market_data():
    try:
        # Ticker verileri: USDTRY, BIST100, BIST30, BTC, GOLD, SILVER
        symbols = {
            "USDTRY": "USDTRY=X", "BIST100": "XU100.IS", "BIST30": "XU030.IS",
            "BTCUSD": "BTC-USD", "GOLD_TL": "GC=F", "SILVER_TL": "SI=F"
        }
        data = {}
        for name, sym in symbols.items():
            t = yf.Ticker(sym)
            h = t.history(period="2d")
            if not h.empty:
                last = h['Close'].iloc[-1]
                prev = h['Close'].iloc[-2]
                pct = ((last - prev) / prev) * 100
                data[name] = {"val": last, "pct": pct}
        return data
    except: return {}

@st.cache_data(ttl=600)
def fetch_tefas_data(font_list):
    try:
        crawler = Crawler()
        today = get_istanbul_now()
        raw = crawler.fetch((today - timedelta(days=7)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
        if raw is not None and not raw.empty:
            filtered = raw[raw['code'].isin(font_list)]
            return filtered[filtered['date'] == filtered['date'].max()]
    except: return None

def main():
    # 3. Üst Bilgilendirme Navigasyonu (Ticker Bar)
    m = fetch_market_data()
    if m:
        cols_html = ""
        for k, v in m.items():
            color_class = "delta-up" if v['pct'] >= 0 else "delta-down"
            sign = "+" if v['pct'] >= 0 else ""
            cols_html += f"""
                <div class="ticker-item">
                    <span class="ticker-label">{k}</span>
                    <span class="ticker-value">{v['val']:.2f if 'BTC' not in k else int(v['val'])}</span>
                    <span class="ticker-delta {color_class}">{sign}{v['pct']:.2f}%</span>
                </div>
            """
        st.markdown(f'<div class="ticker-container">{cols_html}</div>', unsafe_allow_html=True)

    # 4. Fon Tahminleri
    my_funds = ["TLY", "DFI", "PHE", "PBR"]
    # Dağılım oranları (KAP verilerine göre optimize edilebilir)
    portfoy_yapisi = {
        "TLY": {"Hisse": 0.90, "Dolar": 0.05, "Sabit": 0.05, "desc": "Tera Portföy Birinci Serbest Fon"},
        "DFI": {"Hisse": 0.15, "Dolar": 0.75, "Sabit": 0.10, "desc": "Atlas Portföy Serbest Fon"},
        "PHE": {"Hisse": 0.85, "Dolar": 0.10, "Sabit": 0.05, "desc": "Pusula Portföy Hisse Senedi Fonu"},
        "PBR": {"Hisse": 0.40, "Dolar": 0.40, "Sabit": 0.20, "desc": "Pusula Portföy Birinci Değişken Fon"}
    }

    df = fetch_tefas_data(my_funds)
    
    if df is not None:
        grid = st.columns(3)
        for i, code in enumerate(my_funds):
            col_idx = i % 3
            fund_data = df[df['code'] == code]
            
            if not fund_data.empty:
                row = fund_data.iloc[0]
                struct = portfoy_yapisi[code]
                
                # Tahmin Motoru
                bist_chg = m.get("BIST100", {"pct":0})["pct"]
                usd_chg = m.get("USDTRY", {"pct":0})["pct"]
                est_chg = (struct["Hisse"] * bist_chg) + (struct["Dolar"] * usd_chg) + (struct.get("Sabit",0) * 0.12)
                
                with grid[col_idx]:
                    st.markdown(f"""
                        <div class="fund-card">
                            <div class="fund-title">{code}</div>
                            <div class="fund-subtitle">{struct['desc']}</div>
                            <div class="getiri-label">Anlık Tahmini Getiri</div>
                            <div class="getiri-value">{"%+ .2f" % est_chg}%</div>
                            <p style="color:#555; font-size:0.7rem; margin-top:10px;">Son Güncelleme: {get_istanbul_now().strftime('%H:%M')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    # Alt kısma detay metrikleri (fiyat vb.) opsiyonel eklenebilir
                    st.metric("Tahmini Fiyat", f"{float(row['price']) * (1+est_chg/100):.4f} TL", f"{est_chg:.2f}%")

    if st.button("Verileri Zorla Güncelle"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()
