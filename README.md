# RetailRocket 电商转化漏斗分析

用 DuckDB SQL 分析公开电商日志，以「访客＋商品」为单位匹配浏览、加购和购买，并用 Streamlit 展示转化路径和时间窗口差异。

- 对 2,756,101 条事件进行质量检查与去重，保留 2,755,641 条有效事件。
- 在能完整观察 7 天的 2,042,310 个浏览组合上比较 1 小时、24 小时和 7 天窗口。购买转化率分别为 **0.61%、0.71%、0.76%**，从 1 小时放宽到 24 小时多计入 2,101 个转化组合。
- 按首次浏览日期（UTC）分组，工作日与周末的 24 小时购买转化率分别为 **0.77% 和 0.52%**。这组历史数据用于描述转化差异。
- 在独立的模拟模块中，用历史购买率作参数，练习样本量规划、两比例检验和置信区间。看板明确标注模拟结果。

## 运行看板

使用 Python 3.12，在仓库根目录运行以下命令。看板使用仓库内的两份历史汇总表和脚本本地生成的模拟数据。

```sh
python -m pip install -r requirements-lock.txt
python scripts/generate_ab_simulation.py
python -m streamlit run app.py
```

打开终端显示的 Local URL。若要核对模拟的样本量和统计结果，运行：

```sh
python scripts/plan_ab_sample_size.py
python scripts/analyze_ab_simulation.py
```

## 复现历史分析

```sh
python scripts/download_data.py
python scripts/profile_data.py
```

若下载接口要求登录，请从 [RetailRocket 的 Kaggle 发布页](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset) 获取 `events.csv` 并放入 `data/raw/`。在以仓库根目录为当前目录的 DuckDB 会话中，先执行 [00_load.sql](sql/00_load.sql) 和 [04_clean.sql](sql/04_clean.sql)，再执行 [多窗口漏斗](sql/11_funnel_windows.sql) 与 [工作日和周末对比](sql/13_weekday_weekend.sql)。SQL 14–16 可依次运行以复现历史 A/A 演练。

- [历史分析报告](reports/analysis_report.md)
- [A/A 演练与 A/B 模拟报告](reports/ab_simulation_report.md)
- [指标口径](docs/02_指标与验收规范.md)
- [数据来源与许可](docs/00_数据来源.md)

数据归属 RetailRocket / Roman Zykov。数据来源与适用许可见 [来源清单](reports/source_manifest.json)。仓库提供代码、聚合结果和报告。
