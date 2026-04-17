def tefas_portfoy_cek(fon_kodu):

    url = "https://www.tefas.gov.tr/api/DB/BindPortfolio"

    payload = {
        "fontur": "",
        "fonkod": fon_kodu
    }

    headers = {
        "Content-Type": "application/json"
    }

    res = requests.post(url, json=payload, headers=headers).json()

    hisse = 0
    doviz = 0
    altin = 0
    faiz = 0

    for item in res["data"]:
        tip = item["TUR"]
        oran = float(item["ORAN"])

        if "Hisse" in tip:
            hisse += oran
        elif "Döviz" in tip:
            doviz += oran
        elif "Altın" in tip:
            altin += oran
        else:
            faiz += oran

    toplam = hisse + doviz + altin + faiz

    return {
        "hisse": hisse / toplam,
        "doviz": doviz / toplam,
        "altin": altin / toplam,
        "faiz": faiz / toplam
    }
