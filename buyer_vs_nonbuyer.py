"""
Statistical comparison of buyers (converted leads) vs non-buyers.
Outputs a ranked table of differentiating variables with effect sizes and p-values.
"""

import pandas as pd
import numpy as np
from scipy import stats
import argparse
import json


NUMERIC_COLS = [
    "pages_visited",
    "email_open_rate",
    "age",
    "days_to_first_action",
    "touchpoint_count",
    "income_estimate",
]

CATEGORICAL_COLS = [
    "referral_source",
    "product_category",
    "region",
]


def cohens_d(group_a: pd.Series, group_b: pd.Series) -> float:
    """Cohen's d effect size for two independent groups."""
    n_a, n_b = len(group_a), len(group_b)
    pooled_std = np.sqrt(
        ((n_a - 1) * group_a.std() ** 2 + (n_b - 1) * group_b.std() ** 2)
        / (n_a + n_b - 2)
    )
    return (group_a.mean() - group_b.mean()) / pooled_std if pooled_std > 0 else 0.0


def cramers_v(col: pd.Series, target: pd.Series) -> float:
    """Cramer's V association for categorical variables."""
    ct = pd.crosstab(col, target)
    chi2 = stats.chi2_contingency(ct, correction=False)[0]
    n = ct.sum().sum()
    k = min(ct.shape) - 1
    return np.sqrt(chi2 / (n * k)) if k > 0 else 0.0


def compare(customers: pd.DataFrame, leads: pd.DataFrame) -> pd.DataFrame:
    results = []

    for col in NUMERIC_COLS:
        if col not in customers.columns or col not in leads.columns:
            continue
        a = customers[col].dropna()
        b = leads[col].dropna()
        t_stat, p_val = stats.ttest_ind(a, b, equal_var=False)
        d = cohens_d(a, b)
        results.append(
            {
                "variable": col,
                "type": "numeric",
                "customers_mean": round(a.mean(), 2),
                "leads_mean": round(b.mean(), 2),
                "delta_pct": round((a.mean() - b.mean()) / (b.mean() + 1e-9) * 100, 1),
                "cohens_d": round(abs(d), 3),
                "p_value": round(p_val, 4),
                "significant": p_val < 0.05,
            }
        )

    for col in CATEGORICAL_COLS:
        combined = pd.concat(
            [customers[[col]].assign(converted=1), leads[[col]].assign(converted=0)],
            ignore_index=True,
        )
        if col not in combined.columns:
            continue
        v = cramers_v(combined[col].fillna("Unknown"), combined["converted"])
        chi2, p_val, _, _ = stats.chi2_contingency(
            pd.crosstab(combined[col].fillna("Unknown"), combined["converted"]),
            correction=False,
        )
        results.append(
            {
                "variable": col,
                "type": "categorical",
                "customers_mode": customers[col].mode().iloc[0] if len(customers[col].dropna()) else "N/A",
                "leads_mode": leads[col].mode().iloc[0] if len(leads[col].dropna()) else "N/A",
                "cramers_v": round(v, 3),
                "p_value": round(p_val, 4),
                "significant": p_val < 0.05,
            }
        )

    df = pd.DataFrame(results)
    effect_col = df.get("cohens_d", df.get("cramers_v"))
    df["effect_size"] = df["cohens_d"].fillna(df.get("cramers_v", 0)) if "cohens_d" in df.columns else df.get("cramers_v", 0)
    return df.sort_values("effect_size", ascending=False)


def run(customers_path: str, leads_path: str, output_path: str) -> None:
    customers = pd.read_csv(customers_path)
    leads = pd.read_csv(leads_path)
    results = compare(customers, leads)
    results.to_csv(output_path, index=False)
    print(results.to_string(index=False))
    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare buyer vs non-buyer profiles")
    parser.add_argument("--customers", required=True)
    parser.add_argument("--leads", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    run(args.customers, args.leads, args.output)
