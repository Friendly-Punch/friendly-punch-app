import streamlit as st
import pandas as pd

st.title("資産形成シミュレーション（収支＋ライフイベント対応）")

# 基本情報
start_age = st.number_input("開始年齢", min_value=18, max_value=80, value=30)
goal_age = st.number_input("目標年齢", min_value=start_age+1, max_value=100, value=65)
income = st.number_input("月々の手取り額（円）", min_value=50000, step=10000, value=300000)
rate = st.slider("運用利回り（年率 %）", 0.0, 10.0, 5.0)

r_month = rate / 100 / 12

# 支出内訳
housing = st.number_input("住居費（円）", 0, step=1000, value=60000)
food = st.number_input("食費（円）", 0, step=1000, value=40000)
utilities = st.number_input("光熱費（円）", 0, step=1000, value=15000)
insurance = st.number_input("保険・医療（円）", 0, step=1000, value=20000)
education = st.number_input("教育費（円）", 0, step=1000, value=30000)
other = st.number_input("その他生活費（円）", 0, step=1000, value=20000)

# 支出変動率
housing_growth = st.slider("住居費の年間増減率（%）", -5.0, 5.0, 0.0)
food_growth = st.slider("食費の年間増減率（%）", -5.0, 5.0, 1.0)
utilities_growth = st.slider("光熱費の年間増減率（%）", -5.0, 5.0, 0.0)
insurance_growth = st.slider("保険・医療の年間増減率（%）", -5.0, 5.0, 0.0)
education_growth = st.slider("教育費の年間増減率（%）", -5.0, 10.0, 3.0)
other_growth = st.slider("その他生活費の年間増減率（%）", -5.0, 5.0, 0.0)

# 余剰資金の振り分け
ratio_invest = st.slider("余剰資金の運用割合（%）", 0, 100, 50)
ratio_cash = 100 - ratio_invest

# ライフイベント入力
events = []
if st.checkbox("ライフイベントを追加する"):
    event_name = st.text_input("イベント名", "住宅購入")
    event_age = st.number_input("イベント発生年齢", min_value=start_age+1, max_value=goal_age, value=start_age+10)
    event_cost = st.number_input("イベント支出額（円）", min_value=100000, step=100000, value=5000000)
    events.append({"name": event_name, "age": event_age, "cost": event_cost})

# 資産推移計算
ages = list(range(start_age + 1, goal_age + 1))
invest_values, cash_values, total_values, event_spending = [], [], [], []
value_invest, value_cash = 0.0, 0.0

for age in ages:
    # 支出更新
    housing *= (1 + housing_growth/100)
    food *= (1 + food_growth/100)
    utilities *= (1 + utilities_growth/100)
    insurance *= (1 + insurance_growth/100)
    education *= (1 + education_growth/100)
    other *= (1 + other_growth/100)

    expenses_total = housing + food + utilities + insurance + education + other
    surplus = income - expenses_total

    invest_amount = surplus * ratio_invest / 100
    cash_amount = surplus * ratio_cash / 100

    # 運用資産（複利）
    for _ in range(12):
        value_invest = value_invest * (1 + r_month) + invest_amount

    # 現金資産（単純加算）
    value_cash += cash_amount * 12

    # ライフイベント発生
    spent = 0
    for ev in events:
        if age == ev["age"]:
            spent = ev["cost"]
            # 現金から優先的に差し引き、足りなければ運用から
            if value_cash >= spent:
                value_cash -= spent
            else:
                deficit = spent - value_cash
                value_cash = 0
                value_invest -= deficit

    invest_values.append(value_invest)
    cash_values.append(value_cash)
    total_values.append(value_invest + value_cash)
    event_spending.append(spent)

df = pd.DataFrame({
    "年齢": ages,
    "運用資産": invest_values,
    "現金資産": cash_values,
    "合計資産": total_values,
    "イベント支出": event_spending
})

# グラフ表示
st.subheader("年齢ごとの資産推移")
st.line_chart(df.set_index("年齢")[["運用資産", "現金資産", "合計資産"]])

# 表を任意表示
if st.checkbox("年齢ごとの資産表を表示する"):
    st.dataframe(df.style.format({"運用資産": "{:,.0f}", "現金資産": "{:,.0f}", "合計資産": "{:,.0f}", "イベント支出": "{:,.0f}"}))