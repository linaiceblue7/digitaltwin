"""
optimize_real.py
Отбирает 20 лучших локаций: 10 быстрых (150 кВт) + 10 медленных (50 кВт).
Такой подход отражает реальную стратегию: быстрые в центре, медленные на периферии.
"""
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

TOP_FAST = 10
TOP_SLOW = 10
MIN_DISTANCE_M = 1500


def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


def calc_score(df):
    df["demand_score"] = df["predicted_demand_kwh"] / df["predicted_demand_kwh"].max()
    max_dist = df["dist_to_station_m"].max()
    df["competition_score"] = df["dist_to_station_m"] / max_dist
    max_center = df["dist_to_center_km"].max()
    df["center_score"] = 1 - (df["dist_to_center_km"] / max_center)
    type_score_map = {"mall": 1.0, "transport_hub": 0.9, "parking": 0.6}
    df["type_score"] = df["type"].map(type_score_map).fillna(0.5)
    df["score"] = (
        0.50 * df["demand_score"] +
        0.25 * df["competition_score"] +
        0.15 * df["center_score"] +
        0.10 * df["type_score"]
    )
    return df


def greedy_select(df_sorted, n, min_distance_m, exclude_coords=None):
    """Жадный отбор N локаций с ограничением по расстоянию."""
    selected = []
    if exclude_coords is None:
        exclude_coords = []
    for _, row in df_sorted.iterrows():
        too_close = False
        for s in selected:
            if haversine_m(row["latitude"], row["longitude"], s["latitude"], s["longitude"]) < min_distance_m:
                too_close = True
                break
        if not too_close:
            for ex in exclude_coords:
                if haversine_m(row["latitude"], row["longitude"], ex[0], ex[1]) < min_distance_m:
                    too_close = True
                    break
        if not too_close:
            selected.append(row)
        if len(selected) >= n:
            break
    return selected


def main():
    print("=== optimize_real.py ===\n")

    df = pd.read_csv(r"C:\rosa_project\output\potential_with_demand.csv")
    print(f"Загружено локаций: {len(df)}")

    df = calc_score(df)

    # Группа 1: только 150 кВт
    df_fast = df[df["power_kw"] >= 150].sort_values("score", ascending=False).reset_index(drop=True)
    print(f"Быстрых (150 кВт): {len(df_fast)}")

    # Группа 2: только 50 кВт
    df_slow = df[df["power_kw"] < 150].sort_values("score", ascending=False).reset_index(drop=True)
    print(f"Медленных (50 кВт): {len(df_slow)}")

    # Отбираем 10 быстрых
    print(f"\nОтбираю топ-{TOP_FAST} быстрых...")
    selected_fast = greedy_select(df_fast, TOP_FAST, MIN_DISTANCE_M)
    fast_coords = [(s["latitude"], s["longitude"]) for s in selected_fast]

    # Отбираем 10 медленных (не ближе 1.5 км к быстрым)
    print(f"Отбираю топ-{TOP_SLOW} медленных (не ближе 1.5 км к быстрым)...")
    selected_slow = greedy_select(df_slow, TOP_SLOW, MIN_DISTANCE_M, exclude_coords=fast_coords)

    # Объединяем и сортируем по скору
    all_selected = selected_fast + selected_slow
    result = pd.DataFrame(all_selected).sort_values("score", ascending=False).reset_index(drop=True)
    result["priority"] = range(1, len(result) + 1)

    output_path = r"C:\rosa_project\output\optimized_locations_real.csv"
    result.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\nСохранено: {output_path}")
    print(f"Отобрано: {len(result)} локаций")

    print("\n=== Топ-20 ===")
    cols = ["priority", "id", "latitude", "longitude", "type", "power_kw", "predicted_demand_kwh", "name", "score"]
    print(result[cols].to_string(index=False))

    print("\n=== Статистика ===")
    print(f"Средний спрос: {result['predicted_demand_kwh'].mean():.2f} кВт·ч/час")
    print(f"Средняя мощность: {result['power_kw'].mean():.0f} кВт")
    print(f"Среднее расстояние до центра: {result['dist_to_center_km'].mean():.2f} км")
    print(f"По мощности:")
    print(result["power_kw"].value_counts())
    print(f"По типам:")
    print(result["type"].value_counts())

    print("\n=== Готово ===")


if __name__ == "__main__":
    main()