import pandas as pd
import numpy as np
from scipy.spatial import cKDTree

print("Скрипт optimize.py запущен")

stations = pd.read_csv(r"C:\rosa_project\output\stations_with_demand.csv")
grid = pd.read_csv(r"C:\rosa_project\data\grid.csv")

print(f"Загружено станций: {len(stations)}")
print(f"Загружено подстанций: {len(grid)}")

stations["demand_score"] = stations["predicted_demand_kwh"] / stations["predicted_demand_kwh"].max()

tree = cKDTree(grid[["latitude", "longitude"]].values)
dist, idx = tree.query(stations[["latitude", "longitude"]].values)
stations["dist_to_grid_km"] = dist * 111
stations["grid_capacity_kw"] = grid.iloc[idx]["capacity_kw"].values
stations["grid_load_kw"] = grid.iloc[idx]["load_kw"].values
stations["grid_free_kw"] = stations["grid_capacity_kw"] - stations["grid_load_kw"]
stations["grid_score"] = stations["grid_free_kw"] / stations["grid_capacity_kw"]

stations["score"] = (
    0.5 * stations["demand_score"] +
    0.3 * stations["grid_score"] -
    0.2 * (stations["dist_to_grid_km"] / stations["dist_to_grid_km"].max())
)

result = stations.sort_values("score", ascending=False).head(20).copy()
result["priority"] = range(1, len(result) + 1)
result.to_csv(r"C:\rosa_project\output\optimized_locations.csv", index=False)

print(f"Топ-{len(result)} локаций сохранён")
print("Готово")