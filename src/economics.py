import pandas as pd
import numpy as np

CAPEX_PER_KW = 30_000
OPEX_PER_YEAR = 500_000
TARIFF = 15
DISCOUNT_RATE = 0.12
YEARS = 10

def npv(cf, rate):
    return sum(c / (1 + rate) ** i for i, c in enumerate(cf))

def irr(cf):
    low, high = 0.0, 1.0
    for _ in range(100):
        mid = (low + high) / 2
        if npv(cf, mid) > 0:
            low = mid
        else:
            high = mid
    return (low + high) / 2

def payback(cf):
    cum = 0
    for i, c in enumerate(cf):
        cum += c
        if cum >= 0:
            return i
    return YEARS

def evaluate(row):
    power = row["power_kw"]
    daily_kwh = row["predicted_demand_kwh"] * 24 * 0.5
    capex = power * CAPEX_PER_KW
    annual_revenue = daily_kwh * 365 * TARIFF
    annual_cf = annual_revenue - OPEX_PER_YEAR
    cf = [-capex] + [annual_cf] * YEARS
    return pd.Series({
        "capex": capex,
        "annual_revenue": annual_revenue,
        "npv": npv(cf, DISCOUNT_RATE),
        "irr": irr(cf),
        "payback_years": payback(cf),
    })

print("Скрипт economics.py запущен")

df = pd.read_csv(r"C:\rosa_project\output\optimized_locations.csv")
print(f"Загружено локаций: {len(df)}")

econ = df.apply(evaluate, axis=1)
result = pd.concat([df, econ], axis=1)
result.to_csv(r"C:\rosa_project\output\result.csv", index=False)

print("Экономика посчитана")
print(result[["priority", "latitude", "longitude", "npv", "irr", "payback_years"]].head(10))
print("Готово")
CAPEX_PER_KW = 45_000     # было 30_000 — реалистичнее для РФ
OPEX_PER_YEAR = 900_000   # было 500_000
TARIFF = 18               # было 15
