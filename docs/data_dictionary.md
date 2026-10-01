# Data Dictionary — SYNTHETIC DATA

> **SYNTHETIC DATA**: Every table below is synthetic (seed 42). "Source" = Snowflake-style source layer; "Report" = Power BI report layer.

## Overview
Two-layer architecture: Snowflake source (system of record) → Power BI report layer (semantic/report tables). Grain, keys, and reconciliation totals are validated by the 25-test framework.

## source_customers (Snowflake source)
- **Grain**: 1 row per customer
- **Source**: synthetic generator `src/generate_data.py`
- **Rows (seed 42)**: 100

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| customer_id | string (PK) | No | Unique customer key, format CUST-### | CUST-001 |
| customer_name | string | No (source) | Customer display name | Customer 001 |
| email | string | Yes | Synthetic email | customer001@example.com |
| segment | string | No | One of Retail / Corporate / Consumer | Retail |
| region | string | Yes | North/South/East/West/Central | North |
| created_date | date | Yes | Account creation date | 2023-01-15 |

## source_products
- **Grain**: 1 row per product | **Rows**: 20

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| product_id | string (PK) | No | PROD-## |
| product_name | string | No | Product ## |
| category | string | No | Electronics/Furniture/Clothing/Food/Office Supplies |
| unit_price | decimal(10,2) | No | List price USD |

## source_orders
- **Grain**: 1 row per order | **Rows**: 500

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| order_id | string (PK) | No | ORD-#### |
| customer_id | string (FK → source_customers) | No | Buyer |
| product_id | string (FK → source_products) | No | Purchased product |
| order_date | date | No | 2025 order date |
| quantity | int | No | Units, expected > 0 |
| order_amount | decimal(12,2) | No | quantity × unit_price |

## source_payments
- **Grain**: 1 row per payment | **Rows**: 500

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| payment_id | string (PK) | No | PAY-#### |
| order_id | string (FK → source_orders) | No | Paid order |
| payment_date | date | Yes | order_date + 0–5 days |
| payment_amount | decimal(12,2) | No | Equals order_amount in source |
| payment_method | string | No | Card / Bank Transfer / Cash / Digital Wallet |

## report_customers (Power BI report layer)
- **Grain (intended)**: 1 row per customer | **Rows (with defects)**: 102
- Same columns as source_customers. Defects: 3 null customer_name, 2 duplicate customer_id extra rows. See `docs/injected_defects.md`.

## report_products
- **Grain (intended)**: 1 row per product | **Rows**: 21
- Same columns as source_products. Defects: 2 null category, 1 duplicate product_id.

## report_orders
- **Grain (intended)**: 1 row per order | **Rows**: 504
- Same columns as source_orders. Defects: 5 null customer_id, 3 orphan customer_id, 2 orphan product_id, 4 quantity ≤0, 3 negative order_amount, 4 duplicate order_id, 8 drift-inflated amounts (+$800).

## report_payments
- **Grain (intended)**: 1 row per payment | **Rows**: 502
- Same columns as source_payments. Defects: 3 null payment_amount, 2 orphan order_id, 2 negative payment_amount, 2 duplicate payment_id.

## Reconciliation totals (seed-42 ground truth)
- source_orders_total $655,327.30 vs report_orders_total $656,082.32 (diff $755.02, 0.1152%)
- source_payments_total $655,327.30 vs report_payments_total $655,282.36 (diff -$44.94, 0.0069%)
- Threshold: 0.01% (see test 24–25)
