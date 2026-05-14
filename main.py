"""
End-to-end pipeline: segmentation -> comparison -> geo analysis -> Excel dashboard.
Run this to execute all four analysis steps in sequence.

Usage:
    python main.py --customers data/customers.csv --leads data/leads.csv --output-dir output/
"""

import argparse
import os
from customer_segmentation import run as run_segmentation
from buyer_vs_nonbuyer import run as run_comparison
from geo_opportunity_map import run as run_geo
from excel_dashboard_builder import build as build_dashboard


def main():
    parser = argparse.ArgumentParser(description="Full customer & lead analysis pipeline")
    parser.add_argument("--customers", required=True, help="Customers CSV path")
    parser.add_argument("--leads", required=True, help="Leads CSV path")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    seg_out = os.path.join(args.output_dir, "customers_segmented.csv")
    cmp_out = os.path.join(args.output_dir, "buyer_comparison.csv")
    geo_out = os.path.join(args.output_dir, "geo_analysis.csv")
    xls_out = os.path.join(args.output_dir, "dashboard.xlsx")

    print("=== Step 1: Customer Segmentation ===")
    run_segmentation(args.customers, seg_out)

    print("\n=== Step 2: Buyer vs Non-Buyer Comparison ===")
    run_comparison(args.customers, args.leads, cmp_out)

    print("\n=== Step 3: Geographic Opportunity Map ===")
    run_geo(args.customers, args.leads, geo_out)

    print("\n=== Step 4: Excel Dashboard ===")
    build_dashboard(seg_out, cmp_out, geo_out, xls_out)

    print(f"\nAll outputs saved to {args.output_dir}/")
    print(f"  {seg_out}")
    print(f"  {cmp_out}")
    print(f"  {geo_out}")
    print(f"  {xls_out}")


if __name__ == "__main__":
    main()
