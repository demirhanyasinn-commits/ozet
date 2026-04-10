import streamlit as st
@st.cache_data(ttl=300)
def fetch_tefas(fon_kodu):



import streamlit as st
import pandas as pd

uploaded_file = st.file_uploader("Choose a file") # Line 45 aligned with imports
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)






    
    url = "https://www.tefas.gov.tr/api/DB/BindHistoryInfo"

    payload = {
        "fontip": "YAT",
        "fonkod": fon_kodu,
        "bastarih": "01.01.2024",
        "bittarih": pd.Timestamp.today().strftime("%d.%m.%Y")
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.tefas.gov.tr/"
    }

    try:
        session = requests.Session()

        # 🔥 Önce siteyi ziyaret et (cookie al)
        session.get("https://www.tefas.gov.tr/")

        r = session.post(url, data=payload, headers=headers, timeout=10)

        # JSON kontrol
        if "application/json" not in r.headers.get("Content-Type", ""):
            return pd.DataFrame()

        json_data = r.json()

        data = json_data.get("data", [])

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        df["Tarih"] = pd.to_datetime(df["Tarih"], format="%d.%m.%Y")
        df["Fiyat"] = df["Fiyat"].astype(float)

        return df.sort_values("Tarih")

  uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) # Or read_excel
    
    if not df.empty:
        st.write("Data loaded successfully!")
else:
    st.info("Please upload a file to proceed.")
