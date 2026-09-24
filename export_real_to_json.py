"""
export_real_to_json.py
Экспортирует 20 реальных локаций + 326 существующих ЭЗС в JSON для сайта.
Исправляет NaN в именах.
"""
import pandas as pd
import json

# ============ 1. Экспорт 20 отобранных локаций ============
df_result = pd.read_csv(r"C:\rosa_project\output\result_real.csv")

keep = ["priority", "latitude", "longitude", "power_kw",
        "predicted_demand_kwh", "npv", "irr", "payback_years",
        "capex", "annual_revenue", "type", "name", "utilization"]
df_result = df_result[[c for c in keep if c in df_result.columns]].copy()

# Чистим name — заменяем NaN на пустую строку
if "name" in df_result.columns:
    df_result["name"] = df_result["name"].fillna("").astype(str)

# Чистим type — заменяем NaN
if "type" in df_result.columns:
    df_result["type"] = df_result["type"].fillna("parking").astype(str)

# Округляем числовые поля
df_result["npv"] = df_result["npv"].round(0)
df_result["irr"] = df_result["irr"].round(3)
df_result["capex"] = df_result["capex"].round(0)
df_result["annual_revenue"] = df_result["annual_revenue"].round(0)
df_result["predicted_demand_kwh"] = df_result["predicted_demand_kwh"].round(2)
df_result["payback_years"] = df_result["payback_years"].round(1)
df_result["utilization"] = df_result["utilization"].round(3)
df_result["latitude"] = df_result["latitude"].round(6)
df_result["longitude"] = df_result["longitude"].round(6)

# Заменяем оставшиеся NaN на 0
df_result = df_result.fillna(0)

records = df_result.to_dict(orient="records")

with open(r"C:\rosa_project\web\locations.json", "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print(f"Экспортировано {len(records)} локаций в locations.json")

# ============ 2. Экспорт существующих ЭЗС ============
df_real = pd.read_csv(r"C:\rosa_project\data\stations_real.csv")
df_real["name"] = df_real["address"].fillna("").astype(str).replace("nan", "")
df_real = df_real[["latitude", "longitude", "power_kw", "name"]].copy()
df_real = df_real.dropna()
df_real = df_real[["latitude", "longitude", "power_kw", "name"]].copy()

df_real["latitude"] = df_real["latitude"].round(6)
df_real["longitude"] = df_real["longitude"].round(6)
df_real["power_kw"] = df_real["power_kw"].fillna(50).astype(int)
df_real = df_real.fillna("")

existing = df_real.to_dict(orient="records")

with open(r"C:\rosa_project\web\existing_stations.json", "w", encoding="utf-8") as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

print(f"Экспортировано {len(existing)} существующих ЭЗС в existing_stations.json")
print("Готово.")