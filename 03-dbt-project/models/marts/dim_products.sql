-- Dimension table: product performance metrics

with products as (
    select * from {{ ref('stg_products') }}
),

orders as (
    select * from {{ ref('int_orders_enriched') }}
    where status = 'completed'
),

product_metrics as (
    select
        product_name,
        count(distinct order_id) as times_ordered,
        sum(quantity) as total_units_sold,
        sum(total_revenue) as total_revenue,
        sum(gross_profit) as total_profit,
        avg(gross_profit * 1.0 / nullif(total_revenue, 0)) as avg_profit_margin
    from orders
    group by product_name
),

final as (
    select
        p.product_name,
        p.category,
        p.cost_price,
        coalesce(m.times_ordered, 0) as times_ordered,
        coalesce(m.total_units_sold, 0) as total_units_sold,
        coalesce(m.total_revenue, 0) as total_revenue,
        coalesce(m.total_profit, 0) as total_profit,
        m.avg_profit_margin,
        rank() over (order by coalesce(m.total_revenue, 0) desc) as revenue_rank
    from products p
    left join product_metrics m on p.product_name = m.product_name
)

select * from final
