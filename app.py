from pathlib import Path

from math import sqrt, erfc

import pandas as pd
import plotly.express as px
import streamlit as st

csv_path = Path(__file__).resolve().parent / "reports" / "funnel_windows.csv"
data = pd.read_csv(csv_path)

st.title("RetailRocket 电商转化分析")

fig = px.bar(
    data,
    x="window_label",
    y="view_to_purchase_pct",
    category_orders={"window_label": ["1h", "24h", "7d"]},
    labels={
        "window_label": "从首次浏览开始计算的时间窗口",
        "view_to_purchase_pct": "浏览到购买的转化率",
    },
    title="不同时间窗口下的浏览到购买转化率",
)
fig.update_yaxes(ticksuffix="%", rangemode="tozero")

st.plotly_chart(fig)

selected_window = st.segmented_control(
    "选择时间窗口",
    ["1h", "24h", "7d"],
    default="24h",
    required=True,
)

selected_row = data.loc[data["window_label"] == selected_window].iloc[0]

view_col, cart_col, purchase_col = st.columns(3)
view_col.metric("浏览组合数", f"{selected_row['viewed_pairs']:,}")
cart_col.metric("加购组合数", f"{selected_row['carted_pairs']:,}")
purchase_col.metric("购买组合数", f"{selected_row['purchased_pairs']:,}")



st.subheader(f"{selected_window} 转化漏斗")

funnel_fig = px.funnel(
    x=[
        selected_row["viewed_pairs"],
        selected_row["carted_pairs"],
        selected_row["purchased_pairs"],
    ],
    y=["浏览", "加购", "购买"],
    labels={"x": "组合数", "y": "漏斗阶段"},
)
funnel_fig.update_traces(texttemplate="%{x:,.0f}", textposition="outside")
st.plotly_chart(funnel_fig, alt=f"{selected_window} 窗口的浏览、加购和购买漏斗")



st.subheader("工作日与周末的 24 小时转化对比")

day_data = pd.read_csv(csv_path.with_name("weekday_weekend.csv"))
day_data["首次浏览日"] = day_data["first_view_day_type"].map(
    {"weekday": "工作日", "weekend": "周末"}
)

day_fig = px.bar(
    day_data,
    x="首次浏览日",
    y="view_to_purchase_pct_24h",
    category_orders={"首次浏览日": ["工作日", "周末"]},
    labels={"view_to_purchase_pct_24h": "浏览到购买的转化率"},
)
day_fig.update_yaxes(ticksuffix="%", rangemode="tozero")
st.plotly_chart(day_fig, alt="工作日和周末首次浏览后的 24 小时购买转化率")


st.subheader("A/B 模拟购买率对比")
st.caption("以下结果来自模拟数据，B组购买概率预设为相对提高20%。")

ab_path = (
    Path(__file__).resolve().parent
    / "data"
    / "processed"
    / "ab_simulated_users.csv"
)
ab_data = pd.read_csv(ab_path)

# 把用户明细汇总成 A、B 两行
ab_summary = ab_data.groupby("experiment_group", as_index=False).agg(
    users=("simulated_user_id", "size"),
    purchasers=("purchased_24h", "sum"),
)
ab_summary["purchase_rate_pct"] = (
    100.0 * ab_summary["purchasers"] / ab_summary["users"]
)

ab_fig = px.bar(
    ab_summary,
    x="experiment_group",
    y="purchase_rate_pct",
    text="purchase_rate_pct",
    labels={
        "experiment_group": "模拟分组",
        "purchase_rate_pct": "购买率",
    },
)
ab_fig.update_traces(texttemplate="%{text:.4f}%", textposition="outside")
ab_fig.update_yaxes(ticksuffix="%", rangemode="tozero")

st.plotly_chart(ab_fig, alt="模拟数据中A组与B组的购买率对比")


# 取出 A、B 两组的汇总结果
group_a = ab_summary.loc[ab_summary["experiment_group"] == "A"].iloc[0]
group_b = ab_summary.loc[ab_summary["experiment_group"] == "B"].iloc[0]

rate_a = group_a["purchasers"] / group_a["users"]
rate_b = group_b["purchasers"] / group_b["users"]
difference = rate_b - rate_a

# 计算差值的 95% 置信区间
standard_error = sqrt(
    rate_a * (1 - rate_a) / group_a["users"]
    + rate_b * (1 - rate_b) / group_b["users"]
)
ci_lower = difference - 1.96 * standard_error
ci_upper = difference + 1.96 * standard_error

# 计算双侧检验的 p 值
pooled_rate = (
    (group_a["purchasers"] + group_b["purchasers"])
    / (group_a["users"] + group_b["users"])
)
null_standard_error = sqrt(
    pooled_rate * (1 - pooled_rate)
    * (1 / group_a["users"] + 1 / group_b["users"])
)
p_value = erfc(abs(difference / null_standard_error) / sqrt(2))

difference_col, p_value_col = st.columns(2)
difference_col.metric("B减A（百分点）", f"{difference * 100:.4f}")
p_value_col.metric("双侧检验p值", f"{p_value:.6f}")

st.markdown(
    f"差值的 **95%置信区间**为 "
    f"**[{ci_lower * 100:.4f}, {ci_upper * 100:.4f}] 个百分点**。"
)

if p_value < 0.05:
    st.info("按预先设定的5%标准，本次模拟中两组购买率存在统计显著差异。")
else:
    st.info("按预先设定的5%标准，本次模拟未检出两组购买率的统计显著差异。")