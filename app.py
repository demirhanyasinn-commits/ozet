import streamlit as st
import pandas as pd
import yfinance as yf
from tefas import Crawler
from datetime import datetime, timedelta
import pytz

# ... (CSS ve fetch fonksiyonları aynı kalacak, sadece main içindeki hesaplama değişiyor) ...

def main():
    # Piyasadan canlı verileri al
    market = fetch_market_data()
    bist_pct = market.get("BIST100", {"pct":0})["pct"]
    usd_pct = market.get("USDTRY", {"pct":0})["pct"]

    # FON PORTFÖY YAPISI - image_26de41.jpg tablosuna göre kalibre edildi
    # Hisse paylarını %90'dan %82-85 bandına çektik çünkü fonun bir kısmı nakit/repo'da durur.
    portfoy_yapisi = {
        "TLY": {"Hisse": 0.82, "Dolar": 0.05, "Sabit": 0.13, "desc": "Tera Portföy Birinci Serbest Fon"},
        "DFI": {"Hisse": 0.12, "Dolar": 0.78, "Sabit": 0.10, "desc": "Atlas Portföy Serbest Fon"},
        "PHE": {"Hisse": 0.85, "Dolar": 0.05, "Sabit": 0.10, "desc": "Pusula Portföy Hisse Fonu"},
        "PBR": {"Hisse": 0.35, "Dolar": 0.45, "Sabit": 0.20, "desc": "Pusula Portföy Birinci Değişken"}
    }

    df = fetch_tefas_data(list(portfoy_yapisi.keys()))
    
    if df is not None:
        grid = st.columns(len(portfoy_yapisi))
        
        for i, (code, config) in enumerate(portfoy_yapisi.items()):
            fund_row = df[df['code'] == code]
            if not fund_row.empty:
                row = fund_row.iloc[0]
                
                # --- YENİ HESAPLAMA MODELİ (KALİBRE EDİLMİŞ) ---
                # Profesyonel tabloda görünen "Günlük % Getiri" ile eşleşmesi için:
                # 1. Hisse etkisi: Endeks değişimini fonun hisse ağırlığıyla çarpıyoruz.
                # 2. Sabit etki: Fonun içindeki nakit/repo payı için günlük sabit faiz tahmini ekliyoruz.
                
                gunluk_sabit_getiri = 0.0012 # Yaklaşık günlük %0.12 mevduat/repo karşılığı
                
                tahmini_yuzde = (
                    (config["Hisse"] * bist_pct) + 
                    (config["Dolar"] * usd_pct) + 
                    (config["Sabit"] * gunluk_sabit_getiri)
                )

                # Sapmayı engellemek için %0.25'lik aşırılığı törpüleyen katsayı (Beta Düzenlemesi)
                # Fonlar genellikle endeksin tamamını kopyalamaz, biraz geriden takip eder.
                tahmini_yuzde = tahmini_yuzde * 0.98 

                with grid[i]:
                    st.markdown(f"""
                        <div class="fund-card">
                            <div class="fund-title">{code}</div>
                            <div class="est-label">KALİBRE EDİLMİŞ TAHMİN</div>
                            <div class="est-value">%{tahmini_yuzde:+.2f}</div>
                        </div>
                    """, unsafe_allow_html=True)
