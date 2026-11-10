WITH first_views AS (
    SELECT
        visitorid,
        itemid,
        MIN(timestamp) AS first_view_ms
    FROM clean_events
    WHERE event = 'view'
    GROUP BY visitorid, itemid
    HAVING MIN(timestamp) + 604800000 <= (
        SELECT MAX(timestamp) FROM clean_events
    )
),
first_carts AS (
    SELECT
        v.visitorid,
        v.itemid,
        v.first_view_ms,
        MIN(c.timestamp) AS first_cart_ms
    FROM first_views AS v
    LEFT JOIN clean_events AS c
        ON c.visitorid = v.visitorid
        AND c.itemid = v.itemid
        AND c.event = 'addtocart'
        AND c.timestamp > v.first_view_ms
        AND c.timestamp <= v.first_view_ms + 604800000
    GROUP BY v.visitorid, v.itemid, v.first_view_ms
),
first_purchases AS (
    SELECT
        c.visitorid,
        c.itemid,
        c.first_view_ms,
        c.first_cart_ms,
        MIN(p.timestamp) AS first_purchase_ms
    FROM first_carts AS c
    LEFT JOIN clean_events AS p
        ON p.visitorid = c.visitorid
        AND p.itemid = c.itemid
        AND p.event = 'transaction'
        AND p.timestamp > c.first_cart_ms
        AND p.timestamp <= c.first_view_ms + 604800000
    GROUP BY c.visitorid, c.itemid, c.first_view_ms, c.first_cart_ms
),
grouped_pairs AS (
    SELECT
        CASE
            WHEN EXTRACT(ISODOW FROM epoch_ms(first_view_ms)) IN (6, 7)
                THEN 'weekend'
            ELSE 'weekday'
        END AS first_view_day_type,
        first_cart_ms - first_view_ms AS cart_delay_ms,
        first_purchase_ms - first_view_ms AS purchase_delay_ms
    FROM first_purchases
)
SELECT
    first_view_day_type,
    COUNT(*) AS viewed_pairs,
    COUNT(*) FILTER (WHERE cart_delay_ms <= 86400000) AS carted_pairs_24h,
    COUNT(*) FILTER (WHERE purchase_delay_ms <= 86400000) AS purchased_pairs_24h,
     ROUND(
        100.0 * COUNT(*) FILTER (WHERE cart_delay_ms <= 86400000)
        / NULLIF(COUNT(*), 0),
        2
    ) AS view_to_cart_pct_24h,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE purchase_delay_ms <= 86400000)
        / NULLIF(COUNT(*) FILTER (WHERE cart_delay_ms <= 86400000), 0),
        2
    ) AS cart_to_purchase_pct_24h,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE purchase_delay_ms <= 86400000)
        / NULLIF(COUNT(*), 0),
        2
    ) AS view_to_purchase_pct_24h
FROM grouped_pairs
GROUP BY first_view_day_type
ORDER BY first_view_day_type;
