"""
fetch_real_stations.py
Скачивает реальные ЭЗС Москвы из OpenChargeMap.
"""
import requests
import pandas as pd
import time

# Границы Москвы (примерный прямоугольник)
BOUNDS = {
    "lat_min": 55.55,
    "lat_max": 55.95,
    "lon_min": 37.35,
    "lon_max": 37.95
}

def fetch_stations():
    url = "https://api.openchargemap.io/v3/poi/"
    all_stations = []
    max_results = 500
    offset = 0

    print("Начинаю загрузку ЭЗС Москвы из OpenChargeMap...")

    while True:
        params = {
            "output": "json",
            "countrycode": "RU",
            "latitude": 55.7558,
            "longitude": 37.6173,
            "distance": 40,
            "distanceunit": "KM",
            "maxresults": max_results,
            "compact": "true",
            "verbose": "false"
        }

        try:
            r = requests.get(url, params=params, timeout=30)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"Ошибка на offset={offset}: {e}")
            break

        if not data:
            break

        for item in data:
            addr = item.get("AddressInfo", {})
            lat = addr.get("Latitude")
            lon = addr.get("Longitude")
            if lat is None or lon is None:
                continue
            if not (BOUNDS["lat_min"] <= lat <= BOUNDS["lat_max"]):
                continue
            if not (BOUNDS["lon_min"] <= lon <= BOUNDS["lon_max"]):
                continue

            conns = item.get("Connections", [])
            power = 22
            if conns:
                powers = [c.get("PowerKW") for c in conns if c.get("PowerKW")]
                if powers:
                    power = max(powers)

            all_stations.append({
                "id": item.get("ID"),
                "latitude": lat,
                "longitude": lon,
                "power_kw": power,
                "connector_type": (conns[0].get("ConnectionType", {}) or {}).get("Title", "Unknown") if conns else "Unknown",
                "address": addr.get("Title", "")
            })

        print(f"Загружено {len(all_stations)} точек (offset={offset})")

        if len(data) < max_results:
            break

        offset += max_results
        time.sleep(1)
        if offset > 5000:
            break

    return all_stations


if __name__ == "__main__":
    stations = fetch_stations()
    print(f"\nИтого: {len(stations)} ЭЗС Москвы")

    if stations:
        df = pd.DataFrame(stations)
        df.to_csv(r"C:\rosa_project\data\stations_real.csv", index=False, encoding="utf-8")
        print(f"Сохранено: C:\\rosa_project\\data\\stations_real.csv")
        print(df.head(10))
    else:
        print("Ничего не загружено. Проверь интернет.")