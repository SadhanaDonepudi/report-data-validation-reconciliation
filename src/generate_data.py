"""
Generate SYNTHETIC two-layer dataset: Snowflake-style source vs Power BI report layer.
All data is synthetic. Fixed seed 42. Report layer = source copy + deliberately injected defects.
Writes CSVs to data/ and manifest to docs/injected_defects.md + data/manifest.json
"""
import json
import random
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
DOCS = BASE / "docs"
DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

# ---------- SOURCE LAYER (clean) ----------
segments = ["Retail", "Corporate", "Consumer"]
regions = ["North", "South", "East", "West", "Central"]
categories = ["Electronics", "Furniture", "Clothing", "Food", "Office Supplies"]
payment_methods = ["Card", "Bank Transfer", "Cash", "Digital Wallet"]

customers = []
for i in range(1, 101):
    customers.append({
        "customer_id": f"CUST-{i:03d}",
        "customer_name": f"Customer {i:03d}",
        "email": f"customer{i:03d}@example.com",
        "segment": random.choice(segments),
        "region": random.choice(regions),
        "created_date": pd.Timestamp("2023-01-01") + pd.Timedelta(days=random.randint(0, 700)),
    })
source_customers = pd.DataFrame(customers)
source_customers["created_date"] = pd.to_datetime(source_customers["created_date"]).dt.date

products = []
base_prices = [29.99, 49.99, 99.99, 199.99, 499.99, 19.99, 79.99, 149.99, 299.99, 999.99,
               39.99, 59.99, 89.99, 129.99, 249.99, 399.99, 699.99, 24.99, 69.99, 179.99]
for i in range(1, 21):
    products.append({
        "product_id": f"PROD-{i:02d}",
        "product_name": f"Product {i:02d}",
        "category": categories[(i - 1) % len(categories)],
        "unit_price": base_prices[i - 1],
    })
source_products = pd.DataFrame(products)
price_map = dict(zip(source_products["product_id"], source_products["unit_price"]))

orders = []
for i in range(1, 501):
    cid = random.choice(source_customers["customer_id"].tolist())
    pid = random.choice(source_products["product_id"].tolist())
    qty = random.randint(1, 10)
    amount = round(qty * price_map[pid], 2)
    orders.append({
        "order_id": f"ORD-{i:04d}",
        "customer_id": cid,
        "product_id": pid,
        "order_date": (pd.Timestamp("2025-01-01") + pd.Timedelta(days=random.randint(0, 364))).date(),
        "quantity": qty,
        "order_amount": amount,
    })
source_orders = pd.DataFrame(orders)

payments = []
for i, row in enumerate(source_orders.itertuples(), start=1):
    payments.append({
        "payment_id": f"PAY-{i:04d}",
        "order_id": row.order_id,
        "payment_date": (pd.Timestamp(row.order_date) + pd.Timedelta(days=random.randint(0, 5))).date() if isinstance(row.order_date, pd.Timestamp) else row.order_date,
        "payment_amount": float(row.order_amount),
        "payment_method": random.choice(payment_methods),
    })
# fix payment_date type
source_payments = pd.DataFrame(payments)

source_customers.to_csv(DATA / "source_customers.csv", index=False)
source_products.to_csv(DATA / "source_products.csv", index=False)
source_orders.to_csv(DATA / "source_orders.csv", index=False)
source_payments.to_csv(DATA / "source_payments.csv", index=False)

# ---------- REPORT LAYER (defective copy) ----------
report_customers = source_customers.copy()
report_products = source_products.copy()
report_orders = source_orders.copy()
report_payments = source_payments.copy()

manifest = {
    "seed": SEED,
    "synthetic": True,
    "source_rows": {
        "source_customers": len(source_customers),
        "source_products": len(source_products),
        "source_orders": len(source_orders),
        "source_payments": len(source_payments),
    },
    "defects": {}
}

