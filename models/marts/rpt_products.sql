-- SYNTHETIC DATA: Power BI report-layer products
select product_id, product_name, category, unit_price
from {{ source('powerbi_report', 'report_products') }}
