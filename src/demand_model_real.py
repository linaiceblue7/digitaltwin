"""
demand_model_real.py
Рассчитывает прогноз спроса для потенциальных локаций ЭЗС Москвы
на основе реальных признаков:
- тип локации (ТЦ, ТПУ, парковка)
- расстояние до центра
- конкуренция (есть ли рядом ЭЗС)
- плотность населения
"""
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

# Центр Москвы
CENTER_LAT = 55.7558
CENTER_LON = 37.6173


def haversine_m(lat1, lon1, lat2, lon2):
    """Расстояние в метрах."""
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


def distance_to_center_km(lat, lon):
    """Расстояние до центра Москвы в км."""
    return haversine_m(lat, lon, CENTER_LAT, CENTER_LON) / 1000


def nearest_station_distance_m(lat, lon, stations):
    """Минимальное расстояние до существующей ЭЗС в метрах."""
    if not stations:
        return 99999
    dists = [haversine_m(lat, lon, s[0], s[1]) for s in stations]
    return min(dists)


def calc_demand(row, real_stations):
    """Считает прогноз спроса (кВт·ч/час) для локации."""
    lat = row["latitude"]
    lon = row["longitude"]
    power = row["power_kw"]
    loc_type = row["type"]

    # 1. Коэффициент типа локации
    type_coef = {
        "mall": 1.4,
        "transport_hub": 1.3,
        "parking": 1.0
    }.get(loc_type, 1.0)

    # 2. Коэффициент центра (0.7 на окраине, 1.5 в центре)
    dist_center = distance_to_center_km(lat, lon)
    if dist_center < 3:
        center_coef = 1.5
    elif dist_center < 7:
        center_coef = 1.3
    elif dist_center < 15:
        center_coef = 1.1
    elif dist_center < 25:
        center_coef = 0.9
    else:
        center_coef = 0.7

    # 3. Коэффициент конкуренции
    dist_to_station = nearest_station_distance_m(lat, lon, real_stations)
    if dist_to_station < 300:
        comp_coef = 0.5
    elif dist_to_station < 700:
        comp_coef = 0.7
    elif dist_to_station < 1500:
        comp_coef = 0.85
    else:
        comp_coef = 1.0

    # 4. Коэффициент плотности населения (приблизительно по расстоянию до центра)
    if dist_center < 5:
        pop_coef = 1.2
    elif dist_center < 12:
        pop_coef = 1.1
    elif dist_center < 20:
        pop_coef = 1.0
    else:
        pop_coef = 0.85

    # 5. Базовый спрос: мощность × коэффициент загрузки
    base_demand = power * 0.15  # 15% базовой загрузки

    # 6. Итоговый спрос
    demand = base_demand * type_coef * center_coef * comp_coef * pop_coef

    return round(demand, 2)


def main():
    print("=== demand_model_real.py ===")
    print("Прогноз спроса для потенциальных локаций Москвы\n")

    # 1. Загружаем потенциальные локации
    df_potential = pd.read_csv(r"C:\rosa_project\data\potential_locations.csv")
    print(f"Потенциальных локаций: {len(df_potential)}")

    # 2. Загружаем существующие ЭЗС (для расчёта конкуренции)
    df_real = pd.read_csv(r"C:\rosa_project\data\stations_real.csv")
    print(f"Существующих ЭЗС: {len(df_real)}")

    real_stations = list(zip(df_real["latitude"], df_real["longitude"]))

    # 3. Считаем спрос для каждой потенциальной локации
        # 3. Пересчёт мощности по расположению и типу
    print("\nПересчитываю мощность по локациям...")
    def calc_power(row):
        dist_center = distance_to_center_km(row["latitude"], row["longitude"])
        loc_type = row["type"]
        if loc_type == "transport_hub":
            return 150
        if loc_type == "mall":
            if dist_center < 8:
                return 150
            else:
                return 50
        # parking
        if dist_center < 5:
            return 50
        return 50

    df_potential["power_kw"] = df_potential.apply(calc_power, axis=1)
    print("Распределение мощности:")
    print(df_potential["power_kw"].value_counts())

    # 4. Считаем спрос для каждой локации
        # 3. Пересчёт мощности по расположению и типу
    print("\nПересчитываю мощность по локациям...")

    def calc_power(row):
        dist_center = distance_to_center_km(row["latitude"], row["longitude"])
        loc_type = row["type"]
        if loc_type == "transport_hub":
            return 150
        if loc_type == "mall":
            if dist_center < 8:
                return 150
            else:
                return 50
        # parking
        return 50

    df_potential["power_kw"] = df_potential.apply(calc_power, axis=1)
    print("Распределение мощности:")
    print(df_potential["power_kw"].value_counts())

    # 4. Считаем спрос для каждой локации
       # 3. Пересчёт мощности по расположению и типу
    print("\nПересчитываю мощность по локациям...")

    def calc_power(row):
        dist_center = distance_to_center_km(row["latitude"], row["longitude"])
        loc_type = row["type"]
        if loc_type == "transport_hub":
            return 150
        if loc_type == "mall":
            if dist_center < 8:
                return 150
            else:
                return 50
        # parking
        return 50

    df_potential["power_kw"] = df_potential.apply(calc_power, axis=1)
    print("Распределение мощности:")
    print(df_potential["power_kw"].value_counts())

    # 4. Считаем спрос для каждой локации
    print("\nСчитаю прогноз спроса...")
    df_potential["predicted_demand_kwh"] = df_potential.apply(
        lambda r: calc_demand(r, real_stations), axis=1
    )

    # 4. Дополнительные признаки
    df_potential["dist_to_center_km"] = df_potential.apply(
        lambda r: round(distance_to_center_km(r["latitude"], r["longitude"]), 2), axis=1
    )

    df_potential["dist_to_station_m"] = df_potential.apply(
        lambda r: round(nearest_station_distance_m(r["latitude"], r["longitude"], real_stations)), axis=1
    )

    # 5. Сохраняем
    output_path = r"C:\rosa_project\output\potential_with_demand.csv"
    df_potential.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\nСохранено: {output_path}")

    # 6. Статистика
    print("\nСтатистика спроса (кВт·ч/час):")
    print(df_potential["predicted_demand_kwh"].describe())

    print("\nТоп-10 по спросу:")
    top10 = df_potential.nlargest(10, "predicted_demand_kwh")
    print(top10[["id", "latitude", "longitude", "type", "power_kw", "predicted_demand_kwh", "name"]])

    print("\n=== Готово ===")


if __name__ == "__main__":
    main()