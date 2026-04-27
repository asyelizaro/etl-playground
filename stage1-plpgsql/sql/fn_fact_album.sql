CREATE OR REPLACE FUNCTION dds.fn_fact_album()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO dds.dim_album (
        album_id,
		title,
		artist_id,
        created_at
    )
    SELECT
		album_id,
		title,
		artist_id,
        NOW() AS created_at
    FROM
    	stage.album al 
    ORDER BY
        album_id;

END $$;