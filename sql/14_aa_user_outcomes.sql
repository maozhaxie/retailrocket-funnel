CREATE OR REPLACE TABLE aa_user_outcomes AS
WITH first_views AS (
    SELECT
        visitorid,
        MIN(timestamp) AS first_view_ms
    FROM clean_events
    WHERE event = 'view'
    GROUP BY visitorid
    HAVING MIN(timestamp) + 86400000 <= (
        SELECT MAX(timestamp) FROM clean_events
    )
)
SELECT
    v.visitorid,
    v.first_view_ms,
    MIN(p.timestamp) AS first_purchase_ms,
    CASE
        WHEN MIN(p.timestamp) IS NOT NULL THEN 1
        ELSE 0
    END AS purchased_24h
FROM first_views AS v
LEFT JOIN clean_events AS p
    ON p.visitorid = v.visitorid
    AND p.event = 'transaction'
    AND p.timestamp > v.first_view_ms
    AND p.timestamp <= v.first_view_ms + 86400000
GROUP BY v.visitorid, v.first_view_ms;

SELECT
    COUNT(*) AS total_users,
    COUNT(DISTINCT visitorid) AS unique_users,
    SUM(purchased_24h) AS purchasers_24h,
    ROUND(100.0 * AVG(purchased_24h), 2) AS purchase_rate_pct
FROM aa_user_outcomes;