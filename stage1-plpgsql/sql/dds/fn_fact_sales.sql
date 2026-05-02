CREATE OR REPLACE FUNCTION dds.fn_fact_sales()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO dds.t_fact_sales (
        sale_id,
        invoice_id,
        employee_id,
        customer_id,
        track_id,
        artist_id,
        album_id,
        invoice_date,
        unit_price,
        quantity,
        total_amount,
        created_at
    )
    SELECT
        il.invoice_line_id AS sale_id,
        i.invoice_id,
        c.support_rep_id AS employee_id,
        i.customer_id,
        il.track_id,
        al.artist_id,
        t.album_id,
        i.invoice_date::DATE AS invoice_date,
        il.unit_price,
        il.quantity,
        il.unit_price * il.quantity AS total_amount,
        NOW() AS created_at
    FROM
        stage.invoice_line il
    JOIN stage.invoice i ON i.invoice_id = il.invoice_id
    JOIN stage.track t ON t.track_id = il.track_id
    JOIN stage.album al ON al.album_id = t.album_id
    JOIN stage.customer c ON c.customer_id = i.customer_id;

    ANALYZE dds.t_fact_sales;
    
END $$;