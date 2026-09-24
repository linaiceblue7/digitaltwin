# VERSION_2026_09_22_NEW
import pandas as pd
import numpy as np

CAPEX_PER_KW = 40_000
OPEX_PER_YEAR = 1_200_000
TARIFF = 20
DISCOUNT_RATE = 0.12
YEARS = 10
UTILIZATION_BASE = 0.10
UTILIZATION_MIN = 0.06
UTILIZATION_MAX = 0.16


def npv(cashflows, rate):
    return sum(cf / (1 + rate) ** i for i, cf in enumerate(cashflows))


def irr(cashflows):
    low, high = -0.5, 1.0
    for _ in range(200):
        mid = (low + high) / 2
        try:
            v = npv(cashflows, mid)
            if v > 0:
                low = mid
            else:
                high = mid
        except Exception:
            return 0.0
    return round((low + high) / 2, 3)


def payback(cashflows):
    cum = 0
    for i, cf in enumerate(cashflows):
        cum += cf
        if cum >= 0:
            return i
    return YEARS


def evaluate(row):
    power = row["power_kw"]
    demand = row["predicted_demand_kwh"]
    utilization = UTILIZATION_BASE + (demand - 150) / 100 * 0.06
    utilization = max(UTILIZATION_MIN, min(UTILIZATION_MAX, utilization))
    annual_revenue = power * 24 * 365 * TARIFF * utilization
    capex = power * CAPEX_PER_KW
    annual_cf = annual_revenue - OPEX_PER_YEAR
    cf = [-capex] + [annual_cf] * YEARS
    return pd.Series({
        "utilization": round(utilization, 3),
        "capex": round(capex),
        "annual_revenue": round(annual_revenue),
        "annual_cf": round(annual_cf),
        "npv": round(npv(cf, DISCOUNT_RATE)),
        "irr": irr(cf),
        "payback_years": round(payback(cf), 1),
    })


if __name__ == "__main__":
    print("=== NEW VERSION 2026_09_22 ===")
    df = pd.read_csv(r"C:\rosa_project\output\optimized_locations.csv")
    print(f"Загружено локаций: {len(df)}")
    econ = df.apply(evaluate, axis=1)
    result = pd.concat([df, econ], axis=1)
    result.to_csv(r"C:\rosa_project\output\result.csv", index=False)
    print(result[["priority", "power_kw", "predicted_demand_kwh", "utilization",
                  "annual_revenue", "npv", "irr", "payback_years"]].head(10))
    print("=== Готово ===")