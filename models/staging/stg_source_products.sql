-- SYNTHETIC DATA
select product_id, product_name, category, unit_price
from {{ source('snowflake_source', 'source_products') }}
