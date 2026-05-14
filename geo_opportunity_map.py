"""
Geographic opportunity analysis: compares lead density vs customer density by region.
Identifies regions where leads are not converting (marketing allocation gaps).
"""

import pandas as pd
import numpy as np
import argparse


def compute_geo_gap(customers: pd.DataFrame, leads: pd.DataFrame, region_col: str = "region") -> pd.DataFrame:
    cust_counts = customers[region_col].value_counts(normalize=True).rename("customer_share")
    lead_counts = leads[region_col].value_counts(normalize=True).rename("lead_share")

    geo = pd.concat([cust_counts, lead_counts], axis=1).fillna(0).reset_index()
    geo.columns = [region_col, "customer_share", "lead_share"]

    geo["conversion_gap"] = geo["lead_share"] - geo["customer_share"]
    geo["opportunity_score"] = (geo["lead_share"] / (geo["customer_share"] + 1e-6)).round(2)

    def classify(row):
        if row["opportunity_score"] > 1.5 and row["lead_share"] > 0.05:
            return "Underperforming - High Priority"
        elif row["opportunity_score"] > 1.2:
            return "Underperforming - Monitor"
        elif row["opportunity_score"] < 0.8:
            return "Overperforming"
        else:
            return "On Target"

    geo["status"] = geo.apply(classify, axis=1)
    geo["customer_share_pct"] = (geo["customer_share"] * 100).round(1)
    geo["lead_share_pct"] = (geo["lead_share"] * 100).round(1)

    return geo.sort_values("opportunity_score", ascending=False)


def run(customers_path: str, leads_path: str, output_path: str, region_col: str = "region") -> None:
    customers = pd.read_csv(customers_path)
    leads = pd.read_csv(leads_path)

    result = compute_geo_gap(customers, leads, region_col)
    result.to_csv(output_path, index=False)

    print(result[[region_col, "customer_share_pct", "lead_share_pct", "opportunity_score", "status"]].to_string(index=False))
    print(f"\nSaved to {output_path}")

    gaps = result[result["status"].str.contains("Underperforming")]
    if not gaps.empty:
        print(f"\n{len(gaps)} underperforming region(s) identified:")
        for _, row in gaps.iterrows():
            print(f"  - {row[region_col]}: {row['lead_share_pct']}% of leads, only {row['customer_share_pct']}% of customers")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Identify geographic conversion gaps")
    parser.add_argument("--customers", required=True)
    parser.add_argument("--leads", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--region-col", default="region")
    args = parser.parse_args()
    run(args.customers, args.leads, args.output, args.region_col)
