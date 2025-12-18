import streamlit as st
import random
import matplotlib.pyplot as plt

# -----------------------------
# 初期設定
# -----------------------------
st.title("家計・資産運用シミュレーション（簡易版）")

start_age = st.number_input("開始年齢", 18, 80, 25)
goal_age = st.number_input("終了年齢", start_age+1, 100, 65)
current_salary = st.number_input("月給（手取り 円）", 0, step=10000, value=300000)

# ボーナス設定
bonus_multiplier = st.slider("ボーナス倍率（何か月分）", 0.0, 6.0, 2.5)
bonus_spend_ratio = st.slider("ボーナス支出割合（旅行・買い物など）", 0, 100, 30)
bonus_cash_ratio = st.slider("ボーナス現金貯金割合", 0, 100, 40)
bonus_invest_ratio = 100 - bonus_spend_ratio - bonus_cash_ratio

annual_bonus = current_salary * bonus_multiplier * 2

# -----------------------------
# 支出カテゴリ
# -----------------------------
housing = st.number_input("住居費（月額 円）", 0, step=1000, value=80000)
food = st.number_input("食費（月額 円）", 0, step=1000, value=60000)

utilities = st.number_input("水道光熱費（月額 円）", 0, step=1000, value=20000)
comm = st.number_input("通信費（月額 円）", 0, step=1000, value=12000)
transport = st.number_input("交通費（月額 円）", 0, step=1000, value=20000)
insurance = st.number_input("保険料（月額 円）", 0, step=1000, value=30000)
misc = st.number_input("その他雑費（月額 円）", 0, step=1000, value=50000)

# -----------------------------
# 投資・余力振り分け設定
# -----------------------------
allocation_mode = st.radio("余力の振り分け方法", ["デフォルト固定割合", "100-年齢ルール", "個人設定"])

if allocation_mode == "デフォルト固定割合":
    invest_ratio = 50
    cash_ratio = 50
elif allocation_mode == "100-年齢ルール":
    invest_ratio = max(0, 100 - start_age)
    cash_ratio = 100 - invest_ratio
elif allocation_mode == "個人設定":
    invest_ratio = st.slider("投資割合（%）", 0, 100, 50)
    cash_ratio = 100 - invest_ratio

cash_rate = st.slider("預金利息（年率 %）", 0.0, 1.0, 0.01)

scenario = st.radio("投資シナリオ", ["ランダム変動", "強気", "弱気"])
if scenario == "ランダム変動":
    avg_invest_rate = st.slider("平均投資利回り（年率 %）", -10.0, 20.0, 3.0)
    volatility = st.slider("変動幅（年率 %）", 0.0, 20.0, 5.0)
elif scenario == "強気":
    avg_invest_rate = 6.0
    volatility = 3.0
elif scenario == "弱気":
    avg_invest_rate = 1.0
    volatility = 8.0

# -----------------------------
# シミュレーション本体
# -----------------------------
value_cash = 0
value_invest = 0
history_cash = []
history_invest = []
history_total = []
ages = []

for age in range(start_age, goal_age+1):
    for month in range(12):
        # 月収入
        monthly_income = current_salary
        
        # 月支出
        monthly_expenses = housing + food + utilities + comm + transport + insurance + misc
        
        # 余力
        surplus = monthly_income - monthly_expenses
        
        # 投資利回り（ランダム）
        rand_factor = random.uniform(-1, 1)
        monthly_rate = (avg_invest_rate + rand_factor * volatility) / 100 / 12
        
        # 資産更新
        value_cash = value_cash * (1 + cash_rate/100/12) + surplus * cash_ratio/100
        value_invest = value_invest * (1 + monthly_rate) + surplus * invest_ratio/100
        
        # ボーナス処理（仮に6月と12月）
        if month in [5, 11]:
            bonus_spend = annual_bonus/2 * bonus_spend_ratio/100
            bonus_cash = annual_bonus/2 * bonus_cash_ratio/100
            bonus_invest = annual_bonus/2 * bonus_invest_ratio/100
            
            if value_cash >= bonus_spend:
                value_cash -= bonus_spend
            else:
                value_cash = 0  # 足りなければゼロ
            
            value_cash += bonus_cash
            value_invest = value_invest * (1 + monthly_rate) + bonus_invest
    
    # 年末記録
    history_cash.append(value_cash)
    history_invest.append(value_invest)
    history_total.append(value_cash + value_invest)
    ages.append(age)

# -----------------------------
# グラフ描画
# -----------------------------
fig, ax = plt.subplots(figsize=(10,6))
ax.plot(ages, history_cash, label="現金資産", color="blue")
ax.plot(ages, history_invest, label="投資資産", color="green")
ax.plot(ages, history_total, label="総資産", color="red")
ax.set_xlabel("年齢")
ax.set_ylabel("資産額（円）")
ax.legend()
st.pyplot(fig)