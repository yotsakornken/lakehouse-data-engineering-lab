-- Staging model: clean raw products

with source as (
    select * from {{ ref('raw_products') }}
),

renamed as (
    select
        product_name,
        lower(trim(category)) as category,
        cost_price
    from source
)

select * from renamed
