SELECT
    visitorid,
    itemid,
    MIN(timestamp) AS first_view_ms,
    epoch_ms(MIN(timestamp)) AS first_view_time_utc
FROM clean_events
WHERE event = 'view'
GROUP BY
    visitorid,
    itemid
ORDER BY
    visitorid,
    itemid
LIMIT 10;