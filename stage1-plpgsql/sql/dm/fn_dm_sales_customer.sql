CREATE OR REPLACE FUNCTION data_mart.fn_dm_sales_customer()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO data_mart.t_dm_sales_customer (
        customer_id,
        full_name,
        country,
        first_purchase,
        last_purchase,
        revenue,
        quanity
    )
    SELECT
        customer_id,
        full_name,
        country,
        first_purchase,
        last_purchase,
        SUM(total_amount) AS revenue,
        SUM(quantity) AS quanity
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
        FROM dds.fact_sales AS fct
        JOIN dds.dim_customer AS c
            ON c.customer_id = fct.customer_id
    ) AS t 
    GROUP BY
        1,2,3,4,5;

    ANALYZE data_mart.t_dm_sales_customer;

END $$;