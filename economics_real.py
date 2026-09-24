"""
economics_real.py
Считает экономику для 20 отобранных реальных локаций Москвы.
"""
import pandas as pd
import numpy as np

# Параметры экономики
CAPEX_PER_KW = 40_000
OPEX_PER_YEAR = 1_200_000
TARIFF = 20
DISCOUNT_RATE = 0.12
YEARS = 10

# Загрузка в зависимости от спроса (кВт·ч/час)
# При спросе 40 кВт·ч/час — загрузка 10%
UTILIZATION_BASE = 0.10
UTILIZATION_MIN = 0.06
UTILIZATION_MAX = 0.18


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

    # Загрузка: при demand=40 → 10%, диапазон 6-18%
    utilization = UTILIZATION_BASE + (demand - 40) / 40 * 0.05
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


def main():
    print("=== economics_real.py ===")
    print("Экономика для 20 реальных локаций Москвы\n")

    df = pd.read_csv(r"C:\rosa_project\output\optimized_locations_real.csv")
    print(f"Загружено локаций: {len(df)}")

    econ = df.apply(evaluate, axis=1)
    result = pd.concat([df, econ], axis=1)

    output_path = r"C:\rosa_project\output\result_real.csv"
    result.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Сохранено: {output_path}\n")

    print("=== Результаты ===")
    cols = ["priority", "name", "type", "power_kw", "predicted_demand_kwh",
            "utilization", "annual_revenue", "npv", "irr", "payback_years"]
    print(result[cols].to_string(index=False))

    print("\n=== Статистика ===")
    print(f"Средний NPV: {result['npv'].mean() / 1e6:.1f} млн ₽")
    print(f"Суммарный NPV: {result['npv'].sum() / 1e6:.1f} млн ₽")
    print(f"Средний IRR: {result['irr'].mean() * 100:.1f}%")
    print(f"Средняя окупаемость: {result['payback_years'].mean():.1f} лет")
    print(f"Суммарный CAPEX: {result['capex'].sum() / 1e6:.0f} млн ₽")
    print(f"Средняя мощность: {result['power_kw'].mean():.0f} кВт")

    print("\n=== Готово ===")


if __name__ == "__main__":
    main()