CREATE OR REPLACE FUNCTION dds.fn_fact_artist()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

    TRUNCATE TABLE dds.t_dim_artist;
    
    INSERT INTO dds.t_dim_artist (
		artist_id,
		"name",
        created_at
    )
    SELECT
		artist_id,
		name,
        NOW() AS created_at
    FROM
    	stage.artist al
    ORDER BY
        artist_id;

    ANALYZE dds.t_dim_artist;

END $$;