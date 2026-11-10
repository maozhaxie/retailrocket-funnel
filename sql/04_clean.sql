-- 建立清洗表，同时增加一列方便阅读的日期时间
CREATE OR REPLACE TABLE clean_events AS
SELECT DISTINCT
    timestamp,
    visitorid,
    event,
    itemid,
    transactionid,
    epoch_ms(timestamp) AS event_time_utc
FROM raw_events
WHERE timestamp IS NOT NULL
  AND visitorid IS NOT NULL
  AND event IS NOT NULL
  AND itemid IS NOT NULL
  AND event IN ('view', 'addtocart', 'transaction')
  AND (
      event <> 'transaction'
      OR transactionid IS NOT NULL
  );

-- 对比原始表与清洗表的数量
SELECT
    'raw_events' AS table_name,
    COUNT(*) AS row_count
FROM raw_events

UNION ALL

SELECT
    'clean_events' AS table_name,
    COUNT(*) AS row_count
FROM clean_events;