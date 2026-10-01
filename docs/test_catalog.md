# Test Catalog — Exactly 25 Data Tests (SYNTHETIC DATA)

> **SYNTHETIC DATA**: All tests run against synthetic CSVs. Count is programmatic: 20 dbt generic tests in `models/schema.yml` + 5 singular tests in `tests/*.sql` = **25**.

| # | Test name | Type | Layer / Table.Column | Purpose | Expected behavior |
|---|-----------|------|----------------------|---------|-------------------|
| 1 | unique_stg_source_customers_customer_id | generic unique | Source / source_customers.customer_id | Grain check: one row per customer in Snowflake source | PASS (source clean) |
| 2 | not_null_stg_source_customers_customer_id | generic not_null | Source / source_customers.customer_id | Null detection on PK | PASS |
| 3 | accepted_values_stg_source_customers_segment | generic accepted_values | Source / source_customers.segment | Domain check: Retail/Corporate/Consumer | PASS |
| 4 | unique_stg_source_products_product_id | generic unique | Source / source_products.product_id | Grain check: one row per product | PASS |
| 5 | unique_stg_source_orders_order_id | generic unique | Source / source_orders.order_id | Grain check: one row per order | PASS |
| 6 | not_null_stg_source_orders_customer_id | generic not_null | Source / source_orders.customer_id | Null FK detection | PASS |
| 7 | relationships_stg_source_orders_customer_id | generic relationships | Source / source_orders.customer_id → customers | Orphan FK detection | PASS |
| 8 | relationships_stg_source_orders_product_id | generic relationships | Source / source_orders.product_id → products | Orphan FK detection | PASS |
| 9 | unique_stg_source_payments_payment_id | generic unique | Source / source_payments.payment_id | Grain check: one row per payment | PASS |
| 10 | accepted_values_stg_source_payments_payment_method | generic accepted_values | Source / source_payments.payment_method | Domain check: Card/Bank Transfer/Cash/Digital Wallet | PASS |
| 11 | unique_rpt_customers_customer_id | generic unique | Report / report_customers.customer_id | Grain / duplicate detection (Power BI layer) | FAIL — 2 extra duplicate rows injected |
| 12 | not_null_rpt_customers_customer_name | generic not_null | Report / report_customers.customer_name | Null detection | FAIL — 3 nulls injected |
| 13 | unique_rpt_products_product_id | generic unique | Report / report_products.product_id | Grain / duplicate detection | FAIL — 1 extra duplicate injected |
| 14 | not_null_rpt_products_category | generic not_null | Report / report_products.category | Null detection | FAIL — 2 nulls injected |
| 15 | unique_rpt_orders_order_id | generic unique | Report / report_orders.order_id | Grain / duplicate detection | FAIL — 4 extra duplicates injected |
| 16 | not_null_rpt_orders_customer_id | generic not_null | Report / report_orders.customer_id | Null FK detection | FAIL — 5 nulls injected |
| 17 | relationships_rpt_orders_customer_id | generic relationships | Report / report_orders.customer_id → report_customers | Orphan FK detection | FAIL — 3 orphans injected |
| 18 | relationships_rpt_orders_product_id | generic relationships | Report / report_orders.product_id → report_products | Orphan FK detection | FAIL — 2 orphans injected |
| 19 | unique_rpt_payments_payment_id | generic unique | Report / report_payments.payment_id | Grain / duplicate detection | FAIL — 2 extra duplicates injected |
| 20 | not_null_rpt_payments_payment_amount | generic not_null | Report / report_payments.payment_amount | Null detection | FAIL — 3 nulls injected |
| 21 | assert_report_orders_quantity_positive | singular SQL | Report / report_orders.quantity | Out-of-range: quantity > 0 | FAIL — 4 rows <=0 injected |
| 22 | assert_report_orders_amount_nonnegative | singular SQL | Report / report_orders.order_amount | Out-of-range: amount >= 0 | FAIL — 3 negative injected |
| 23 | assert_report_payments_amount_positive | singular SQL | Report / report_payments.payment_amount | Out-of-range: payment_amount > 0 when present | FAIL — 2 negative injected |
| 24 | assert_reconciliation_orders_total_within_threshold | singular SQL | Reconciliation / orders total | Power BI vs Snowflake totals within 0.01% | FAIL — injected drift 0.1152% > 0.01% |
| 25 | assert_reconciliation_payments_total_within_threshold | singular SQL | Reconciliation / payments total | Power BI vs Snowflake totals within 0.01% | PASS/FAIL per actual diff (0.0069% in seed-42 run => PASS, correctly under threshold) |

## Counting proof
- Generic tests counted from `models/schema.yml`: **20**
- Singular tests counted from `tests/*.sql`: **5**
- **Total: 25** — verified programmatically in `src/run_validations.py` and README.
