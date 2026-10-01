-- SYNTHETIC DATA: Power BI report-layer orders
select order_id, customer_id, product_id, order_date, quantity, order_amount
from {{ source('powerbi_report', 'report_orders') }}
