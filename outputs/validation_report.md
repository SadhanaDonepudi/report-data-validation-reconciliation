# Validation Report — SYNTHETIC DATA

> **SYNTHETIC DATA**: All numbers below are real harness output against synthetic CSVs (seed 42).

**Total tests executed: 25** (20 generic + 5 singular = 25)
**PASS: 11** | **FAIL: 14**

| # | Test | Type | Layer | Rows checked | Failures | Status | Detail |
|---|------|------|-------|--------------|----------|--------|--------|
| 1 | `unique_stg_source_customers_customer_id` | generic unique | Source | 100 | 0 | **PASS** | distinct_duplicated_keys=0 |
| 2 | `not_null_stg_source_customers_customer_id` | generic not_null | Source | 100 | 0 | **PASS** |  |
| 3 | `accepted_values_stg_source_customers_segment` | generic accepted_values | Source | 100 | 0 | **PASS** |  |
| 4 | `unique_stg_source_products_product_id` | generic unique | Source | 20 | 0 | **PASS** | distinct_duplicated_keys=0 |
| 5 | `unique_stg_source_orders_order_id` | generic unique | Source | 500 | 0 | **PASS** | distinct_duplicated_keys=0 |
| 6 | `not_null_stg_source_orders_customer_id` | generic not_null | Source | 500 | 0 | **PASS** |  |
| 7 | `relationships_stg_source_orders_customer_id` | generic relationships | Source | 500 | 0 | **PASS** |  |
| 8 | `relationships_stg_source_orders_product_id` | generic relationships | Source | 500 | 0 | **PASS** |  |
| 9 | `unique_stg_source_payments_payment_id` | generic unique | Source | 500 | 0 | **PASS** | distinct_duplicated_keys=0 |
| 10 | `accepted_values_stg_source_payments_payment_method` | generic accepted_values | Source | 500 | 0 | **PASS** |  |
| 11 | `unique_rpt_customers_customer_id` | generic unique | Report | 102 | 2 | **FAIL** | distinct_duplicated_keys=2 |
| 12 | `not_null_rpt_customers_customer_name` | generic not_null | Report | 102 | 3 | **FAIL** |  |
| 13 | `unique_rpt_products_product_id` | generic unique | Report | 21 | 1 | **FAIL** | distinct_duplicated_keys=1 |
| 14 | `not_null_rpt_products_category` | generic not_null | Report | 21 | 2 | **FAIL** |  |
| 15 | `unique_rpt_orders_order_id` | generic unique | Report | 504 | 4 | **FAIL** | distinct_duplicated_keys=4 |
| 16 | `not_null_rpt_orders_customer_id` | generic not_null | Report | 504 | 5 | **FAIL** |  |
| 17 | `relationships_rpt_orders_customer_id` | generic relationships | Report | 504 | 3 | **FAIL** |  |
| 18 | `relationships_rpt_orders_product_id` | generic relationships | Report | 504 | 2 | **FAIL** |  |
| 19 | `unique_rpt_payments_payment_id` | generic unique | Report | 502 | 2 | **FAIL** | distinct_duplicated_keys=2 |
| 20 | `not_null_rpt_payments_payment_amount` | generic not_null | Report | 502 | 3 | **FAIL** |  |
| 21 | `assert_report_orders_quantity_positive` | singular | Report | 504 | 4 | **FAIL** | quantity <= 0 or null |
| 22 | `assert_report_orders_amount_nonnegative` | singular | Report | 504 | 3 | **FAIL** | order_amount < 0 or null |
| 23 | `assert_report_payments_amount_positive` | singular | Report | 502 | 2 | **FAIL** | payment_amount <= 0 (non-null) |
| 24 | `assert_reconciliation_orders_total_within_threshold` | singular reconciliation | Reconciliation | 1004 | 1 | **FAIL** | source_total=$655,327.30 report_total=$656,082.32 diff=$755.02 diff_pct=0.1152% threshold=0.01% |
| 25 | `assert_reconciliation_payments_total_within_threshold` | singular reconciliation | Reconciliation | 1002 | 0 | **PASS** | source_total=$655,327.30 report_total=$655,282.36 diff=$-44.94 diff_pct=0.0069% threshold=0.01% |

## Reconciliation detail (threshold 0.01%)
- `assert_reconciliation_orders_total_within_threshold`: source=$655,327.30 report=$656,082.32 diff=$755.02 diff_pct=0.1152% => **FAIL**
- `assert_reconciliation_payments_total_within_threshold`: source=$655,327.30 report=$655,282.36 diff=$-44.94 diff_pct=0.0069% => **PASS**

Source layer expectation: all PASS. Report layer expectation: FAIL where defects injected (see docs/injected_defects.md).