CREATE OR REPLACE FUNCTION data_mart.fn_dm_sales_by_artist()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO data_mart.t_dm_sales_by_artist (
        invoice_date,
        artist_name,
        genre_name,
        avg_price_track,
        revenue,
        quantity
    )
    SELECT
        fct.invoice_date,
        fct.artist_id,
        g.name AS genre_name,
        AVG(fct.unit_price) AS avg_price_track,
        SUM(fct.total_amount) AS revenue,
        SUM(fct.quantity) AS quantity
    FROM
        dds.fact_sales AS fct
    JOIN dds.dim_track AS t
        ON t.track_id = fct.track_id
    JOIN dds.dim_genre AS g
        ON g.genre_id = t.genre_id
    JOIN dds.dim_artist AS a
        ON a.artist_id = fct.artist_id
    GROUP BY
        1, 2, 3;

    ANALYZE data_mart.t_dm_sales_by_artist;

END $$;