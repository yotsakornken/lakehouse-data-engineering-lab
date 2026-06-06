-- Staging model: clean raw orders
-- Follows dbt convention: stg_<source>_<entity>

with source as (
    select * from {{ ref('raw_orders') }}
),

renamed as (
    select
        order_id,
        customer_id,
        product as product_name,
        quantity,
        unit_price,
        cast(order_date as date) as order_date,
        lower(trim(status)) as status
    from source
)

select * from renamed
