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
time_windows (window_label, window_ms) AS (
    VALUES ('1h', 3600000), ('24h', 86400000), ('7d', 604800000)
)
SELECT
    w.window_label,
    COUNT(*) AS viewed_pairs,
    COUNT(*) FILTER (
        WHERE f.first_cart_ms - f.first_view_ms <= w.window_ms
    ) AS carted_pairs,
    COUNT(*) FILTER (
        WHERE f.first_purchase_ms - f.first_view_ms <= w.window_ms
    ) AS purchased_pairs,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE f.first_purchase_ms - f.first_view_ms <= w.window_ms
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS view_to_purchase_pct
FROM first_purchases AS f
CROSS JOIN time_windows AS w
GROUP BY w.window_label, w.window_ms
ORDER BY w.window_ms;