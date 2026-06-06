-- Dimension table: customer with order metrics

with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('int_orders_enriched') }}
    where status = 'completed'
),

customer_metrics as (
    select
        customer_id,
        count(distinct order_id) as total_orders,
        sum(total_revenue) as lifetime_revenue,
        sum(gross_profit) as lifetime_profit,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date
    from orders
    group by customer_id
),

final as (
    select
        c.customer_id,
        c.customer_name,
        c.email,
        c.city,
        c.registered_date,
        coalesce(m.total_orders, 0) as total_orders,
        coalesce(m.lifetime_revenue, 0) as lifetime_revenue,
        coalesce(m.lifetime_profit, 0) as lifetime_profit,
        m.first_order_date,
        m.last_order_date,
        case
            when m.lifetime_revenue > 50000 then 'gold'
            when m.lifetime_revenue > 20000 then 'silver'
            else 'bronze'
        end as customer_tier
    from customers c
    left join customer_metrics m on c.customer_id = m.customer_id
)

select * from final
