SELECT
    event,
    COUNT(*) AS event_rows,
    COUNT(DISTINCT visitorid) AS visitor_count
FROM clean_events
GROUP BY event
ORDER BY event_rows DESC;