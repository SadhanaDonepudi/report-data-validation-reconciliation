-- Test 21: assert_report_orders_quantity_positive (SYNTHETIC)
-- Purpose: out-of-range detection - quantity must be > 0 in report_orders
-- Expected: FAIL when quantity <= 0 rows exist (injected: 4)
select order_id, quantity
from {{ ref('rpt_orders') }}
where quantity is null or quantity <= 0
