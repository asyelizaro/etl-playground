CREATE OR REPLACE FUNCTION data_mart.fn_dm_sales_by_employee()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

    TRUNCATE TABLE data_mart.t_dm_sales_by_employee;
    
    WITH sales_by_employee AS (
        SELECT
            employee_id,
            COUNT(sale_id) AS purchase_count,
            SUM(total_amount) AS revenue_amount
        FROM
            dds.t_fact_sales
        GROUP BY
            employee_id
    ),
    clients_by_employee AS (
        SELECT
            support_rep_id AS employee_id,
            COUNT(DISTINCT customer_id) AS clients_count
        FROM
            dds.t_dim_customer
        GROUP BY
            support_rep_id
    )
    INSERT INTO data_mart.t_dm_sales_by_employee (
        employee_id,
        full_name,
        clients_count,
        purchase_count,
        revenue_amount
    )
    SELECT
        sales.employee_id,
        e.last_name || ' ' || e.first_name AS full_name,
        COALESCE(clients.clients_count, 0) AS clients_count,
        sales.purchase_count,
        sales.revenue_amount
    FROM
        sales_by_employee AS sales
        JOIN dds.t_dim_employee AS e
            ON e.employee_id = sales.employee_id
        LEFT JOIN clients_by_employee AS clients
            ON clients.employee_id = sales.employee_id;

    ANALYZE data_mart.t_dm_sales_by_employee;

END $$;