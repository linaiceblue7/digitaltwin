"""
fetch_osm_stations.py
Скачивает реальные ЭЗС Москвы из OpenStreetMap (Overpass API).
Мощность определяется по признакам, если не указана в OSM.
"""
import requests
import pandas as pd

OVERPASS_URL = "https://overpass.private.coffee/api/interpreter"

QUERY = """
[out:json][timeout:60];
(
  node["amenity"="charging_station"](55.55,37.35,55.95,37.95);
  way["amenity"="charging_station"](55.55,37.35,55.95,37.95);
);
out center;
"""

# Садовое кольцо (центр Москвы) — приблизительные границы
SADOVOE = {
    "lat_min": 55.73,
    "lat_max": 55.78,
    "lon_min": 37.58,
    "lon_max": 37.66
}

# Признаки быстрых станций (в названии)
FAST_KEYWORDS = ["tesla", "supercharger", "быстр", "fast", "dc", "экспресс",
                 "тц", "трц", "трк", "mall", "авиапарк", "метрополис",
                 "европейский", "афимолл", "ашан", "лента", "метро"]


def is_fast_station(tags, lat, lon):
    """Определяет, быстрая ли станция, по названию и локации."""
    name = (tags.get("name", "") + " " + tags.get("operator", "")).lower()

    for kw in FAST_KEYWORDS:
        if kw in name:
            return True

    # В центре (внутри Садового) — обычно старые медленные
    in_center = (SADOVOE["lat_min"] <= lat <= SADOVOE["lat_max"] and
                 SADOVOE["lon_min"] <= lon <= SADOVOE["lon_max"])
    if in_center:
        return False

    # Всё остальное — 50 на 50
    return (hash(str(tags)) % 100) < 30


def fetch_stations():
    print("Загружаю ЭЗС Москвы из OpenStreetMap...")

    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "DigitalTwinMIIT/1.0 (student project)"
    }

    r = requests.post(
        OVERPASS_URL,
        data={"data": QUERY},
        headers=headers,
        timeout=180
    )

    print(f"Статус: {r.status_code}")
    r.raise_for_status()

    data = r.json()

    stations = []
    for el in data.get("elements", []):
        tags = el.get("tags", {})

        if el["type"] == "node":
            lat = el.get("lat")
            lon = el.get("lon")
        else:
            center = el.get("center", {})
            lat = center.get("lat")
            lon = center.get("lon")

        if lat is None or lon is None:
            continue

        # Попробуем вытащить мощность из OSM
        power = None
        for key in ["charging_station:output", "maxpower", "power"]:
            if key in tags:
                try:
                    val = str(tags[key]).replace("kW", "").replace("кВт", "").strip()
                    power = float(val)
                    break
                except (ValueError, TypeError):
                    pass

        if power and power > 1000:
            power = power / 1000

        # Если мощность не указана — определяем по признакам
        if not power or power <= 0:
            power = 150 if is_fast_station(tags, lat, lon) else 50
        else:
            # Округляем к типовым
            if power >= 300:
                power = 350
            elif power >= 100:
                power = 150
            elif power >= 40:
                power = 50
            else:
                power = 22

        stations.append({
            "id": el.get("id"),
            "latitude": lat,
            "longitude": lon,
            "power_kw": power,
            "connector_type": tags.get("socket:type2", tags.get("socket:chademo", "Unknown")),
            "address": tags.get("name", "")
        })

    return stations


if __name__ == "__main__":
    try:
        stations = fetch_stations()
        print(f"\nИтого: {len(stations)} ЭЗС Москвы")

        if stations:
            df = pd.DataFrame(stations)
            df.to_csv(r"C:\rosa_project\data\stations_real.csv", index=False, encoding="utf-8")
            print(f"Сохранено: C:\\rosa_project\\data\\stations_real.csv")

            print("\nРаспределение по мощности:")
            print(df['power_kw'].value_counts())

            print("\nПервые 10:")
            print(df.head(10))
        else:
            print("Ничего не найдено.")
    except Exception as e:
        print(f"Ошибка: {e}")