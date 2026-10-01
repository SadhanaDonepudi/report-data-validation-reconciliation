-- Test 22: assert_report_orders_amount_nonnegative (SYNTHETIC)
-- Purpose: out-of-range detection - order_amount must be >= 0
-- Expected: FAIL when negative amounts exist (injected: 3)
select order_id, order_amount
from {{ ref('rpt_orders') }}
where order_amount is null or order_amount < 0
