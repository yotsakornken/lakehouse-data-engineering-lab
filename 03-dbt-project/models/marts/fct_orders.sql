-- Fact table: one row per order with all business metrics

with orders_enriched as (
    select * from {{ ref('int_orders_enriched') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

final as (
    select
        o.order_id,
        o.customer_id,
        c.customer_name,
        c.city as customer_city,
        o.product_name,
        o.product_category,
        o.quantity,
        o.unit_price,
        o.cost_price,
        o.total_revenue,
        o.total_cost,
        o.gross_profit,
        round(o.gross_profit * 1.0 / nullif(o.total_revenue, 0), 4) as profit_margin,
        o.order_date,
        o.status
    from orders_enriched o
    left join customers c on o.customer_id = c.customer_id
    where o.status = 'completed'
)

select * from final