# report_customers: 3 null customer_name (indices 5,23,67 -> rows 6,24,68)
null_cust_name_idx = [5, 23, 67]
report_customers.loc[null_cust_name_idx, "customer_name"] = np.nan
manifest["defects"]["report_customers_null_customer_name"] = len(null_cust_name_idx)

# report_customers: duplicate customer_id - duplicate CUST-010 and CUST-042 (2 extra rows)
dup_cust_ids = ["CUST-010", "CUST-042"]
dup_rows_cust = report_customers[report_customers["customer_id"].isin(dup_cust_ids)].copy()
report_customers = pd.concat([report_customers, dup_rows_cust], ignore_index=True)
manifest["defects"]["report_customers_duplicate_customer_id_extra_rows"] = len(dup_rows_cust)
manifest["defects"]["report_customers_duplicate_customer_id_distinct_keys"] = len(dup_cust_ids)

# report_products: 2 null category
null_prod_cat_idx = [3, 11]
report_products.loc[null_prod_cat_idx, "category"] = np.nan
manifest["defects"]["report_products_null_category"] = len(null_prod_cat_idx)

# report_products: duplicate PROD-05 (1 extra)
dup_prod = report_products[report_products["product_id"] == "PROD-05"].copy()
report_products = pd.concat([report_products, dup_prod], ignore_index=True)
manifest["defects"]["report_products_duplicate_product_id_extra_rows"] = 1
manifest["defects"]["report_products_duplicate_product_id_distinct_keys"] = 1

# report_orders defects - use non-overlapping indices
# 5 null customer_id
null_order_cust_idx = [10, 50, 100, 200, 300]
report_orders.loc[null_order_cust_idx, "customer_id"] = np.nan
manifest["defects"]["report_orders_null_customer_id"] = len(null_order_cust_idx)

# 3 orphan customer_id (FK not in customers)
orphan_cust_idx = [15, 55, 105]
report_orders.loc[orphan_cust_idx, "customer_id"] = ["CUST-999", "CUST-998", "CUST-997"]
manifest["defects"]["report_orders_orphan_customer_id"] = len(orphan_cust_idx)

# 2 orphan product_id
orphan_prod_idx = [20, 60]
report_orders.loc[orphan_prod_idx, "product_id"] = ["PROD-99", "PROD-98"]
manifest["defects"]["report_orders_orphan_product_id"] = len(orphan_prod_idx)

# 4 out-of-range quantity (<=0)
oor_qty_idx = [25, 65, 110, 210]
report_orders.loc[oor_qty_idx, "quantity"] = [0, -1, -5, 0]
manifest["defects"]["report_orders_out_of_range_quantity_le_zero"] = len(oor_qty_idx)

# 3 out-of-range order_amount (negative)
oor_amt_idx = [30, 70, 120]
report_orders.loc[oor_amt_idx, "order_amount"] = [-100.00, -50.00, -25.00]
manifest["defects"]["report_orders_negative_order_amount"] = len(oor_amt_idx)

# drift injection: inflate 8 orders by +100 each (indices distinct from above)
drift_idx = [1, 2, 3, 4, 5, 6, 7, 8]
# ensure not overlapping with previous sets
assert not set(drift_idx) & set(null_order_cust_idx + orphan_cust_idx + orphan_prod_idx + oor_qty_idx + oor_amt_idx)
report_orders.loc[drift_idx, "order_amount"] = report_orders.loc[drift_idx, "order_amount"] + 100.00
manifest["defects"]["report_orders_drift_inflated_rows"] = len(drift_idx)
manifest["defects"]["report_orders_drift_injected_amount"] = 800.00

