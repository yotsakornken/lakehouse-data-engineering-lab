-- Staging model: clean raw customers

with source as (
    select * from {{ ref('raw_customers') }}
),

renamed as (
    select
        customer_id,
        name as customer_name,
        lower(trim(email)) as email,
        coalesce(city, 'Unknown') as city,
        cast(registered_date as date) as registered_date
    from source
)

select * from renamed
