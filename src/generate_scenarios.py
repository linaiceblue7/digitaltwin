"""
generate_scenarios.py
Генерирует сценарии развития сети: 2026, 2028, 2030.
Чистит названия от мусора OSM.
"""
import pandas as pd
import numpy as np
import json

CAPEX_PER_KW = 40_000
OPEX_PER_YEAR = 1_200_000
TARIFF = 20
DISCOUNT_RATE = 0.12
YEARS = 10
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


def calc_economics(row):
    power = float(row["power_kw"])
    demand = float(row["predicted_demand_kwh"])
    utilization = UTILIZATION_BASE + (demand - 40) / 40 * 0.05
    utilization = max(UTILIZATION_MIN, min(UTILIZATION_MAX, utilization))

    annual_revenue = power * 24 * 365 * TARIFF * utilization
    capex = power * CAPEX_PER_KW
    annual_cf = annual_revenue - OPEX_PER_YEAR
    cf = [-capex] + [annual_cf] * YEARS

    return {
        "utilization": round(utilization, 3),
        "capex": round(capex),
        "annual_revenue": round(annual_revenue),
        "annual_cf": round(annual_cf),
        "npv": round(npv(cf, DISCOUNT_RATE)),
        "irr": irr(cf),
        "payback_years": round(payback(cf), 1),
    }


def clean_string(value, default=""):
    """Чистит строку от мусора OSM."""
    if pd.isna(value):
        return default
    s = str(value).strip()
    if s.lower() in ("nan", "none", ""):
        return default
    if len(s) < 3:
        return default
    bad_words = ["хорошо", "отлично", "ура", "супер", "класс", "привет",
                 "ok", "okay", "test", "тест", "нет", "да"]
    s_clean = s.lower().replace("!", "").replace("?", "").strip()
    if s_clean in bad_words:
        return default
    return s


def make_record(row, priority):
    econ = calc_economics(row)

    name = clean_string(row.get("name", ""), "")
    loc_type = clean_string(row.get("type", "parking"), "parking")

    if not name:
        if loc_type == "mall":
            name = "Торговый центр №" + str(priority)
        elif loc_type == "transport_hub":
            name = "Транспортный узел №" + str(priority)
        else:
            name = "Парковка №" + str(priority)

    return {
        "priority": int(priority),
        "latitude": round(float(row["latitude"]), 6),
        "longitude": round(float(row["longitude"]), 6),
        "power_kw": int(row["power_kw"]),
        "predicted_demand_kwh": round(float(row["predicted_demand_kwh"]), 2),
        "type": loc_type,
        "name": name,
        "utilization": econ["utilization"],
        "capex": econ["capex"],
        "annual_revenue": econ["annual_revenue"],
        "annual_cf": econ["annual_cf"],
        "npv": econ["npv"],
        "irr": econ["irr"],
        "payback_years": econ["payback_years"],
    }


def main():
    print("=== generate_scenarios.py ===\n")

    df = pd.read_csv(r"C:\rosa_project\output\potential_with_demand.csv")
    print(f"Загружено локаций: {len(df)}")

    type_score_map = {"mall": 1.0, "transport_hub": 0.9, "parking": 0.6}
    df["type_score"] = df["type"].map(type_score_map).fillna(0.5)
    df["demand_norm"] = df["predicted_demand_kwh"] / df["predicted_demand_kwh"].max()
    df["center_norm"] = 1 - (df["dist_to_center_km"] / df["dist_to_center_km"].max())
    df["final_score"] = 0.6 * df["demand_norm"] + 0.25 * df["type_score"] + 0.15 * df["center_norm"]

    df_sorted = df.sort_values("final_score", ascending=False).reset_index(drop=True)

    scenarios = {
        "2026": df_sorted.head(20),
        "2028": df_sorted.head(35),
        "2030": df_sorted.head(60)
    }

    for year, subset in scenarios.items():
        records = []
        for i, (_, row) in enumerate(subset.iterrows(), start=1):
            records.append(make_record(row, i))

        output_path = rf"C:\rosa_project\web\locations_{year}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2, allow_nan=False)

        total_npv = sum(r["npv"] for r in records)
        total_capex = sum(r["capex"] for r in records)
        print(f"\n{year}: {len(records)} локаций")
        print(f"   Суммарный NPV: {total_npv / 1e6:.0f} млн ₽")
        print(f"   Суммарный CAPEX: {total_capex / 1e6:.0f} млн ₽")
        print(f"   Сохранено: {output_path}")

    print("\n=== Готово ===")


if __name__ == "__main__":
    main()