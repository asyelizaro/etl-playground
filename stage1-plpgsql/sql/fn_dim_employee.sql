CREATE OR REPLACE FUNCTION dds.fn_dim_employee()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO dds.dim_employee (
        employee_id,
        last_name,
        first_name,
        title,
        reports_to,
        birth_date,
        hire_date,
        address,
        city,
        "state",
        country,
        postal_code,
        phone,
        fax,
        email,
        created_at
    )
    SELECT
        e.employee_id,
        e.last_name,
        e.first_name,
        e.title,
        e.reports_to,
        e.birth_date,
        e.hire_date,
        e.address,
        e.city,
        e.state,
        e.country,
        e.postal_code,
        e.phone,
        e.fax,
        e.email,
        NOW() AS created_at
    FROM
        stage.employee e
    ORDER BY
        e.employee_id;

END $$;