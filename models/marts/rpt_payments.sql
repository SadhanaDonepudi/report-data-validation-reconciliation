-- SYNTHETIC DATA: Power BI report-layer payments
select payment_id, order_id, payment_date, payment_amount, payment_method
from {{ source('powerbi_report', 'report_payments') }}
