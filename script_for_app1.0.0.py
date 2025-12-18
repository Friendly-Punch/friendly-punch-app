import streamlit as st
import random
import matplotlib.pyplot as plt

# -----------------------------
# 初期設定
# -----------------------------
st.title("家計・資産運用シミュレーション（フルイベント版）")

start_age = st.number_input("開始年齢", 18, 80, 25)
goal_age = st.number_input("終了年齢", start_age+1, 100, 65)
current_salary = st.number_input("月給（手取り 円）", 0, step=10000, value=300000)

# -----------------------------
# ボーナス設定
# -----------------------------
bonus_multiplier = st.slider("ボーナス倍率（何か月分）", 0.0, 6.0, 2.5)
bonus_spend_ratio = st.slider("ボーナス支出割合（旅行・買い物など）", 0, 100, 30)
bonus_cash_ratio = st.slider("ボーナス現金貯金割合", 0, 100, 40)
bonus_invest_ratio = 100 - bonus_spend_ratio - bonus_cash_ratio
annual_bonus = current_salary * bonus_multiplier * 2

# -----------------------------
# 支出カテゴリ（年間増減率＋イベント補正）
# -----------------------------
def expense_with_growth(base, growth, years, event_up=0, event_down=0, event_flag_up=False, event_flag_down=False):
    val = base * ((1 + growth/100) ** years)
    if event_flag_up:
        val *= (1 + event_up/100)
    if event_flag_down:
        val *= (1 - event_down/100)
    return val

housing = st.number_input("住居費（月額 円）", 0, step=1000, value=80000)
food = st.number_input("食費（月額 円）", 0, step=1000, value=60000)

utilities_base = st.number_input("水道光熱費（月額 円）", 0, step=1000, value=20000)
utilities_growth = st.slider("水道光熱費 年間増減率（%）", -5.0, 10.0, 1.5)
utilities_event_up = st.slider("車購入後の増加率（%）", 0.0, 50.0, 10.0)
utilities_event_down = st.slider("定年退職後の減少率（%）", 0.0, 50.0, 20.0)

comm_base = st.number_input("通信費（月額 円）", 0, step=1000, value=12000)
comm_growth = st.slider("通信費 年間増減率（%）", -5.0, 10.0, 1.0)

transport_base = st.number_input("交通費（月額 円）", 0, step=1000, value=20000)
transport_growth = st.slider("交通費 年間増減率（%）", -5.0, 10.0, 1.5)

insurance_base = st.number_input("保険料（月額 円）", 0, step=1000, value=30000)
insurance_growth = st.slider("保険料 年間増減率（%）", -5.0, 10.0, 1.0)

misc_base = st.number_input("その他雑費（月額 円）", 0, step=1000, value=50000)
misc_growth = st.slider("その他雑費 年間増減率（%）", -5.0, 10.0, 1.0)

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
# イベント設定（例）
# -----------------------------
house_age = st.number_input("住宅購入年齢", min_value=start_age+1, max_value=goal_age, value=start_age+35)
house_cost = st.number_input("住宅購入費用（円）", min_value=1000000, step=1000000, value=30000000)

car_age = st.number_input("車購入年齢", min_value=start_age+1, max_value=goal_age, value=start_age+30)
car_cost = st.number_input("車購入費用（円）", min_value=100000, step=100000, value=3000000)

edu_age = st.number_input("教育費発生年齢", min_value=start_age+1, max_value=goal_age, value=start_age+20)
edu_cost = st.number_input("教育費支出額（円）", min_value=100000, step=100000, value=3000000)

marriage_age = st.number_input("結婚年齢", min_value=start_age+1, max_value=goal_age, value=start_age+28)
marriage_cost = st.number_input("結婚費用（円）", min_value=100000, step=100000, value=5000000)

travel_age = st.number_input("旅行イベント年齢", min_value=start_age+1, max_value=goal_age, value=start_age+25)
travel_cost = st.number_input("旅行費用（円）", min_value=10000, step=10000, value=300000)

