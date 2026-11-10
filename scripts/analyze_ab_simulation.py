from math import sqrt, erfc
from pathlib import Path

import pandas as pd

project_root = Path(__file__).resolve().parents[1]
data_path = project_root / "data" / "processed" / "ab_simulated_users.csv"
data = pd.read_csv(data_path)

# 分别统计两组用户数和购买人数
summary = data.groupby("experiment_group").agg(
    users=("simulated_user_id", "size"),
    purchasers=("purchased_24h", "sum"),
)

n_a = summary.loc["A", "users"]
n_b = summary.loc["B", "users"]
buyers_a = summary.loc["A", "purchasers"]
buyers_b = summary.loc["B", "purchasers"]

rate_a = buyers_a / n_a
rate_b = buyers_b / n_b
difference = rate_b - rate_a

# 用两组各自的购买率计算差值的标准误和置信区间
standard_error = sqrt(
    rate_a * (1 - rate_a) / n_a
    + rate_b * (1 - rate_b) / n_b
)
ci_lower = difference - 1.96 * standard_error
ci_upper = difference + 1.96 * standard_error

# 在“两组购买概率相等”的假设下，计算双侧 z 检验的 p 值
pooled_rate = (buyers_a + buyers_b) / (n_a + n_b)
null_standard_error = sqrt(
    pooled_rate * (1 - pooled_rate) * (1 / n_a + 1 / n_b)
)
z_value = difference / null_standard_error
p_value = erfc(abs(z_value) / sqrt(2))

print("A/B 模拟数据分析")
print(f"A组购买率：{rate_a:.4%}")
print(f"B组购买率：{rate_b:.4%}")
print(f"B减A的差值：{difference * 100:.4f} 个百分点")
print(
    f"差值的95%置信区间："
    f"[{ci_lower * 100:.4f}, {ci_upper * 100:.4f}] 个百分点"
)
print(f"双侧检验p值：{p_value:.6f}")