-- Test 23: assert_report_payments_amount_positive (SYNTHETIC)
-- Purpose: out-of-range detection - payment_amount must be > 0 when present
-- Expected: FAIL when negative amounts exist (injected: 2)
select payment_id, payment_amount
from {{ ref('rpt_payments') }}
where payment_amount is not null and payment_amount <= 0
