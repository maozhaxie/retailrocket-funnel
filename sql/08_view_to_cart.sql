WITH first_views AS (
    SELECT
        visitorid,
        itemid,
        MIN(timestamp) AS first_view_ms
    FROM clean_events
    WHERE event = 'view'
    GROUP BY visitorid, itemid
),
first_carts AS (
    SELECT
        v.visitorid,
        v.itemid,
        MIN(c.timestamp) AS first_cart_ms
    FROM first_views AS v
    LEFT JOIN clean_events AS c
        ON c.visitorid = v.visitorid
        AND c.itemid = v.itemid
        AND c.event = 'addtocart'
        AND c.timestamp > v.first_view_ms
    GROUP BY v.visitorid, v.itemid
)
SELECT
    COUNT(*) AS viewed_pairs,
    COUNT(first_cart_ms) AS carted_pairs,
    ROUND(
        100.0 * COUNT(first_cart_ms) / NULLIF(COUNT(*), 0),
        2
    ) AS view_to_cart_pct
FROM first_carts;