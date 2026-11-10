CREATE OR REPLACE TABLE aa_assignments AS
SELECT
    *,
    CASE
        WHEN substr(
            md5('aa_demo_v1|' || CAST(visitorid AS VARCHAR)),
            1,
            1
        ) IN ('0', '1', '2', '3', '4', '5', '6', '7')
            THEN 'A'
        ELSE 'B'
    END AS experiment_group
FROM aa_user_outcomes;

SELECT
    experiment_group,
    COUNT(*) AS users,
    SUM(purchased_24h) AS purchasers_24h,
    ROUND(100.0 * AVG(purchased_24h), 2) AS purchase_rate_pct
FROM aa_assignments
GROUP BY experiment_group
ORDER BY experiment_group;