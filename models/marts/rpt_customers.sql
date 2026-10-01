-- SYNTHETIC DATA: Power BI report-layer customers
select customer_id, customer_name, email, segment, region, created_date
from {{ source('powerbi_report', 'report_customers') }}
