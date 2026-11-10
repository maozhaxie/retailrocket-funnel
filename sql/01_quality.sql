SELECT
    COUNT(*) AS total_rows,

    COUNT(*) - COUNT(timestamp) AS missing_timestamp,
    COUNT(*) - COUNT(visitorid) AS missing_visitorid,
    COUNT(*) - COUNT(event) AS missing_event,
    COUNT(*) - COUNT(itemid) AS missing_itemid,
    COUNT(*) - COUNT(transactionid) AS missing_transactionid

FROM raw_events;