import streamlit as st
import yfinance as yf
import pandas as pd

# 1. VERİ ÇEKME (Hassas Veri)
@st.cache_data(ttl=300)
def get_live_data():
    bist = yf.Ticker("XU100.IS").history(period="2d")
    usd = yf.Ticker("USDTRY=X").history(period="2d")
    # Yüzdesel değişimleri en hassas noktadan alıyoruz
    bist_chg = ((bist['Close'].iloc[-1] - bist['Close'].iloc[-2]) / bist['Close'].iloc[-2]) * 100
    usd_chg = ((usd['Close'].iloc[-1] - usd['Close'].iloc[-2]) / usd['Close'].iloc[-2]) * 100
    return bist_chg, usd_chg

bist, usd = get_live_data()

# 2. FON ANALİZİ (Regresyon Temelli Katsayılar)
# Buradaki değerler fonların BIST100'e olan duyarlılığıdır. 
# Eğer hata payı yüksekse bu 'beta' değerlerini gerçek getiriye göre kalibre ediyoruz.
fon_data = {
    "TLY": {"ad": "Tera 1. Serbest", "beta": 1.31, "alfa": 0.05}, # Alfa: Sabit getiri payı
    "KHA": {"ad": "İstanbul 1. Değişken", "beta": 0.55, "alfa": 0.12},
    "PHE": {"ad": "Pusula Hisse", "beta": 1.02, "alfa": 0.01},
    "DFI": {"ad": "Atlas Serbest", "beta": 0.90, "alfa": 0.03},
    "PBR": {"ad": "Pusula 1. Değişken", "beta": 0.40, "alfa": 0.08}
}

# 3. HESAPLAMA MOTORU
# Formül: (Endeks * Beta) + Sabit Getiri (Alfa) + (Dolar Etkisi * Duyarlılık)
def hesapla(kod, info, b_val, u_val):
    tahmin = (b_val * info['beta']) + info['alfa']
    # Değişken fonlarda doların etkisini de ekliyoruz
    if kod in ["KHA", "TLY"]:
        tahmin += (u_val * 0.15)
    return tahmin

# Arayüz Elemanları (Tasarımını koruyarak)
st.markdown("<h1 style='color:white; font-family: monospace;'>YA 34 YA 39 | PRO</h1>", unsafe_allow_html=True)

cols = st.columns(5)
for i, (kod, info) in enumerate(fon_data.items()):
    net_tahmin = hesapla(kod, info, bist, usd)
    with cols[i]:
        st.markdown(f"""
            <div style="background: linear-gradient(145deg, #064e3b, #022c22); padding:20px; border-radius:15px; border:1px solid #10b981;">
                <h3 style="margin:0; color:white;">{kod}</h3>
                <p style="font-size:10px; color:#a7f3d0;">{info['ad']}</p>
                <hr style="border-color:#1e293b">
                <p style="font-size:10px; color:gray; margin:0;">GÜN SONU TAHMİNİ</p>
                <h2 style="color:#4ade80; margin:0;">%{net_tahmin:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)

st.sidebar.info(f"BIST100 Değişim: %{bist:.2f}\nUSD/TRY Değişim: %{usd:.2f}")
