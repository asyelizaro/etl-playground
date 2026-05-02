CREATE OR REPLACE FUNCTION data_mart.fn_dm_sales_by_employee()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO data_mart.t_dm_sales_by_employee (
        employee_id,
        full_name,
        clients_count,
        purchase_count,
        revenue_amount
    )
    SELECT
        fct.employee_id,
        e.last_name || ' ' || e.first_name AS full_name,
        COUNT(DISTINCT c.customer_id) AS clients_count,
        COUNT(fct.sale_id) AS purchase_count,
        SUM(fct.total_amount) AS revenue_amount
    FROM
        dds.t_fact_sales AS fct
        JOIN dds.t_dim_employee AS e
            ON e.employee_id = fct.employee_id
        LEFT JOIN dds.t_dim_customer AS c
            ON c.support_rep_id = e.employee_id
    GROUP BY
        1, 2;

    ANALYZE data_mart.t_dm_sales_by_employee;

END $$;