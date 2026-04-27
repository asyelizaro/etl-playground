CREATE OR REPLACE FUNCTION dds.fn_dim_customer()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO dds.dim_customer (
        customer_id,
        first_name,
        last_name,
        company,
        address,
        city,
        "state",
        country,
        postal_code,
        phone,
        fax,
        email,
        support_rep_id,
        created_at
    )
    SELECT
        c.customer_id,
        c.first_name,
        c.last_name,
        c.company,
        c.address,
        c.city,
        c.state,
        c.country,
        c.postal_code,
        c.phone,
        c.fax,
        c.email,
        c.support_rep_id,
        NOW() AS created_at
    FROM
        stage.customer c
    ORDER BY
        c.customer_id;

END $$;