import streamlit as st
import yfinance as yf

# Sayfa Ayarları
st.set_page_config(page_title="YA 34 YA 39 | Terminal", layout="wide")

# Tasarım CSS (Aynı kaldı)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117; }
    .tahmin-kart {
        background: linear-gradient(145deg, #064e3b, #022c22);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #10b981;
        text-align: left;
        color: white;
        min-height: 220px;
    }
    .fon-kodu { font-size: 24px; font-weight: bold; margin-bottom: 5px; }
    .fon-adi { font-size: 12px; color: #a7f3d0; margin-bottom: 20px; min-height: 40px; }
    .tahmin-etiket { font-size: 10px; font-weight: bold; opacity: 0.8; }
    .tahmin-deger { font-size: 32px; font-weight: bold; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 1. VERİ ÇEKME (Hata burada düzeltildi)
@st.cache_data(ttl=60)
def get_bist_data():
    try:
        # ticker nesnesi üzerinden çekmek daha güvenlidir
        ticker = yf.Ticker("XU100.IS")
        data = ticker.history(period="2d")
        
        if len(data) >= 2:
            current_price = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2]
            change = ((current_price - prev_close) / prev_close) * 100
            return float(change) # Kesinlikle float'a çeviriyoruz
        return 0.35
    except:
        return 0.35

bist_degisim = get_bist_data()

# 2. HESAPLAMA MANTIĞI (Senin yeni verilerine göre katsayılar)
fon_ayarlari = {
    "TLY": {"ad": "Tera Portföy Birinci Serbest", "katsayi": 0.77},
    "DFI": {"ad": "Atlas Portföy Serbest Fon", "katsayi": 0.88},
    "PHE": {"ad": "Pusula Portföy Hisse Fon", "katsayi": 0.91},
    "PBR": {"ad": "Pusula Portföy Birinci Değişken", "katsayi": 0.31},
    "KHA": {"ad": "İstanbul Portföy Birinci Değişken", "katsayi": 2.91}
}

# Arayüz Elemanları
st.markdown("<h1 style='color:white; font-family: monospace; letter-spacing: 5px;'>YA 34 YA 39</h1>", unsafe_allow_html=True)

# BIST100 Kutusu (Görseldeki hata burada 'dtype' yazıyordu, şimdi sadece sayı görünecek)
st.markdown(f"""
    <div style="background-color: #1e293b; width: 140px; padding: 10px; border-radius: 10px; border-left: 5px solid #10b981; margin-bottom: 20px;">
        <p style="color: #94a3b8; font-size: 10px; margin: 0;">BIST100 ENDEKS</p>
        <p style="color: #4ade80; font-size: 18px; font-weight: bold; margin: 0;">%+{bist_degisim:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

cols = st.columns(5)

for i, (kod, info) in enumerate(fon_ayarlari.items()):
    # Hesaplama hatasını önlemek için sayısal garanti
    hesaplanan_getiri = float(bist_degisim) * info["katsayi"]
    
    with cols[i]:
        st.markdown(f"""
            <div class="tahmin-kart">
                <div class="fon-kodu">{kod}</div>
                <div class="fon-adi">{info['ad']}</div>
                <div class="tahmin-etiket">GÜN SONU TAHMİNİ</div>
                <div class="tahmin-deger">%+{hesaplanan_getiri:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
