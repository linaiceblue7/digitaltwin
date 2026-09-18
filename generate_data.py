import pandas as pd
import numpy as np
import os

np.random.seed(42)
os.makedirs(r"C:\rosa_project\data", exist_ok=True)

n = 200
stations = pd.DataFrame({
    "id": range(1, n + 1),
    "latitude": np.random.uniform(55.60, 55.90, n),
    "longitude": np.random.uniform(37.40, 37.90, n),
    "power_kw": np.random.choice([50, 150, 350], n),
    "connector_type": np.random.choice(["CCS", "GBT", "CHAdeMO"], n),
})
stations.to_csv(r"C:\rosa_project\data\stations.csv", index=False)

grid = pd.DataFrame({
    "id": range(1, 51),
    "latitude": np.random.uniform(55.60, 55.90, 50),
    "longitude": np.random.uniform(37.40, 37.90, 50),
    "capacity_kw": np.random.choice([500, 800, 1000, 1500], 50),
    "load_kw": np.random.uniform(300, 900, 50),
})
grid.to_csv(r"C:\rosa_project\data\grid.csv", index=False)

rows = []
for _ in range(2000):
    rows.append({
        "latitude": np.random.uniform(55.60, 55.90),
        "longitude": np.random.uniform(37.40, 37.90),
        "hour": np.random.randint(0, 24),
        "traffic": np.random.uniform(50, 1500),
    })
pd.DataFrame(rows).to_csv(r"C:\rosa_project\data\traffic.csv", index=False)

print("Данные созданы в C:\\rosa_project\\data")
