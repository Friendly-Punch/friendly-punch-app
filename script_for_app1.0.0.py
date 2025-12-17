import streamlit as st
import pandas as pd

st.title("資産形成シミュレーション（選択式ライフイベント対応）")

# 基本情報
start_age = st.number_input("開始年齢", min_value=18, max_value=80, value=30)
goal_age = st.number_input("目標年齢", min_value=start_age+1, max_value=100, value=65)
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
# ライフイベント選択肢
# -------------------------
st.subheader("ライフイベント設定")
events = []

if st.checkbox("教育費（子どもの大学進学など）"):
    edu_age = st.number_input("教育費発生年齢", min_value=start_age+1, max_value=goal_age, value=start_age+20)
    edu_cost = st.number_input("教育費支出額（円）", min_value=100000, step=100000, value=3000000)
    events.append({"name": "教育費", "age": edu_age, "cost": edu_cost})

if st.checkbox("住宅購入"):
    house_age = st.number_input("住宅購入年齢", min_value=start_age+1, max_value=goal_age, value=start_age+10)
    house_cost = st.number_input("住宅購入費用（円）", min_value=1000000, step=1000000, value=30000000)
    events.append({"name": "住宅購入", "age": house_age, "cost": house_cost})

if st.checkbox("車購入"):
    car_age = st.number_input("車購入年齢", min_value=start_age+1, max_value=goal_age, value=start_age+5)
    car_cost = st.number_input("車購入費用（円）", min_value=100000, step=100000, value=3000000)
    events.append({"name": "車購入", "age": car_age, "cost": car_cost})

if st.checkbox("結婚"):
    marriage_age = st.number_input("結婚年齢", min_value=start_age+1, max_value=goal_age, value=start_age+8)
    marriage_cost = st.number_input("結婚費用（円）", min_value=100000, step=100000, value=5000000)
    events.append({"name": "結婚", "age": marriage_age, "cost": marriage_cost})

if st.checkbox("その他イベント"):
    other_name = st.text_input("イベント名", "旅行")
    other_age = st.number_input("イベント発生年齢", min_value=start_age+1, max_value=goal_age, value=start_age+15)
    other_cost = st.number_input("イベント支出額（円）", min_value=100000, step=100000, value=1000000)
    events.append({"name": other_name, "age": other_age, "cost": other_cost})

# -------------------------
# シミュレーション開始ボタン
# -------------------------
if st.button("シミュレーション開始！"):
    ages = list(range(start_age + 1, goal_age + 1))
    invest_values, cash_values, total_values, event_spending, event_names = [], [], [], [], []
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

        # ライフイベント発生
        spent, ev_name = 0, ""
        for ev in events:
            if age == ev["age"]:
                spent = ev["cost"]
                ev_name = ev["name"]
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
        event_names.append(ev_name)

    df = pd.DataFrame({
        "年齢": ages,
        "運用資産": invest_values,
        "現金資産": cash_values,
        "合計資産": total_values,
        "イベント支出": event_spending,
        "イベント名": event_names
    })

    # グラフ表示
    st.subheader("年齢ごとの資産推移")
    st.line_chart(df.set_index("年齢")[["運用資産", "現金資産", "合計資産"]])

    # 表を任意表示
    if st.checkbox("年齢ごとの資産表を表示する"):
        st.dataframe(df.style.format({
            "運用資産": "{:,.0f}", 
            "現金資産": "{:,.0f}", 
            "合計資産": "{:,.0f}", 
            "イベント支出": "{:,.0f}"
        }))