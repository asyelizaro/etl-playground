CREATE OR REPLACE FUNCTION dds.fn_dim_genre()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO dds.t_dim_genre (
        genre_id,
        "name",
        created_at
    )
    SELECT
        genre_id,
        name,
        NOW() AS created_at
    FROM
        stage.genre g
    ORDER BY
        genre_id;

    ANALYZE dds.t_dim_genre;

END $$;