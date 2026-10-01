-- Test 25: assert_reconciliation_payments_total_within_threshold (SYNTHETIC)
-- Purpose: Power BI report_payments total vs Snowflake source_payments total within 0.01%
-- Expected: flagged FAIL when |diff|/source_total > 0.01%; PASS otherwise
with source_total as (
    select sum(payment_amount) as total from {{ ref('stg_source_payments') }}
),
report_total as (
    select sum(payment_amount) as total from {{ ref('rpt_payments') }}
)
select
    s.total as source_total,
    r.total as report_total,
    abs(r.total - s.total) / nullif(s.total, 0) * 100 as diff_pct
from source_total s, report_total r
where abs(r.total - s.total) / nullif(s.total, 0) * 100 > 0.01
