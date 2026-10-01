-- Test 24: assert_reconciliation_orders_total_within_threshold (SYNTHETIC)
-- Purpose: Power BI report_orders total vs Snowflake source_orders total within 0.01%
-- Expected: FAIL when |diff|/source_total > 0.01% (injected drift makes this FAIL)
with source_total as (
    select sum(order_amount) as total from {{ ref('stg_source_orders') }}
),
report_total as (
    select sum(order_amount) as total from {{ ref('rpt_orders') }}
)
select
    s.total as source_total,
    r.total as report_total,
    abs(r.total - s.total) / nullif(s.total, 0) * 100 as diff_pct
from source_total s, report_total r
where abs(r.total - s.total) / nullif(s.total, 0) * 100 > 0.01
