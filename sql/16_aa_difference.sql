WITH group_stats AS (
    SELECT
        experiment_group,
        COUNT(*) AS users,
        AVG(purchased_24h) AS purchase_rate
    FROM aa_assignments
    GROUP BY experiment_group
),
comparison AS (
    SELECT
        a.purchase_rate AS rate_a,
        b.purchase_rate AS rate_b,
        b.purchase_rate - a.purchase_rate AS rate_difference,
        SQRT(
            a.purchase_rate * (1 - a.purchase_rate) / a.users
            + b.purchase_rate * (1 - b.purchase_rate) / b.users
        ) AS standard_error
    FROM group_stats AS a
    CROSS JOIN group_stats AS b
    WHERE a.experiment_group = 'A'
      AND b.experiment_group = 'B'
)
SELECT
    ROUND(100.0 * rate_a, 4) AS rate_a_pct,
    ROUND(100.0 * rate_b, 4) AS rate_b_pct,
    ROUND(100.0 * rate_difference, 4) AS difference_pp,
    ROUND(
        100.0 * (rate_difference - 1.96 * standard_error),
        4
    ) AS ci_lower_pp,
    ROUND(
        100.0 * (rate_difference + 1.96 * standard_error),
        4
    ) AS ci_upper_pp
FROM comparison;