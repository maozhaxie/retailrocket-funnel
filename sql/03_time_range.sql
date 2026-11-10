SELECT
    epoch_ms(MIN(timestamp)) AS first_time_utc,
    epoch_ms(MAX(timestamp)) AS last_time_utc
FROM raw_events;