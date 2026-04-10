@st.cache_data(ttl=300)
def fetch_tefas(fon_kodu):
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

    except Exception as e:
        return pd.DataFrame()
if df.empty:
    st.warning(f"{fon} verisi alınamadı")
     current = df.iloc[-1]["Fiyat"]
        prev = df.iloc[-2]["Fiyat"]
if not df.empty:
    current = df.iloc[-1]["Fiyat"]
    prev = df.iloc[-2]["Fiyat"]
else:
    st.warning(f"{fon} verisi alınamadı")
