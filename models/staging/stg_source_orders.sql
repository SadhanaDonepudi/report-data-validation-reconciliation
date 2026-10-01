-- SYNTHETIC DATA
select order_id, customer_id, product_id, order_date, quantity, order_amount
from {{ source('snowflake_source', 'source_orders') }}
