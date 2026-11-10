import numpy as np


import pandas as pd
from pathlib import Path


# 使用刚才算出的样本量和基准购买率
users_per_group = 66737
baseline_rate = 8986 / 1399102
target_rate = baseline_rate * 1.20

# 固定随机种子，让相同代码每次得到相同结果
rng = np.random.default_rng(20261108)

# 每位模拟用户的结果为 0 或 1
purchase_a = rng.binomial(1, baseline_rate, size=users_per_group)
purchase_b = rng.binomial(1, target_rate, size=users_per_group)

print(f"A组用户数：{users_per_group:,}")
print(f"A组购买人数：{purchase_a.sum():,}")
print(f"A组购买率：{purchase_a.mean():.4%}")

print(f"B组用户数：{users_per_group:,}")
print(f"B组购买人数：{purchase_b.sum():,}")
print(f"B组购买率：{purchase_b.mean():.4%}")



# 把两组结果整理成一张表，每位模拟用户占一行
simulated_data = pd.DataFrame(
    {
        "simulated_user_id": np.arange(1, users_per_group * 2 + 1),
        "experiment_group": np.repeat(["A", "B"], users_per_group),
        "purchased_24h": np.concatenate([purchase_a, purchase_b]),
        "data_origin": "simulated",
    }
)

# 保存到项目的 data/processed 文件夹
project_root = Path(__file__).resolve().parents[1]
output_path = project_root / "data" / "processed" / "ab_simulated_users.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)

simulated_data.to_csv(output_path, index=False, encoding="utf-8")

print(f"已保存 {len(simulated_data):,} 行模拟数据")
print(f"保存位置：{output_path}")