# Customer & Lead Profiler

A Python pipeline for analyzing CRM exports to understand who your best customers are, why leads don't convert, and where your next growth opportunities lie.

## What it does

| Script | Purpose |
|---|---|
| `customer_segmentation.py` | K-Means clustering into 4-6 behavioral segments |
| `buyer_vs_nonbuyer.py` | Statistical comparison (t-tests, Cohen's d, Cramer's V) |
| `geo_opportunity_map.py` | Region-by-region lead vs customer density gap analysis |
| `excel_dashboard_builder.py` | Multi-sheet formatted Excel dashboard with charts |
| `generate_sample_data.py` | Synthetic CRM data generator for testing |

## Quick start

```bash
pip install -r requirements.txt

# Generate sample data
python generate_sample_data.py

# Run the full pipeline
python main.py --customers data/customers.csv --leads data/leads.csv --output-dir output/
```

## Input format

**customers.csv** — one row per customer:
```
customer_id, age, order_count, avg_order_value, days_since_last_order,
email_open_rate, pages_visited, touchpoint_count, income_estimate,
referral_source, product_category, region
```

**leads.csv** — same schema (order-related columns can be 0/null for non-buyers).

## Outputs

- `customers_segmented.csv` — original data + cluster_id + segment label
- `buyer_comparison.csv` — ranked differentiating variables with effect sizes + p-values
- `geo_analysis.csv` — region-level conversion gap analysis
- `dashboard.xlsx` — formatted Excel workbook with summary, segment, comparison, and geo sheets

## License

CC BY-NC 4.0 — view and adapt for non-commercial use.