# duplicate order_id: duplicate 4 orders (extra rows)
dup_order_ids = ["ORD-0010", "ORD-0120", "ORD-0250", "ORD-0400"]
dup_orders = report_orders[report_orders["order_id"].isin(dup_order_ids)].copy()
# deduplicate to exactly 4 rows (one per id)
dup_orders = dup_orders.drop_duplicates(subset=["order_id"]).head(4)
report_orders = pd.concat([report_orders, dup_orders], ignore_index=True)
manifest["defects"]["report_orders_duplicate_order_id_extra_rows"] = len(dup_orders)
manifest["defects"]["report_orders_duplicate_order_id_distinct_keys"] = len(dup_order_ids)

# report_payments defects
null_pay_amt_idx = [12, 52, 102]
report_payments.loc[null_pay_amt_idx, "payment_amount"] = np.nan
manifest["defects"]["report_payments_null_payment_amount"] = len(null_pay_amt_idx)

orphan_pay_idx = [18, 58]
report_payments.loc[orphan_pay_idx, "order_id"] = ["ORD-9999", "ORD-9998"]
manifest["defects"]["report_payments_orphan_order_id"] = len(orphan_pay_idx)

# 2 negative payment_amount (out-of-range, singular test)
neg_pay_idx = [33, 73]
report_payments.loc[neg_pay_idx, "payment_amount"] = [-75.00, -20.00]
manifest["defects"]["report_payments_negative_payment_amount"] = len(neg_pay_idx)

dup_pay_ids = ["PAY-0010", "PAY-0200"]
dup_pay = report_payments[report_payments["payment_id"].isin(dup_pay_ids)].drop_duplicates(subset=["payment_id"])
report_payments = pd.concat([report_payments, dup_pay], ignore_index=True)
manifest["defects"]["report_payments_duplicate_payment_id_extra_rows"] = len(dup_pay)
manifest["defects"]["report_payments_duplicate_payment_id_distinct_keys"] = len(dup_pay_ids)

manifest["report_rows"] = {
    "report_customers": len(report_customers),
    "report_products": len(report_products),
    "report_orders": len(report_orders),
    "report_payments": len(report_payments),
}

# totals for reconciliation ground truth
source_orders_total = float(source_orders["order_amount"].sum())
report_orders_total = float(report_orders["order_amount"].sum())
source_payments_total = float(source_payments["payment_amount"].sum())
report_payments_total = float(pd.to_numeric(report_payments["payment_amount"], errors="coerce").sum())

manifest["reconciliation_ground_truth"] = {
    "source_orders_total": round(source_orders_total, 2),
    "report_orders_total": round(report_orders_total, 2),
    "orders_diff": round(report_orders_total - source_orders_total, 2),
    "orders_diff_pct": round(abs(report_orders_total - source_orders_total) / source_orders_total * 100, 6) if source_orders_total else 0,
    "source_payments_total": round(source_payments_total, 2),
    "report_payments_total": round(report_payments_total, 2),
    "payments_diff": round(report_payments_total - source_payments_total, 2),
    "payments_diff_pct": round(abs(report_payments_total - source_payments_total) / source_payments_total * 100, 6) if source_payments_total else 0,
    "threshold_pct": 0.01,
}

report_customers.to_csv(DATA / "report_customers.csv", index=False)
report_products.to_csv(DATA / "report_products.csv", index=False)
report_orders.to_csv(DATA / "report_orders.csv", index=False)
report_payments.to_csv(DATA / "report_payments.csv", index=False)

