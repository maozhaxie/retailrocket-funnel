WITH duplicate_groups AS (
    SELECT
        timestamp,
        visitorid,
        event,
        itemid,
        transactionid,
        COUNT(*) AS repeat_count
    FROM raw_events
    GROUP BY
        timestamp,
        visitorid,
        event,
        itemid,
        transactionid
    HAVING COUNT(*) > 1
)

-- 每组保留一条，计算其余重复记录共有多少条
SELECT
    COALESCE(SUM(repeat_count - 1), 0) AS duplicate_extra_rows
FROM duplicate_groups;