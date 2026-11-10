WITH first_views AS (
    SELECT
        visitorid,
        itemid,
        MIN(timestamp) AS first_view_ms
    FROM clean_events
    WHERE event = 'view'
    GROUP BY visitorid, itemid
)
SELECT
    v.visitorid,
    v.itemid,
    epoch_ms(v.first_view_ms) AS first_view_time_utc,
    epoch_ms(MIN(c.timestamp)) AS first_cart_time_utc
FROM first_views AS v
LEFT JOIN clean_events AS c
    ON c.visitorid = v.visitorid
    AND c.itemid = v.itemid
    AND c.event = 'addtocart'
    AND c.timestamp > v.first_view_ms
GROUP BY v.visitorid, v.itemid, v.first_view_ms
ORDER BY MIN(c.timestamp) NULLS LAST, v.visitorid, v.itemid
LIMIT 10;