import streamlit as st
import pandas as pd
import yfinance as yf
from tefas import Crawler
from datetime import datetime, timedelta
import pytz

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="Fon Gün Sonu Simülatörü", layout="wide")

def get_istanbul_now():
    return datetime.now(pytz.timezone('Europe/Istanbul'))

# 2. Canlı Piyasa Verilerini Çeken Fonksiyon
@st.cache_data(ttl=60) # Her dakika tazelenir
def fetch_live_market():
    try:
        # XU100 (Borsa), USDTRY (Dolar), GC=F (Altın/Döviz etkisi)
        tickers = {"BIST100": "XU100.IS", "USDTRY": "USDTRY=X", "ONS": "GC=F"}
        market_data = {}
        for name, ticker in tickers.items():
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            if len(hist) >= 2:
                change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                market_data[name] = change
            else:
                market_data[name] = 0.0
        return market_data
    except:
        return {"BIST100": 0.0, "USDTRY": 0.0, "ONS": 0.0}

# 3. TEFAS'tan Resmi Dünkü Verileri Çeken Fonksiyon
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
    st.title("🎯 Anlık Gün Sonu Fiyat Simülatörü")
    st.markdown(f"**İstanbul Saati:** {get_istanbul_now().strftime('%H:%M:%S')} | *Piyasa verileri 60 saniyede bir güncellenir.*")
    
    # --- PİYASA DURUMU ---
    market = fetch_live_market()
    m1, m2, m3 = st.columns(3)
    m1.metric("BIST 100", f"%{market['BIST100']:.2f}")
    m2.metric("USD/TRY", f"%{market['USDTRY']:.2f}")
    m3.metric("Ons Altın", f"%{market['ONS']:.2f}")

    # --- FON PORTFÖY YAPILARI (Hassas Tahmin İçin Burayı Düzenle) ---
    # Not: Bu oranlar fonun KAP bildirimindeki ağırlıklardır.
    portfoy_yapisi = {
        "TLY": {"Hisse": 0.88, "Dolar": 0.07, "Sabit": 0.05},
        "DFI": {"Hisse": 0.15, "Dolar": 0.75, "Sabit": 0.10},
        "PHE": {"Hisse": 0.82, "Dolar": 0.13, "Sabit": 0.05}
    }

    my_funds = ["TLY", "DFI", "PHE"]
    df = fetch_official_tefas(my_funds)

    if df is not None and not df.empty:
        st.divider()
        st.subheader("🚀 Akşam Beklenen (Simüle Edilen) Getiriler")
        
        # Sütun isimlerini güvenli alalım
        cols = df.columns.tolist()
        p_col = next((c for c in ['price', 'birim_fiyat'] if c in cols), None)
        
        f_cols = st.columns(3)
        for i, code in enumerate(my_funds):
            row = df[df['code'] == code].iloc[0]
            dagilim = portfoy_yapisi[code]
            
            # --- HESAPLAMA MOTORU ---
            # Fonun o günkü tahmini yüzdesi: (Hisse Payı * Borsa Değişimi) + (Dolar Payı * Kur Değişimi)
            bugunku_tahmini_degisim = (
                (dagilim["Hisse"] * market["BIST100"]) + 
                (dagilim["Dolar"] * market["USDTRY"]) +
                (dagilim.get("Sabit", 0) * 0.12) # Sabit getirili menkul kıymet varsayımı
            )
            
            resmi_fiyat = float(row[p_col])
            tahmini_fiyat = resmi_fiyat * (1 + bugunku_tahmini_degisim / 100)

            with f_cols[i]:
                st.markdown(f"### {code}")
                st.caption("Resmi Kapanış (Dün)")
                st.code(f"{resmi_fiyat:.4f} TL")
                
                st.caption("Beklenen Akşam Fiyatı")
                st.metric(
                    label="Tahmini Değişim", 
                    value=f"{tahmini_fiyat:.4f} TL", 
                    delta=f"%{bugunku_tahmini_degisim:.2f}"
                )
        
        st.divider()
        with st.expander("📌 Bu değerler nasıl hesaplanıyor?"):
            st.write("""
            Bu uygulama, fonların en son açıklanan varlık dağılımlarını kullanır. 
            Örneğin bir fonun %90'ı hisse senediyse, BIST100'deki anlık yükselişin %90'ını fona yansıtır. 
            **Unutmayın:** Bu bir simülasyondur, fonun içindeki hisseler endeksten farklı hareket edebilir.
            """)
    else:
        st.error("TEFAS verilerine erişilemedi.")

if __name__ == "__main__":
    main()
