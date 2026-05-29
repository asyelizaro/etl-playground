CREATE OR REPLACE FUNCTION data_mart.fn_dm_sales_customer()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

    TRUNCATE TABLE data_mart.t_dm_sales_customers;
    
    INSERT INTO data_mart.t_dm_sales_customers (
        customer_id,
        full_name,
        country,
        first_purchase,
        last_purchase,
        revenue,
        quantity
    )
    SELECT
        customer_id,
        full_name,
        country,
        first_purchase,
        last_purchase,
        SUM(total_amount) AS revenue,
        SUM(quantity) AS quantity
    FROM (
        SELECT
            fct.customer_id,
            first_name || ' ' || last_name AS full_name,
            country,
            invoice_date,
            MIN(invoice_date) OVER (PARTITION BY fct.customer_id) AS first_purchase,
            MAX(invoice_date) OVER (PARTITION BY fct.customer_id) AS last_purchase,
            total_amount,
            quantity
        FROM dds.t_fact_sales AS fct
        JOIN dds.t_dim_customer AS c
            ON c.customer_id = fct.customer_id
    ) AS t 
    GROUP BY
        1,2,3,4,5;

    ANALYZE data_mart.t_dm_sales_customers;

END $$;