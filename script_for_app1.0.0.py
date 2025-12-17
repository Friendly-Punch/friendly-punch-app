import streamlit as st
import pandas as pd

st.title("資産形成シミュレーション（振り分け2択対応）")

# 基本情報
start_age = st.number_input("開始年齢", min_value=18, max_value=80, value=30)
goal_age = st.number_input("目標年齢（例：65歳）", min_value=start_age+1, max_value=100, value=65)
income = st.number_input("月々の手取り額（円）", min_value=50000, step=10000, value=300000)
rate = st.slider("運用利回り（年率 %）", 0.0, 10.0, 5.0)

r_month = rate / 100 / 12

# 支出内訳（簡易版）
housing = st.number_input("住居費（円）", 0, step=1000, value=60000)
food = st.number_input("食費（円）", 0, step=1000, value=40000)
other = st.number_input("その他生活費（円）", 0, step=1000, value=50000)

# 支出変動率
housing_growth = st.slider("住居費の年間増減率（%）", -5.0, 5.0, 0.0)
food_growth = st.slider("食費の年間増減率（%）", -5.0, 5.0, 1.0)
other_growth = st.slider("その他生活費の年間増減率（%）", -5.0, 5.0, 0.0)

# 振り分けモード選択
allocation_mode = st.radio(
    "余剰資金の振り分け方法",
    ["常に一定割合", "参考モデル（100 - 年齢）%"]
)

if allocation_mode == "常に一定割合":
    fixed_ratio_invest = st.slider("余剰資金の運用割合（%）", 0, 100, 50)

# -------------------------
# シミュレーション開始ボタン
# -------------------------
if st.button("シミュレーション開始！"):
    ages = list(range(start_age + 1, goal_age + 1))
    invest_values, cash_values, total_values = [], [], []
    value_invest, value_cash = 0.0, 0.0

    for age in ages:
        # 支出更新
        housing *= (1 + housing_growth/100)
        food *= (1 + food_growth/100)
        other *= (1 + other_growth/100)

        expenses_total = housing + food + other
        surplus = income - expenses_total

        # 振り分け計算
        if allocation_mode == "常に一定割合":
            invest_amount = surplus * fixed_ratio_invest / 100
            cash_amount = surplus * (100 - fixed_ratio_invest) / 100
        else:
            invest_ratio = max(0, 100 - age)
            cash_ratio = 100 - invest_ratio
            invest_amount = surplus * invest_ratio / 100
            cash_amount = surplus * cash_ratio / 100

        # 運用資産（複利）
        for _ in range(12):
            value_invest = value_invest * (1 + r_month) + invest_amount

        # 現金資産（単純加算）
        value_cash += cash_amount * 12

        invest_values.append(value_invest)
        cash_values.append(value_cash)
        total_values.append(value_invest + value_cash)

    df = pd.DataFrame({
        "年齢": ages,
        "運用資産": invest_values,
        "現金資産": cash_values,
        "合計資産": total_values
    })

    # グラフ表示
    st.subheader("年齢ごとの資産推移")
    st.line_chart(df.set_index("年齢")[["運用資産", "現金資産", "合計資産"]])

    # 表を任意表示
    if st.checkbox("年齢ごとの資産表を表示する"):
        st.dataframe(df.style.format({
            "運用資産": "{:,.0f}", 
            "現金資産": "{:,.0f}", 
            "合計資産": "{:,.0f}"
        }))