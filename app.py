import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz

# Sayfa Ayarları
st.set_page_config(page_title="YA 34 YA 39 | Terminal", layout="wide")

# Tasarım CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117; }
    .tahmin-kart {
        background: linear-gradient(145deg, #064e3b, #022c22);
        border-radius: 15px; padding: 20px; border: 1px solid #10b981;
        color: white; min-height: 220px;
    }
    .fon-kodu { font-size: 24px; font-weight: bold; }
    .fon-adi { font-size: 11px; color: #a7f3d0; margin-bottom: 25px; height: 35px; }
    .tahmin-deger { font-size: 34px; font-weight: bold; color: #4ade80; }
    
    /* Yan Menü Stilini Koyu Yapma */
    section[data-testid="stSidebar"] { background-color: #1e293b; }
    </style>
    """, unsafe_allow_html=True)

# 1. VERİ ÇEKME
@st.cache_data(ttl=60)
def get_market_data():
    try:
        bist = yf.Ticker("XU100.IS").history(period="2d")
        usd = yf.Ticker("USDTRY=X").history(period="2d")
        bist_chg = ((bist['Close'].iloc[-1] - bist['Close'].iloc[-2]) / bist['Close'].iloc[-2]) * 100
        usd_chg = ((usd['Close'].iloc[-1] - usd['Close'].iloc[-2]) / usd['Close'].iloc[-2]) * 100
        return bist_chg, usd_chg
    except:
        return 0.35, 0.10

bist_degisim, usd_degisim = get_market_data()

# 2. YAN MENÜ (SIDEBAR) - KATSAYI AYARLARI BURADA
st.sidebar.header("⚙️ Fon Kalibrasyonu")
st.sidebar.write("Gerçek verilere göre katsayıları buradan düzeltin:")

# Her fon için manuel katsayı girişleri (Önceki sapmalara göre varsayılanları güncelledim)
katsayi_tly = st.sidebar.number_input("TLY Katsayısı", value=1.71, step=0.01)
katsayi_kha = st.sidebar.number_input("KHA Katsayısı", value=0.88, step=0.01)
katsayi_phe = st.sidebar.number_input("PHE Katsayısı", value=1.05, step=0.01)
katsayi_dfi = st.sidebar.number_input("DFI Katsayısı", value=0.95, step=0.01)
katsayi_pbr = st.sidebar.number_input("PBR Katsayısı", value=0.35, step=0.01)

# 3. HESAPLAMA MANTIĞI
fonlar = {
    "TLY": {"ad": "Tera Portföy Birinci Serbest", "k": katsayi_tly},
    "DFI": {"ad": "Atlas Portföy Serbest Fon", "k": katsayi_dfi},
    "PHE": {"ad": "Pusula Portföy Hisse Fon", "k": katsayi_phe},
    "PBR": {"ad": "Pusula Portföy Birinci Değişken", "k": katsayi_pbr},
    "KHA": {"ad": "İstanbul Portföy Birinci Değişken", "k": katsayi_kha}
}

# 4. ARAYÜZ ELEMANLARI
c1, c2 = st.columns([0.8, 0.2])
with c1:
    st.markdown("<h1 style='color:white; font-family: monospace; letter-spacing: 5px;'>YA 34 YA 39</h1>", unsafe_allow_html=True)
with c2:
    if st.button("🔄 YENİLE"):
        st.cache_data.clear()
        st.rerun()

# Endeks Bilgileri
st.markdown(f"""
    <div style="display: flex; gap: 15px; margin-bottom: 25px;">
        <div style="background:#1e293b; padding:10px; border-radius:10px; border-left:4px solid #10b981;">
            <p style="color:#94a3b8; font-size:10px; margin:0;">BIST100</p>
            <p style="color:#4ade80; font-size:16px; font-weight:bold; margin:0;">%+{bist_degisim:.2f}</p>
        </div>
        <div style="background:#1e293b; padding:10px; border-radius:10px; border-left:4px solid #00f2ff;">
            <p style="color:#94a3b8; font-size:10px; margin:0;">USD/TRY</p>
            <p style="color:#00f2ff; font-size:16px; font-weight:bold; margin:0;">%+{usd_degisim:.2f}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Fon Kartları
cols = st.columns(5)
for i, (kod, info) in enumerate(fonlar.items()):
    # KHA için özel dolar etkisi ekleyebiliriz, diğerleri borsa ağırlıklı
    if kod == "KHA":
        tahmin = (bist_degisim * info['k']) + (usd_degisim * 0.1)
    else:
        tahmin = bist_degisim * info['k']
        
    with cols[i]:
        st.markdown(f"""
            <div class="tahmin-kart">
                <div class="fon-kodu">{kod}</div>
                <div class="fon-adi">{info['ad']}</div>
                <p style="font-size:10px; opacity:0.7; margin-bottom:0;">GÜN SONU TAHMİNİ</p>
                <div class="tahmin-deger">%+{tahmin:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

# Alt Bilgi
tr_saati = datetime.now(pytz.timezone('Europe/Istanbul')).strftime('%H:%M:%S')
st.markdown(f"<br><p style='color:gray; font-size:12px;'>🕒 İstanbul: {tr_saati} | Katsayılar yan menüden optimize edilebilir.</p>", unsafe_allow_html=True)
