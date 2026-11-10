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
),
first_purchases AS (
    SELECT
        c.visitorid,
        c.itemid,
        c.first_cart_ms,
        MIN(p.timestamp) AS first_purchase_ms
    FROM first_carts AS c
    LEFT JOIN clean_events AS p
        ON p.visitorid = c.visitorid
        AND p.itemid = c.itemid
        AND p.event = 'transaction'
        AND p.timestamp > c.first_cart_ms
    GROUP BY c.visitorid, c.itemid, c.first_cart_ms
)
SELECT
    COUNT(*) AS viewed_pairs,
    COUNT(first_cart_ms) AS carted_pairs,
    COUNT(first_purchase_ms) AS purchased_pairs,
    ROUND(
        100.0 * COUNT(first_purchase_ms)
        / NULLIF(COUNT(first_cart_ms), 0),
        2
    ) AS cart_to_purchase_pct
FROM first_purchases;