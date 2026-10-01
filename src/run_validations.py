"""
Validation harness: executes all 25 checks against SYNTHETIC CSVs.
Writes outputs/validation_report.md with real numbers.
Test count is programmatic: 20 generic (schema.yml) + 5 singular (tests/*.sql) = 25.
"""
import json
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
OUT = BASE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

THRESHOLD_PCT = 0.01

def load(name):
    return pd.read_csv(DATA / f"{name}.csv")

def unique_failures(df, col):
    # extra duplicate rows
    total = len(df)
    distinct = df[col].nunique(dropna=False)
    extra = total - distinct
    # distinct duplicated keys
    dup_keys = df[df.duplicated(col, keep=False)][col].nunique() if extra > 0 else 0
    return extra, dup_keys

def not_null_failures(df, col):
    return int(df[col].isna().sum())

def relationships_failures(child, fk, parent, pk):
    parent_keys = set(parent[pk].dropna().unique())
    mask = child[fk].notna() & (~child[fk].isin(parent_keys))
    return int(mask.sum())

def accepted_values_failures(df, col, allowed):
    mask = df[col].notna() & (~df[col].isin(allowed))
    return int(mask.sum())

def main():
    sc = load("source_customers"); sp = load("source_products"); so = load("source_orders"); spa = load("source_payments")
    rc = load("report_customers"); rp = load("report_products"); ro = load("report_orders"); rpa = load("report_payments")

    results = []  # dicts: id, name, type, layer, rows_checked, failures, detail, status

    def add(id_, name, type_, layer, rows_checked, failures, detail=""):
        status = "PASS" if failures == 0 else "FAIL"
        results.append(dict(id=id_, name=name, type=type_, layer=layer, rows_checked=int(rows_checked), failures=int(failures), detail=detail, status=status))

    # 1-10 source generic
    extra, dupk = unique_failures(sc, "customer_id"); add(1, "unique_stg_source_customers_customer_id", "generic unique", "Source", len(sc), extra, f"distinct_duplicated_keys={dupk}")
    add(2, "not_null_stg_source_customers_customer_id", "generic not_null", "Source", len(sc), not_null_failures(sc, "customer_id"))
    add(3, "accepted_values_stg_source_customers_segment", "generic accepted_values", "Source", len(sc), accepted_values_failures(sc, "segment", ["Retail","Corporate","Consumer"]))
    extra, dupk = unique_failures(sp, "product_id"); add(4, "unique_stg_source_products_product_id", "generic unique", "Source", len(sp), extra, f"distinct_duplicated_keys={dupk}")
    extra, dupk = unique_failures(so, "order_id"); add(5, "unique_stg_source_orders_order_id", "generic unique", "Source", len(so), extra, f"distinct_duplicated_keys={dupk}")
    add(6, "not_null_stg_source_orders_customer_id", "generic not_null", "Source", len(so), not_null_failures(so, "customer_id"))
    add(7, "relationships_stg_source_orders_customer_id", "generic relationships", "Source", len(so), relationships_failures(so, "customer_id", sc, "customer_id"))
    add(8, "relationships_stg_source_orders_product_id", "generic relationships", "Source", len(so), relationships_failures(so, "product_id", sp, "product_id"))
    extra, dupk = unique_failures(spa, "payment_id"); add(9, "unique_stg_source_payments_payment_id", "generic unique", "Source", len(spa), extra, f"distinct_duplicated_keys={dupk}")
    add(10, "accepted_values_stg_source_payments_payment_method", "generic accepted_values", "Source", len(spa), accepted_values_failures(spa, "payment_method", ["Card","Bank Transfer","Cash","Digital Wallet"]))

    # 11-20 report generic
    extra, dupk = unique_failures(rc, "customer_id"); add(11, "unique_rpt_customers_customer_id", "generic unique", "Report", len(rc), extra, f"distinct_duplicated_keys={dupk}")
    add(12, "not_null_rpt_customers_customer_name", "generic not_null", "Report", len(rc), not_null_failures(rc, "customer_name"))
    extra, dupk = unique_failures(rp, "product_id"); add(13, "unique_rpt_products_product_id", "generic unique", "Report", len(rp), extra, f"distinct_duplicated_keys={dupk}")
    add(14, "not_null_rpt_products_category", "generic not_null", "Report", len(rp), not_null_failures(rp, "category"))
    extra, dupk = unique_failures(ro, "order_id"); add(15, "unique_rpt_orders_order_id", "generic unique", "Report", len(ro), extra, f"distinct_duplicated_keys={dupk}")
    add(16, "not_null_rpt_orders_customer_id", "generic not_null", "Report", len(ro), not_null_failures(ro, "customer_id"))
    add(17, "relationships_rpt_orders_customer_id", "generic relationships", "Report", len(ro), relationships_failures(ro, "customer_id", rc, "customer_id"))
    add(18, "relationships_rpt_orders_product_id", "generic relationships", "Report", len(ro), relationships_failures(ro, "product_id", rp, "product_id"))
    extra, dupk = unique_failures(rpa, "payment_id"); add(19, "unique_rpt_payments_payment_id", "generic unique", "Report", len(rpa), extra, f"distinct_duplicated_keys={dupk}")
    add(20, "not_null_rpt_payments_payment_amount", "generic not_null", "Report", len(rpa), not_null_failures(rpa, "payment_amount"))

    # 21-23 singular out-of-range
    qty_fail = int(((ro["quantity"].isna()) | (ro["quantity"] <= 0)).sum())
    add(21, "assert_report_orders_quantity_positive", "singular", "Report", len(ro), qty_fail, "quantity <= 0 or null")
    amt_fail = int(((ro["order_amount"].isna()) | (ro["order_amount"] < 0)).sum())
    add(22, "assert_report_orders_amount_nonnegative", "singular", "Report", len(ro), amt_fail, "order_amount < 0 or null")
    pay_pos_fail = int(((rpa["payment_amount"].notna()) & (rpa["payment_amount"] <= 0)).sum())
    add(23, "assert_report_payments_amount_positive", "singular", "Report", len(rpa), pay_pos_fail, "payment_amount <= 0 (non-null)")

    # 24-25 reconciliation
    so_total = float(so["order_amount"].sum()); ro_total = float(ro["order_amount"].sum())
    orders_diff = ro_total - so_total
    orders_pct = abs(orders_diff) / so_total * 100 if so_total else 0.0
    orders_fail = 0 if orders_pct <= THRESHOLD_PCT else 1
    results.append(dict(id=24, name="assert_reconciliation_orders_total_within_threshold", type="singular reconciliation", layer="Reconciliation", rows_checked=int(len(so)+len(ro)), failures=int(orders_fail), detail=f"source_total=${so_total:,.2f} report_total=${ro_total:,.2f} diff=${orders_diff:,.2f} diff_pct={orders_pct:.4f}% threshold={THRESHOLD_PCT}%", status="PASS" if orders_fail==0 else "FAIL", diff_pct=orders_pct, source_total=so_total, report_total=ro_total, diff=orders_diff))

    spa_total = float(spa["payment_amount"].sum()); rpa_total = float(pd.to_numeric(rpa["payment_amount"], errors="coerce").sum())
    pay_diff = rpa_total - spa_total
    pay_pct = abs(pay_diff) / spa_total * 100 if spa_total else 0.0
    pay_fail = 0 if pay_pct <= THRESHOLD_PCT else 1
    results.append(dict(id=25, name="assert_reconciliation_payments_total_within_threshold", type="singular reconciliation", layer="Reconciliation", rows_checked=int(len(spa)+len(rpa)), failures=int(pay_fail), detail=f"source_total=${spa_total:,.2f} report_total=${rpa_total:,.2f} diff=${pay_diff:,.2f} diff_pct={pay_pct:.4f}% threshold={THRESHOLD_PCT}%", status="PASS" if pay_fail==0 else "FAIL", diff_pct=pay_pct, source_total=spa_total, report_total=rpa_total, diff=pay_diff))

    assert len(results) == 25, f"Expected 25 tests, got {len(results)}"

    passes = sum(1 for r in results if r["status"] == "PASS")
    fails = sum(1 for r in results if r["status"] == "FAIL")

    # write JSON for pytest
    (OUT / "validation_results.json").write_text(json.dumps(results, indent=2))

    lines = []
    lines.append("# Validation Report — SYNTHETIC DATA")
    lines.append("")
    lines.append("> **SYNTHETIC DATA**: All numbers below are real harness output against synthetic CSVs (seed 42).")
    lines.append("")
    lines.append(f"**Total tests executed: {len(results)}** (20 generic + 5 singular = 25)")
    lines.append(f"**PASS: {passes}** | **FAIL: {fails}**")
    lines.append("")
    lines.append("| # | Test | Type | Layer | Rows checked | Failures | Status | Detail |")
    lines.append("|---|------|------|-------|--------------|----------|--------|--------|")
    for r in results:
        lines.append(f"| {r['id']} | `{r['name']}` | {r['type']} | {r['layer']} | {r['rows_checked']} | {r['failures']} | **{r['status']}** | {r['detail']} |")
    lines.append("")
    lines.append("## Reconciliation detail (threshold 0.01%)")
    for r in results:
        if "diff_pct" in r:
            lines.append(f"- `{r['name']}`: source=${r['source_total']:,.2f} report=${r['report_total']:,.2f} diff=${r['diff']:,.2f} diff_pct={r['diff_pct']:.4f}% => **{r['status']}**")
    lines.append("")
    lines.append("Source layer expectation: all PASS. Report layer expectation: FAIL where defects injected (see docs/injected_defects.md).")
    (OUT / "validation_report.md").write_text("\n".join(lines))
    print(f"Executed {len(results)} tests: PASS={passes} FAIL={fails}")
    for r in results:
        print(f"{r['id']:2d} {r['status']:4s} failures={r['failures']} {r['name']} {r['detail']}")
    return results

if __name__ == "__main__":
    main()
