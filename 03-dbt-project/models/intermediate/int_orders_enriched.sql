-- Intermediate: enrich orders with product details and calculate amounts

with orders as (
    select * from {{ ref('stg_orders') }}
),

products as (
    select * from {{ ref('stg_products') }}
),

enriched as (
    select
        o.order_id,
        o.customer_id,
        o.product_name,
        p.category as product_category,
        o.quantity,
        o.unit_price,
        p.cost_price,
        o.quantity * o.unit_price as total_revenue,
        o.quantity * p.cost_price as total_cost,
        (o.quantity * o.unit_price) - (o.quantity * p.cost_price) as gross_profit,
        o.order_date,
        o.status
    from orders o
    left join products p on o.product_name = p.product_name
)

select * from enriched
