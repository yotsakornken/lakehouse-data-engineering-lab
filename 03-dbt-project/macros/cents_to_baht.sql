-- Custom macro: format currency display
{% macro format_baht(column_name) %}
    '฿' || cast({{ column_name }} as varchar)
{% endmacro %}
