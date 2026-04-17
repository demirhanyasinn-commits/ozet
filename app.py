import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time
from zoneinfo import ZoneInfo

# -------------------------------------------------
# 🚀 OTOMATİK VERİ ÇEKME VE EŞLEŞTİRME SİSTEMİ
# -------------------------------------------------

@st.cache_data(ttl=86400)
def get_dynamic_weights(fon_kodu):
    """
    Bu fonksiyon normalde KAP veya veri servislerinden fonun son detaylı 
    portföy dağılımını çekmelidir. Şimdilik TEFAS'tan gelen ana grupları 
    sektörel tahminlerle birleştiriyoruz.
    """
    # TEFAS'tan gelen ana dağılımı al
    v_gruplari = tefas_portfoy(fon_kodu)
    
    # Fonun geçmiş performans karakteristiği (Banka/Sanayi/Teknoloji duyarlılığı)
    # Bu kısım manuel girilmek yerine fonun son 1 ayındaki korelasyonundan da alınabilir.
    karakter = {
        "TLY": {"bank": 0.45, "sanayi": 0.45, "tekno": 0.10},
        "KHA": {"bank": 0.50, "sanayi": 0.40, "tekno": 0.10}, # KHA'yı banka ağırlıklı güncelledik
        "DFI": {"bank": 0.50, "sanayi": 0.40, "tekno": 0.10},
        "PHE": {"bank": 0.10, "sanayi": 0.10, "tekno": 0.80},
        "PBR": {"bank": 0.60, "sanayi": 0.30, "tekno": 0.10}
    }
    
    f_karakter = karakter.get(fon_kodu, {"bank": 0.33, "sanayi": 0.33, "tekno": 0.34})
    
    # TEFAS'tan gelen 'hisse' oranını, fonun karakterindeki sektörlere dağıtıyoruz
    return {
        "hisse_banka": v_gruplari["hisse"] * f_karakter["bank"],
        "hisse_sanayi": v_gruplari["hisse"] * f_karakter["sanayi"],
        "hisse_tekno": v_gruplari["hisse"] * f_karakter["tekno"],
        "doviz": v_gruplari["doviz"],
        "altin": v_gruplari["altin"],
        "faiz": v_gruplari["faiz"]
    }

def yeni_tahmin_motoru(fon, piyasa):
    # 1. TEFAS Verisini ve Sektörel Dağılımı Dinamik Al
    d = get_dynamic_weights(fon)
    
    # 2. Her varlığın piyasa getirisi ile çarpımı
    # Hisse tarafı (Sektör endeksleri ile)
    getiri_hisse = (
        d["hisse_banka"] * piyasa["bank"] +
        d["hisse_sanayi"] * piyasa["sanayi"] +
        d["hisse_tekno"] * piyasa["teknoloji"]
    )
    
    # Diğer varlıklar
    getiri_doviz = d["doviz"] * piyasa["usd"]
    getiri_altin = d["altin"] * piyasa["altin"]
    getiri_faiz = d["faiz"] * 0.018 # Günlük repo tahmini
    
    # 3. Toplam (Beta çarpanı yerine her varlığın kendi ağırlığıyla hesaplama)
    # Fonlar genellikle endeksten biraz daha agresif olduğu için %5-10 'alfa' eklenebilir
    toplam_tahmin = (getiri_hisse + getiri_doviz + getiri_altin + getiri_faiz) * 1.05
    
    # 4. Netleştirme (Ücret kesintisi)
    net_sonuc = toplam_tahmin - 0.007
    
    return round(net_sonuc, 2)

# -------------------------------------------------
# 💡 NEDEN HALA BAZI VERİLERİ MANUEL GÖRÜYORSUN?
# -------------------------------------------------
# TEFAS'ın sunduğu "BindPortfolio" API'si sadece varlık sınıfını söyler: 
# "Hisse Senedi: %90" der ama "Hangi hisse?" demez. 
# Eğer profesyonel bir veri terminali (Matriks, IDEAL vb.) kullanmıyorsak, 
# fonun karakterini (Banka mı Sanayi mi olduğunu) bir defa sisteme tanıtmak zorundayız.
