CREATE OR REPLACE TABLE raw_events AS
SELECT *
FROM read_csv(
    'data/raw/events.csv',
    header = true,
    columns = {
        'timestamp': 'BIGINT',
        'visitorid': 'BIGINT',
        'event': 'VARCHAR',
        'itemid': 'BIGINT',
        'transactionid': 'BIGINT'
    }
);

-- 第二步：统计每种行为有多少条记录
SELECT
    event,
    COUNT(*) AS event_count
FROM raw_events
GROUP BY event
ORDER BY event_count DESC;