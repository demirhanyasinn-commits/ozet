import streamlit as st
import pandas as pd
import yfinance as yf
from tefas import Crawler
from datetime import datetime, timedelta
import pytz

# 1. SAYFA AYARLARI VE PREMIUM CSS
st.set_page_config(page_title="Fon Simülatörü Pro", layout="wide", initial_sidebar_state="collapsed")

# Premium Tasarım İçin CSS Enjeksiyonu
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Metrik Kartları Tasarımı */
    [data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #58a6ff;
    }
    
    /* Yazı Tipleri ve Başlıklar */
    h1, h2, h3 {
        color: #f0f6fc;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }
    
    /* Bilgi Kutucukları (st.info) */
    .stAlert {
        border-radius: 12px;
        background-color: #0d1117;
        border: 1px solid #21262d;
    }

    /* Tablo Tasarımı */
    .stDataFrame {
        border-radius: 10px;
        border: 1px solid #30363d;
    }

    /* Mobil Uyumluluk İçin Boşluk Ayarları */
    @media (max-width: 640px) {
        .stMetric {
            margin-bottom: 15px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def get_istanbul_now():
    return datetime.now(pytz.timezone('Europe/Istanbul'))

@st.cache_data(ttl=60)
def fetch_live_market():
    try:
        tickers = {"BIST100": "XU100.IS", "USDTRY": "USDTRY=X", "ONS": "GC=F"}
        market_data = {}
        for name, ticker in tickers.items():
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            if len(hist) >= 2:
                change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                market_data[name] = change
            else: market_data[name] = 0.0
        return market_data
    except: return {"BIST100": 0.0, "USDTRY": 0.0, "ONS": 0.0}

@st.cache_data(ttl=3600)
def fetch_official_tefas(font_list):
    try:
        crawler = Crawler()
        today = get_istanbul_now()
        data = crawler.fetch((today - timedelta(days=7)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
        if data is not None and not data.empty:
            filtered = data[data['code'].isin(font_list)]
            return filtered[filtered['date'] == filtered['date'].max()]
        return None
    except: return None

def main():
    # Üst Başlık Bölümü
    c1, c2 = st.columns([3, 1])
    with c1:
        st.title("💎 Fon Gün Sonu Simülatörü")
        st.markdown(f"<p style='color:#8b949e;'>Piyasa Analizi ve Tahminleme Modülü | {get_istanbul_now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
    with c2:
        if st.button("🔄 Verileri Tazele"):
            st.cache_data.clear()
            st.rerun()

    # 1. PİYASA ÖZETİ (Dashboard Üst Şerit)
    market = fetch_live_market()
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Borsa İstanbul", "XU100", f"%{market['BIST100']:.2f}")
    m_col2.metric("Dolar/TL", "USDTRY", f"%{market['USDTRY']:.2f}")
    m_col3.metric("Altın (Ons)", "GOLD", f"%{market['ONS']:.2f}")

    # 2. FON SİMÜLASYONU
    # Dağılımları fonun karakterine göre buraya giriyoruz
    portfoy_yapisi = {
        "TLY": {"Hisse": 0.88, "Dolar": 0.07, "Sabit": 0.05},
        "DFI": {"Hisse": 0.15, "Dolar": 0.75, "Sabit": 0.10},
        "PHE": {"Hisse": 0.82, "Dolar": 0.13, "Sabit": 0.05}
    }

    my_funds = ["TLY", "DFI", "PHE"]
    df = fetch_official_tefas(my_funds)

    if df is not None and not df.empty:
        st.markdown("<h2 style='margin-top:40px;'>🔮 Gün Sonu Tahminleri</h2>", unsafe_allow_html=True)
        
        cols = df.columns.tolist()
        p_col = next((c for c in ['price', 'birim_fiyat'] if c in cols), None)
        
        f_cols = st.columns(3)
        for i, code in enumerate(my_funds):
            row = df[df['code'] == code].iloc[0]
            dagilim = portfoy_yapisi[code]
            
            # Hesaplama Motoru
            tahmini_yuzde = (dagilim["Hisse"] * market["BIST100"]) + (dagilim["Dolar"] * market["USDTRY"]) + (dagilim.get("Sabit", 0) * 0.12)
            resmi_fiyat = float(row[p_col])
            tahmini_fiyat = resmi_fiyat * (1 + tahmini_yuzde / 100)

            with f_cols[i]:
                # Her fonu bir kart içinde gösteriyoruz
                st.markdown(f"**{code}**")
                st.metric(
                    label="Beklenen Yeni Fiyat", 
                    value=f"{tahmini_fiyat:.4f} TL", 
                    delta=f"%{tahmini_yuzde:.2f} Tahmin"
                )
                st.caption(f"Dünkü Kapanış: {resmi_fiyat:.4f}")

        st.divider()
        st.subheader("📊 Resmi Veri Tablosu")
        # Tabloyu modern bir görünümle sunuyoruz
        st.dataframe(
            df[['code', 'title', 'price', 'date']], 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.warning("Veriler yükleniyor...")

if __name__ == "__main__":
    main()
