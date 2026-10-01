-- SYNTHETIC DATA
select payment_id, order_id, payment_date, payment_amount, payment_method
from {{ source('snowflake_source', 'source_payments') }}
