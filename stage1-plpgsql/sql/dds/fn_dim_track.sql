CREATE OR REPLACE FUNCTION dds.fn_dim_track()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO dds.t_dim_track (
        track_id,
        "name",
        album_id,
        genre_id,
        media_type_id,
        composer,
        milliseconds,
        "bytes",
        unit_price,
        created_at
    )
    SELECT
        t.track_id,
        t.name,
        t.album_id,
        t.genre_id,
        t.media_type_id,
        t.composer,
        t.milliseconds,
        t."bytes",
        t.unit_price,
        NOW() AS created_at
    FROM
        stage.track t
    ORDER BY
        t.album_id, t.track_id;

    ANALYZE dds.t_dim_track;
    
END $$;