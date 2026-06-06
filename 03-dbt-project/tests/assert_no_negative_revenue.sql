-- Custom singular test: ensure no orders have negative revenue
-- A test passes if it returns ZERO rows

select
    order_id,
    total_revenue
from {{ ref('fct_orders') }}
where total_revenue < 0
