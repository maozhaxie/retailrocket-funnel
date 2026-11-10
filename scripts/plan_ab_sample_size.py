from math import ceil, sqrt
from statistics import NormalDist

baseline_rate = 8986 / 1399102
relative_lift = 0.20
target_rate = baseline_rate * (1 + relative_lift)

alpha = 0.05
power = 0.80

normal = NormalDist()
z_alpha = normal.inv_cdf(1 - alpha / 2)
z_power = normal.inv_cdf(power)

average_rate = (baseline_rate + target_rate) / 2
rate_difference = target_rate - baseline_rate

null_variance = 2 * average_rate * (1 - average_rate)
alternative_variance = (
    baseline_rate * (1 - baseline_rate)
    + target_rate * (1 - target_rate)
)

numerator = (
    z_alpha * sqrt(null_variance)
    + z_power * sqrt(alternative_variance)
)
users_per_group = ceil((numerator / rate_difference) ** 2)

print(f"基准购买率：{baseline_rate:.4%}")
print(f"目标购买率：{target_rate:.4%}")
print(f"每组预计需要：{users_per_group:,} 人")
print(f"两组合计需要：{users_per_group * 2:,} 人")
