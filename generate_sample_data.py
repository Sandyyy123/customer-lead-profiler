"""
Generates synthetic CRM sample data for testing the analysis pipeline.
Produces customers.csv and leads.csv with realistic distributions.
"""

import pandas as pd
import numpy as np
import argparse


RNG = np.random.default_rng(42)
REGIONS = ["Northeast", "Southeast", "Midwest", "West Coast", "Southwest"]
SOURCES = ["Organic Search", "Email", "Paid Social", "Referral", "Direct"]
CATEGORIES = ["Core", "Premium", "Entry-level", "Bundle"]


def gen_customers(n: int = 500) -> pd.DataFrame:
    ages = RNG.normal(38, 9, n).clip(22, 65).astype(int)
    return pd.DataFrame({
        "customer_id": [f"C{i:05d}" for i in range(n)],
        "age": ages,
        "order_count": RNG.integers(1, 12, n),
        "avg_order_value": RNG.normal(220, 80, n).clip(30, 600).round(2),
        "days_since_last_order": RNG.integers(1, 300, n),
        "email_open_rate": RNG.beta(3, 5, n).round(3),
        "pages_visited": RNG.integers(3, 20, n),
        "touchpoint_count": RNG.integers(2, 8, n),
        "income_estimate": RNG.choice([45000, 65000, 85000, 110000, 140000], n,
                                       p=[0.10, 0.20, 0.35, 0.25, 0.10]),
        "referral_source": RNG.choice(SOURCES, n, p=[0.30, 0.28, 0.18, 0.14, 0.10]),
        "product_category": RNG.choice(CATEGORIES, n, p=[0.40, 0.25, 0.20, 0.15]),
        "region": RNG.choice(REGIONS, n, p=[0.38, 0.24, 0.19, 0.12, 0.07]),
    })


def gen_leads(n: int = 1200) -> pd.DataFrame:
    ages = RNG.normal(29, 10, n).clip(18, 60).astype(int)
    return pd.DataFrame({
        "lead_id": [f"L{i:05d}" for i in range(n)],
        "age": ages,
        "order_count": np.zeros(n, dtype=int),
        "avg_order_value": np.zeros(n),
        "days_since_last_order": np.full(n, 9999),
        "email_open_rate": RNG.beta(1, 8, n).round(3),
        "pages_visited": RNG.integers(1, 6, n),
        "touchpoint_count": RNG.integers(0, 3, n),
        "income_estimate": RNG.choice([25000, 40000, 55000, 75000, 100000], n,
                                       p=[0.15, 0.30, 0.30, 0.18, 0.07]),
        "referral_source": RNG.choice(SOURCES, n, p=[0.15, 0.12, 0.45, 0.10, 0.18]),
        "product_category": RNG.choice(CATEGORIES, n, p=[0.20, 0.10, 0.55, 0.15]),
        "region": RNG.choice(REGIONS, n, p=[0.25, 0.20, 0.18, 0.28, 0.09]),
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic CRM sample data")
    parser.add_argument("--customers", default="data/customers.csv")
    parser.add_argument("--leads", default="data/leads.csv")
    parser.add_argument("--n-customers", type=int, default=500)
    parser.add_argument("--n-leads", type=int, default=1200)
    args = parser.parse_args()

    import os
    os.makedirs("data", exist_ok=True)

    customers = gen_customers(args.n_customers)
    leads = gen_leads(args.n_leads)
    customers.to_csv(args.customers, index=False)
    leads.to_csv(args.leads, index=False)
    print(f"Generated {args.n_customers} customers -> {args.customers}")
    print(f"Generated {args.n_leads} leads -> {args.leads}")