with open(DATA / "manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

# write docs/injected_defects.md from ground truth
lines = []
lines.append("# Injected Defects Manifest — SYNTHETIC DATA")
lines.append("")
lines.append("> **SYNTHETIC DATA**: All rows are generated with seed 42. Report layer defects below are deliberately injected ground truth.")
lines.append("")
lines.append(f"Seed: `{SEED}`")
lines.append("")
lines.append("## Source layer (clean, expected PASS)")
for k, v in manifest["source_rows"].items():
    lines.append(f"- `{k}`: {v} rows")
lines.append("")
lines.append("## Report layer row counts (after injection)")
for k, v in manifest["report_rows"].items():
    lines.append(f"- `{k}`: {v} rows")
lines.append("")
lines.append("## Injected defects by table (exact ground-truth counts)")
lines.append("")
lines.append("| # | Table | Defect | Count | Notes |")
lines.append("|---|-------|--------|-------|-------|")
rows = [
    ("report_customers", "null customer_name", manifest["defects"]["report_customers_null_customer_name"], "indices [5,23,67]"),
    ("report_customers", "duplicate customer_id (extra rows)", manifest["defects"]["report_customers_duplicate_customer_id_extra_rows"], "CUST-010, CUST-042 duplicated"),
    ("report_products", "null category", manifest["defects"]["report_products_null_category"], "indices [3,11]"),
    ("report_products", "duplicate product_id (extra rows)", manifest["defects"]["report_products_duplicate_product_id_extra_rows"], "PROD-05 duplicated"),
    ("report_orders", "null customer_id", manifest["defects"]["report_orders_null_customer_id"], "5 rows"),
    ("report_orders", "orphan customer_id (FK violation)", manifest["defects"]["report_orders_orphan_customer_id"], "CUST-999/998/997"),
    ("report_orders", "orphan product_id (FK violation)", manifest["defects"]["report_orders_orphan_product_id"], "PROD-99/98"),
    ("report_orders", "out-of-range quantity <= 0", manifest["defects"]["report_orders_out_of_range_quantity_le_zero"], "0,-1,-5,0"),
    ("report_orders", "negative order_amount", manifest["defects"]["report_orders_negative_order_amount"], "-100,-50,-25"),
    ("report_orders", "duplicate order_id (extra rows)", manifest["defects"]["report_orders_duplicate_order_id_extra_rows"], "ORD-0010,0120,0250,0400"),
    ("report_orders", "drift-inflated order_amount (+$100 x 8 rows)", manifest["defects"]["report_orders_drift_inflated_rows"], "+$800.00 injected drift"),
    ("report_payments", "null payment_amount", manifest["defects"]["report_payments_null_payment_amount"], "3 rows"),
    ("report_payments", "orphan order_id (FK violation)", manifest["defects"]["report_payments_orphan_order_id"], "ORD-9999/9998"),
    ("report_payments", "negative payment_amount", manifest["defects"]["report_payments_negative_payment_amount"], "-75,-20"),
    ("report_payments", "duplicate payment_id (extra rows)", manifest["defects"]["report_payments_duplicate_payment_id_extra_rows"], "PAY-0010, PAY-0200"),
]
for i, (tbl, defect, cnt, note) in enumerate(rows, 1):
    lines.append(f"| {i} | `{tbl}` | {defect} | {cnt} | {note} |")
lines.append("")
lines.append("## Reconciliation ground truth")
rt = manifest["reconciliation_ground_truth"]
lines.append(f"- source_orders_total: ${rt['source_orders_total']:,.2f}")
lines.append(f"- report_orders_total: ${rt['report_orders_total']:,.2f}")
lines.append(f"- orders diff: ${rt['orders_diff']:,.2f} ({rt['orders_diff_pct']:.4f}%) — threshold 0.01% => {'FAIL' if rt['orders_diff_pct']>0.01 else 'PASS'}")
lines.append(f"- source_payments_total: ${rt['source_payments_total']:,.2f}")
lines.append(f"- report_payments_total: ${rt['report_payments_total']:,.2f}")
lines.append(f"- payments diff: ${rt['payments_diff']:,.2f} ({rt['payments_diff_pct']:.4f}%) — threshold 0.01% => {'FAIL' if rt['payments_diff_pct']>0.01 else 'PASS'}")
lines.append("")
lines.append("Generated by `src/generate_data.py` from ground truth — never hand-edited.")
(DOCS / "injected_defects.md").write_text("\n".join(lines))
print(json.dumps(manifest, indent=2))
print(f"Wrote CSVs to {DATA}")
