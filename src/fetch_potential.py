"""
fetch_potential.py
Скачивает потенциальные локации для ЭЗС из OpenStreetMap:
- парковки ТЦ
- транспортно-пересадочные узлы
- торговые центры
- деловые центры

Убирает те, где уже есть ЭЗС в радиусе 500 м.
"""
import requests
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

OVERPASS_URL = "https://overpass.private.coffee/api/interpreter"

# Запрос: потенциальные локации Москвы
QUERY = """
[out:json][timeout:180];
(
  node["amenity"="parking"]["parking"="surface"](55.55,37.35,55.95,37.95);
  way["amenity"="parking"]["parking"="surface"](55.55,37.35,55.95,37.95);
  node["shop"="mall"](55.55,37.35,55.95,37.95);
  way["shop"="mall"](55.55,37.35,55.95,37.95);
  node["public_transport"="station"](55.55,37.35,55.95,37.95);
  way["public_transport"="station"](55.55,37.35,55.95,37.95);
  node["railway"="station"](55.55,37.35,55.95,37.95);
  way["railway"="station"](55.55,37.35,55.95,37.95);
);
out center;
"""


def haversine(lat1, lon1, lat2, lon2):
    """Расстояние в метрах между двумя точками."""
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


def fetch_potential():
    print("Загружаю потенциальные локации из OSM...")

    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "DigitalTwinMIIT/1.0 (student project)"
    }

    r = requests.post(OVERPASS_URL, data={"data": QUERY}, headers=headers, timeout=240)
    print(f"Статус: {r.status_code}")
    r.raise_for_status()

    data = r.json()

    locations = []
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

        # Определяем тип локации
        loc_type = "parking"
        if tags.get("shop") == "mall":
            loc_type = "mall"
        elif tags.get("public_transport") == "station" or tags.get("railway") == "station":
            loc_type = "transport_hub"

        # Потенциальная мощность: ТЦ и ТПУ — 150 кВт, парковки — 50 кВт
        power = 150 if loc_type in ["mall", "transport_hub"] else 50

        locations.append({
            "id": el.get("id"),
            "latitude": lat,
            "longitude": lon,
            "type": loc_type,
            "power_kw": power,
            "name": tags.get("name", "")
        })

    return locations


def filter_cannibalization(potential_df, real_df, radius_m=500):
    """Убирает точки, где уже есть ЭЗС в радиусе radius_m."""
    print(f"Фильтрую каннибализацию (радиус {radius_m} м)...")

    real_coords = list(zip(real_df["latitude"], real_df["longitude"]))

    keep = []
    for _, p in potential_df.iterrows():
        too_close = False
        for rlat, rlon in real_coords:
            if haversine(p["latitude"], p["longitude"], rlat, rlon) < radius_m:
                too_close = True
                break
        if not too_close:
            keep.append(p)

    return pd.DataFrame(keep)


if __name__ == "__main__":
    try:
        # 1. Загружаем потенциальные локации
        potential = fetch_potential()
        print(f"\nВсего потенциальных локаций: {len(potential)}")

        if not potential:
            print("Ничего не найдено.")
            exit()

        df_potential = pd.DataFrame(potential)

        # 2. Загружаем реальные ЭЗС
        df_real = pd.read_csv(r"C:\rosa_project\data\stations_real.csv")
        print(f"Загружено реальных ЭЗС: {len(df_real)}")

        # 3. Фильтруем каннибализацию
        df_filtered = filter_cannibalization(df_potential, df_real, radius_m=500)
        print(f"После фильтрации: {len(df_filtered)}")

        # 4. Сохраняем
        df_filtered.to_csv(r"C:\rosa_project\data\potential_locations.csv", index=False, encoding="utf-8")
        print(f"\nСохранено: C:\\rosa_project\\data\\potential_locations.csv")

        # 5. Статистика
        print("\nПо типам локаций:")
        print(df_filtered["type"].value_counts())

        print("\nПервые 10:")
        print(df_filtered.head(10))

    except Exception as e:
        print(f"Ошибка: {e}")
        