# -----------------------------
# シミュレーション本体
# -----------------------------
value_cash = 0
value_invest = 0
history_cash, history_invest, history_total, ages = [], [], [], []

for age in range(start_age, goal_age+1):
    for month in range(12):
        years_passed = age - start_age

        # 各カテゴリ支出
        utilities_month = expense_with_growth(utilities_base, utilities_growth, years_passed)
        comm_month = expense_with_growth(comm_base, comm_growth, years_passed)
        transport_month = expense_with_growth(transport_base, transport_growth, years_passed)
        insurance_month = expense_with_growth(insurance_base, insurance_growth, years_passed)
        misc_month = expense_with_growth(misc_base, misc_growth, years_passed)

        monthly_expenses = housing + food + utilities_month + comm_month + transport_month + insurance_month + misc_month
        monthly_income = current_salary
        surplus = monthly_income - monthly_expenses

        # 投資利回り（ランダム＋シナリオ）
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
                value_cash = 0
            value_cash += bonus_cash
            value_invest = value_invest * (1 + monthly_rate) + bonus_invest

        # イベント処理（簡易版）
        if age == house_age and month == 6:
            if value_cash >= house_cost:
                value_cash -= house_cost
            else:
                # ローン処理（簡易版：頭金20%、残りを返済年数で割る）
                down_payment = house_cost * 0.2
                if value_cash >= down_payment:
                    value_cash -= down_payment
                else:
                    value_cash = 0
                loan_amount = house_cost - down_payment
                monthly_loan = loan_amount / (30 * 12)  # 30年返済の簡易版
                monthly_expenses += monthly_loan

        if age == car_age and month == 6:
            if value_cash >= car_cost:
                value_cash -= car_cost
            else:
                down_payment = car_cost * 0.2
                if value_cash >= down_payment:
                    value_cash -= down_payment
                else:
                    value_cash = 0
                loan_amount = car_cost - down_payment
                monthly_loan = loan_amount / (5 * 12)  # 5年返済の簡易版
                monthly_expenses += monthly_loan

        if age == edu_age and month == 4:  # 教育費イベント
            if value_cash >= edu_cost:
                value_cash -= edu_cost
            else:
                down_payment = edu_cost * 0.2
                if value_cash >= down_payment:
                    value_cash -= down_payment
                else:
                    value_cash = 0
                loan_amount = edu_cost - down_payment
                monthly_loan = loan_amount / (10 * 12)  # 10年返済の簡易版
                monthly_expenses += monthly_loan

        if age == marriage_age and month == 9:  # 結婚イベント
            if value_cash >= marriage_cost:
                value_cash -= marriage_cost
            else:
                down_payment = marriage_cost * 0.2
                if value_cash >= down_payment:
                    value_cash -= down_payment
                else:
                    value_cash = 0
                loan_amount = marriage_cost - down_payment
                monthly_loan = loan_amount / (5 * 12)  # 5年返済の簡易版
                monthly_expenses += monthly_loan

        if age == travel_age and month == 7:  # 旅行イベント
            if value_cash >= travel_cost:
                value_cash -= travel_cost
            else:
                st.warning("現金不足のため旅行イベントを実施できません")
    # 年末記録
    history_cash.append(value_cash)
    history_invest.append(value_invest)
    history_total.append(value_cash + value_invest)
    ages.append(age)

fig, ax = plt.subplots(figsize=(10,6))
ax.plot(ages, history_cash, label="現金資産", color="blue")
ax.plot(ages, history_invest, label="投資資産", color="green")
ax.plot(ages, history_total, label="総資産", color="red")
ax.set_xlabel("年齢")
ax.set_ylabel("資産額（円）")
ax.set_title("資産推移シミュレーション（イベント込み）")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# 最終結果を表示
st.write("最終的な現金資産:", f"{history_cash[-1]:,.0f} 円")
st.write("最終的な投資資産:", f"{history_invest[-1]:,.0f} 円")
st.write("最終的な総資産:", f"{history_total[-1]:,.0f} 円")