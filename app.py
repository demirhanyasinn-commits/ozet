import streamlit as st
import yfinance as yf
import pandas as pd

# Sayfa Yapılandırması
st.set_page_config(page_title="Fon Takip Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Karanlık tema için ufak bir CSS dokunuşu
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    </style>
    """, unsafe_allow_html=True)

# Veri çekme fonksiyonu
@st.cache_data(ttl=300) # 5 dakikada bir veriyi yeniler
def get_live_data():
    try:
        # BIST100 ve USD/TRY verileri (Son 2 günün verisi kıyaslama için gerekli)
        bist = yf.Ticker("XU100.IS").history(period="2d")
        usd = yf.Ticker("USDTRY=X").history(period="2d")
        
        # Değişim hesaplama: (Son Fiyat / Önceki Kapanış) - 1
        bist_pc = ((bist['Close'].iloc[-1] / bist['Close'].iloc[-2]) - 1) * 100
        usd_pc = ((usd['Close'].iloc[-1] / usd['Close'].iloc[-2]) - 1) * 100
        return bist_pc, usd_pc
    except Exception as e:
        return 0.0, 0.0

# Fon Listesi ve Tahmini Duyarlılık (Beta) Katsayıları
def get_fund_estimates(bist_pc, usd_pc):
    # Bu katsayılar fonun BIST100 hareketine ne kadar eşlik ettiğini temsil eder
    funds = {
        "TLY": {"name": "Tera Portföy Birinci Serbest", "beta": 0.92},
        "DFI": {"name": "Atlas Portföy Serbest Fon", "beta": 0.78},
        "PHE": {"name": "Pusula Portföy Hisse Fon", "beta": 1.05},
        "PBR": {"name": "Pusula Portföy Birinci Değişken", "beta": 0.65},
        "KHA": {"name": "İstanbul Portföy Birinci Değişken", "beta": 0.82}
    }
    
    results = {}
    for code, info in funds.items():
        # Tahmini getiri = Endeks değişimi * Fonun hisse yoğunluğu
        prediction = bist_pc * info['beta']
        results[code] = {"name": info['name'], "val": prediction}
    return results

# Verileri Çek
bist_pc, usd_pc = get_live_data()

# Üst Bilgi Paneli
st.markdown(f"## BIST100: %{bist_pc:+.2f} | USDTRY: %{usd_pc:+.2f}")
st.write("---")

# Kartları Oluşturma
fund_results = get_fund_estimates(bist_pc, usd_pc)
cols = st.columns(len(fund_results))

for i, (code, data) in enumerate(fund_results.items()):
    with cols[i]:
        # Pozitif/Negatif durumuna göre renk paleti belirleme
        if data['val'] >= 0:
            bg_color = "#064e3b"     # Koyu Yeşil
            border_color = "#10b981" # Parlak Yeşil Şerit
            text_color = "#a7f3d0"   # İkincil Yazı Rengi
        else:
            bg_color = "#450a0a"     # Koyu Kırmızı
            border_color = "#ef4444" # Parlak Kırmızı Şerit
            text_color = "#fecaca"   # İkincil Yazı Rengi
        
        # HTML Kart Tasarımı
        st.markdown(f"""
        <div style="
            background-color: {bg_color}; 
            padding: 20px; 
            border-radius: 15px; 
            border-left: 7px solid {border_color}; 
            min-height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.3);
            ">
            <div>
                <p style="color: #ffffff; font-weight: 800; margin-bottom: 0; font-size: 1.4em; letter-spacing: 1px;">{code}</p>
                <p style="color: {text_color}; font-size: 0.85em; margin-top: 5px; line-height: 1.2; height: 45px; overflow: hidden;">{data['name']}</p>
            </div>
            <div>
                <p style="color: #ffffff; font-size: 0.75em; margin-bottom: 2px; font-weight: bold; opacity: 0.8;">GÜNLÜK BEKLENTİ</p>
                <h2 style="color: #ffffff; margin: 0; font-size: 2em; font-weight: 900;">%{data['val']:+.2f}</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Alt Bilgi Notu
st.caption("Veriler yfinance üzerinden çekilmektedir ve tahmini katsayılar ile hesaplanmaktadır. Kesinlik içermez.")
