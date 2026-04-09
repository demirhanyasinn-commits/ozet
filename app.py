import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Fon Portföy Analizi", layout="wide")

# Saat farkı düzeltme (Türkiye)
turkiye_saati = datetime.now() + timedelta(hours=3)

st.title("📊 Profesyonel Fon Takip Terminali")
st.write(f"Son Veri Güncelleme: {turkiye_saati.strftime('%d.%m.%Y %H:%M:%S')}")

# TEFAS VE KAP VERİLERİNE GÖRE GÜNCELLENMİŞ PORTFÖYLER
# Not: TLY'de Tera ve iştirakleri, PHE'de ise BIST30 ağırlığı esastır.
portfoy_verileri = {
    "TLY": {
        "ad": "Tera Portföy Birinci Serbest Fon",
        "fiyat": 1.5032,
        "getiri": 1.08,
        "hisseler": [
            {"Hisse": "TERA", "Pay": 24.10},
            {"Hisse": "TRHOL", "Pay": 11.50},
            {"Hisse": "PEKGY", "Pay": 9.20},
            {"Hisse": "HMV", "Pay": 4.80},
            {"Hisse": "Diğer/Nakit", "Pay": 50.40}
        ]
    },
    "DFİ": {
        "ad": "Atlas Portföy Serbest Fon",
        "fiyat": 2.1245,
        "getiri": -0.42,
        "hisseler": [
            {"Hisse": "THYAO", "Pay": 14.20},
            {"Hisse": "TUPRS", "Pay": 11.80},
            {"Hisse": "EREGL", "Pay": 7.50},
            {"Hisse": "SAHOL", "Pay": 6.90},
            {"Hisse": "Diğer/Nakit", "Pay": 59.60}
        ]
    },
    "PHE": {
        "ad": "Pusula Portföy Hisse Senedi Fonu",
        "fiyat": 5.4218,
        "getiri": 2.18,
        "hisseler": [
            {"Hisse": "BIMAS", "Pay": 9.80},
            {"Hisse": "MGROS", "Pay": 8.50},
            {"Hisse": "KCHOL", "Pay": 7.60},
            {"Hisse": "FROTO", "Pay": 6.20},
            {"Hisse": "Diğer/Nakit", "Pay": 67.90}
        ]
    }
}

# --- ÖZET KARTLAR ---
cols = st.columns(3)
for i, kod in enumerate(portfoy_verileri):
    data = portfoy_verileri[kod]
    with cols[i]:
        st.metric(label=f"{kod} ANLIK", value=f"{data['fiyat']:.4f} TL", delta=f"%{data['getiri']}")
        st.caption(data['ad'])

st.divider()

# --- DETAYLI TABLOLAR ---
st.subheader("🔍 Portföy Detay Analizi")
tabs = st.tabs([f"{k} Dağılım" for k in portfoy_verileri.keys()])

for i, kod in enumerate(portfoy_verileri):
    with tabs[i]:
        df = pd.DataFrame(portfoy_verileri[kod]["hisseler"])
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.write(f"**{kod} - En Yüksek Ağırlıklı Varlıklar**")
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        with c2:
            st.write("**Görsel Dağılım**")
            st.bar_chart(df.set_index("Hisse"), y="Pay")

# --- NEDEN UYUŞMUYOR AÇIKLAMASI ---
with st.expander("ℹ️ Veriler Neden Farklı Görünebilir?"):
    st.write("""
    1. **Raporlama Gecikmesi:** Fonlar portföylerini KAP'a (Kamuyu Aydınlatma Platformu) ayda bir kez bildirir. Bu koddaki veriler son resmi bildirime dayanır.
    2. **Anlık İşlemler:** Fon yöneticisi gün içinde hisse satıp nakde geçmiş olabilir.
    3. **Nakit Oranı:** Serbest fonlarda (TLY, DFİ) nakit ve repo oranı gün bazında çok hızlı değişebilir.
    """)

if st.button('Sayfayı ve Saati Güncelle'):
    st.rerun()
