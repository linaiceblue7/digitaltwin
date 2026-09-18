import pandas as pd
import numpy as np

# Реалистичные параметры экономики (на основе рынка РФ 2026)
CAPEX_PER_KW = 30_000       # рублей за кВт установленной мощности
OPEX_PER_YEAR = 700_000     # рублей в год на станцию (обслуживание + электричество)
TARIFF = 18                 # рублей за кВт·ч для пользователя
UTILIZATION_RATE = 0.10     # 10% — реальная средняя загрузка станции
DISCOUNT_RATE = 0.12        # ставка дисконтирования
YEARS = 10

def npv(cf, rate):
    return sum(c / (1 + rate) ** i for i, c in enumerate(cf))

def irr(cf):
    low, high = -0.9, 2.0
    for _ in range(200):
        mid = (low + high) / 2
        try:
            if npv(cf, mid) > 0:
                low = mid
            else:
                high = mid
        except Exception:
            return 0.0
    return round((low + high) / 2, 3)

def payback(cf):
    cum = 0
    for i, c in enumerate(cf):
        cum += c
        if cum >= 0:
            return i
    return YEARS

def evaluate(row):
    power = row["power_kw"]
    demand = row["predicted_demand_kwh"]        # прогноз спроса, кВт·ч в час
    daily_kwh = demand * 24 * UTILIZATION_RATE   # реально отпущено за сутки
    
    capex = power * CAPEX_PER_KW
    annual_revenue = daily_kwh * 365 * TARIFF
    annual_opex = OPEX_PER_YEAR
    annual_cf = annual_revenue - annual_opex
    
    cf = [-capex] + [annual_cf] * YEARS
    
    return pd.Series({
        "capex": round(capex),
        "annual_revenue": round(annual_revenue),
        "npv": round(npv(cf, DISCOUNT_RATE)),
        "irr": irr(cf),
        "payback_years": round(payback(cf), 1),
    })

print("Скрипт economics.py запущен")

df = pd.read_csv(r"C:\rosa_project\output\optimized_locations.csv")
print(f"Загружено локаций: {len(df)}")

econ = df.apply(evaluate, axis=1)
result = pd.concat([df, econ], axis=1)
result.to_csv(r"C:\rosa_project\output\result.csv", index=False)

print("Экономика посчитана")
print(result[["priority", "power_kw", "capex", "npv", "irr", "payback_years"]].head(10))
print("Готово")