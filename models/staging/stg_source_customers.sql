-- SYNTHETIC DATA: staging model over source_customers.csv (Snowflake-style source)
select
    customer_id,
    customer_name,
    email,
    segment,
    region,
    created_date
from {{ source('snowflake_source', 'source_customers') }}
