import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
import os

os.makedirs(r"C:\rosa_project\output", exist_ok=True)
os.makedirs(r"C:\rosa_project\models", exist_ok=True)

stations = pd.read_csv(r"C:\rosa_project\data\stations.csv")
traffic = pd.read_csv(r"C:\rosa_project\data\traffic.csv")

stations["dist_to_center"] = np.sqrt(
    (stations["latitude"] - 55.7558) ** 2 +
    (stations["longitude"] - 37.6173) ** 2
) * 111

traffic["lat_bin"] = (traffic["latitude"] / 0.01).round() * 0.01
traffic["lon_bin"] = (traffic["longitude"] / 0.01).round() * 0.01
agg = traffic.groupby(["lat_bin", "lon_bin"])["traffic"].mean().reset_index()

stations["lat_bin"] = (stations["latitude"] / 0.01).round() * 0.01
stations["lon_bin"] = (stations["longitude"] / 0.01).round() * 0.01
stations = stations.merge(agg, on=["lat_bin", "lon_bin"], how="left")
stations["traffic"] = stations["traffic"].fillna(stations["traffic"].median())

stations["demand_kwh"] = (
    stations["power_kw"] * 0.3 +
    stations["traffic"] / 1000 * 50
) * np.random.uniform(0.8, 1.2, len(stations))

features = ["latitude", "longitude", "power_kw", "dist_to_center", "traffic"]
X = stations[features]
y = stations["demand_kwh"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = XGBRegressor(n_estimators=300, max_depth=6, learning_rate=0.05)
model.fit(X_train, y_train)

pred = model.predict(X_test)
print(f"MAE: {mean_absolute_error(y_test, pred):.2f}")

joblib.dump(model, r"C:\rosa_project\models\demand_model.pkl")
stations["predicted_demand_kwh"] = model.predict(X)
stations.to_csv(r"C:\rosa_project\output\stations_with_demand.csv", index=False)
print("Модель обучена и сохранена")
