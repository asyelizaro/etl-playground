CREATE OR REPLACE FUNCTION dds.fn_dim_date()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO dds.dim_date (
        date_key,
        "date",
        day,
        month,
        quarter,
        year,
        day_of_week,
        day_name,
        month_name,
        created_at
    )
    SELECT
        TO_CHAR(d::DATE, 'YYYYMMDD')::INTEGER AS date_key,
        d::DATE,
        EXTRACT(DAY FROM d)::INTEGER AS day,
        EXTRACT(MONTH FROM d)::INTEGER AS month,
        EXTRACT(QUARTER FROM d)::INTEGER AS quarter,
        EXTRACT(YEAR FROM d)::INTEGER AS year,
        EXTRACT(DOW FROM d)::INTEGER AS day_of_week,
        TO_CHAR(d::DATE, 'Day') AS day_name,
        TO_CHAR(d::DATE, 'Month') AS month_name,
        NOW() AS created_at
    FROM
        (
            SELECT
                generate_series(
                    '2009-01-01'::DATE,
                    '2050-12-31'::DATE,
                    '1 day'::INTERVAL
                )::TIMESTAMP d
        ) x
    ORDER BY
        d::DATE;

END $$;