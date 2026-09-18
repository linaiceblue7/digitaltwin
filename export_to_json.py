import pandas as pd
import json
import os

df = pd.read_csv(r"C:\rosa_project\output\result.csv")

keep = ["priority", "latitude", "longitude", "power_kw",
        "predicted_demand_kwh", "npv", "irr", "payback_years", "capex", "annual_revenue"]
df = df[[c for c in keep if c in df.columns]].copy()

df["npv"] = df["npv"].round(0)
df["irr"] = df["irr"].round(3)
df["capex"] = df["capex"].round(0)
df["annual_revenue"] = df["annual_revenue"].round(0)
df["predicted_demand_kwh"] = df["predicted_demand_kwh"].round(1)
df["payback_years"] = df["payback_years"].round(1)

records = df.to_dict(orient="records")

os.makedirs(r"C:\rosa_project\web", exist_ok=True)
with open(r"C:\rosa_project\web\data.json", "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print(f"Экспортировано {len(records)} записей в C:\\rosa_project\\web\\data.json")
