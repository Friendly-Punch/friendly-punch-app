import streamlit as st

st.title("ライフイベント設定（人生の順番で入力）")

# -----------------------------
# 車購入（5年ごとに買い替え）
# -----------------------------
st.header("🚗 車購入")
car_first_age = st.number_input("最初の車購入年齢", min_value=18, max_value=100, value=30)
car_cost = st.number_input("車購入費用（円）", min_value=100000, step=100000, value=3000000)

# -----------------------------
# 結婚
# -----------------------------
st.header("💍 結婚")
marriage_age = st.number_input("結婚年齢", min_value=18, max_value=100, value=28)
marriage_cost = st.number_input("結婚費用（円）", min_value=100000, step=100000, value=2000000)

# -----------------------------
# 子ども（人数可変）
# -----------------------------
st.header("👶 子ども")
num_children = st.number_input("子どもの人数", 0, 5, 0)

children = []

for i in range(num_children):
    st.subheader(f"{i+1}人目の子ども")
    birth_age = st.number_input(f"{i+1}人目の出産年齢", min_value=18, max_value=100, value=30+i*3)

    # 教育イベントは後で自動生成するので、ここでは birth_age だけ保持
    children.append({"birth_age": birth_age})

# -----------------------------
# 教育費（固定ロジック）
# -----------------------------
st.header("🎒 教育費（固定）")
st.write("小→中：20万円、中→高：20万円、高→大：50万円、大学学費：年60万円（4年間）")

# -----------------------------
# 住宅購入
# -----------------------------
st.header("🏠 住宅購入")
house_age = st.number_input("住宅購入年齢", min_value=18, max_value=100, value=35)
house_cost = st.number_input("住宅購入費用（円）", min_value=1000000, step=1000000, value=30000000)
house_down_payment_ratio = 0.2  # デフォルト20%

st.write(f"頭金はデフォルトで {house_down_payment_ratio*100:.0f}% に設定されています。")
import streamlit as st

st.title("ライフイベント設定（人生の順番で入力）")

# -----------------------------
# 車購入（5年ごとに買い替え）
# -----------------------------
st.header("🚗 車購入")
car_first_age = st.number_input("最初の車購入年齢", min_value=18, max_value=100, value=30, key="car_age_input")
car_cost = st.number_input("車購入費用（円）", min_value=100000, step=100000, value=3000000, key="car_cost_input")

# -----------------------------
# 結婚
# -----------------------------
st.header("💍 結婚")
marriage_age = st.number_input("結婚年齢", min_value=18, max_value=100, value=28)
marriage_cost = st.number_input("結婚費用（円）", min_value=100000, step=100000, value=2000000)

# -----------------------------
# 子ども（人数可変）
# -----------------------------
st.header("👶 子ども")
num_children = st.number_input("子どもの人数", 0, 5, 0)

children = []

for i in range(num_children):
    st.subheader(f"{i+1}人目の子ども")
    birth_age = st.number_input(f"{i+1}人目の出産年齢", min_value=18, max_value=100, value=30+i*3)

    # 教育イベントは後で自動生成するので、ここでは birth_age だけ保持
    children.append({"birth_age": birth_age})

# -----------------------------
# 教育費（固定ロジック）
# -----------------------------
st.header("🎒 教育費（固定）")
st.write("小→中：20万円、中→高：20万円、高→大：50万円、大学学費：年60万円（4年間）")

# -----------------------------
# 住宅購入
# -----------------------------
st.header("🏠 住宅購入")
house_age = st.number_input("住宅購入年齢", min_value=18, max_value=100, value=35)
house_cost = st.number_input("住宅購入費用（円）", min_value=1000000, step=1000000, value=30000000)
house_down_payment_ratio = 0.2  # デフォルト20%

st.write(f"頭金はデフォルトで {house_down_payment_ratio*100:.0f}% に設定されています。")
# ----------------------------------------
# Step 3：メインループ（イベント処理・ローン積み上げ）
# ----------------------------------------

value_cash = 0
value_invest = 0
loan_payments = []  # 毎月の返済額を積み上げるリスト

history_cash = []
history_invest = []
history_total = []
ages = []

for age in range(start_age, goal_age + 1):
    for month in range(12):

        years_passed = age - start_age

        # -----------------------------
        # 毎月の支出（年間増減率を反映）
        # -----------------------------
        utilities_month = expense_with_growth(utilities_base, utilities_growth, years_passed)
        comm_month = expense_with_growth(comm_base, comm_growth, years_passed)
        transport_month = expense_with_growth(transport_base, transport_growth, years_passed)
        insurance_month = expense_with_growth(insurance_base, insurance_growth, years_passed)
        misc_month = expense_with_growth(misc_base, misc_growth, years_passed)

        monthly_expenses = (
            housing + food + utilities_month + comm_month +
            transport_month + insurance_month + misc_month
        )

        # -----------------------------
        # ローン返済を支出に加算
        # -----------------------------
        monthly_expenses += sum(loan_payments)

        # -----------------------------
        # 月収入 → 余力
        # -----------------------------
        monthly_income = current_salary
        surplus = monthly_income - monthly_expenses

        # -----------------------------
        # 投資利回り（ランダム変動＋シナリオ）
        # -----------------------------
        rand_factor = random.uniform(-1, 1)
        monthly_rate = (avg_invest_rate + rand_factor * volatility) / 100 / 12

        # -----------------------------
        # 資産更新（現金・投資）
        # -----------------------------
        value_cash = value_cash * (1 + cash_rate/100/12) + surplus * cash_ratio/100
        value_invest = value_invest * (1 + monthly_rate) + surplus * invest_ratio/100

        # -----------------------------
        # ボーナス処理（6月・12月）
        # -----------------------------
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

        # -----------------------------
        # イベント発生チェック
        # -----------------------------
        for event in events:
            if event["age"] == age and month == 6:  # イベントは6月に発生とする

                cost = event["cost"]

                # -----------------------------
                # ローンなしイベント（出産・小中高進学など）
                # -----------------------------
                if not event.get("loan", False):
                    if value_cash >= cost:
                        value_cash -= cost
                    else:
                        value_cash = 0
                    continue

                # -----------------------------
                # ローンありイベント（住宅・車・大学など）
                # -----------------------------
                down_ratio = event.get("down_payment_ratio", 0.2)
                loan_years = event.get("loan_years", 5)

                down_payment = cost * down_ratio

                if value_cash >= down_payment:
                    value_cash -= down_payment
                else:
                    value_cash = 0

                loan_amount = cost - down_payment
                monthly_loan = loan_amount / (loan_years * 12)

                loan_payments.append(monthly_loan)

    # -----------------------------
    # 年末記録
    # -----------------------------
    history_cash.append(value_cash)
    history_invest.append(value_invest)
    history_total.append(value_cash + value_invest)
    ages.append(age)
# ----------------------------------------
# Step 4：グラフ描画（シンプル版）
# ----------------------------------------
fig, ax = plt.subplots(figsize=(10,6))

ax.plot(ages, history_cash, label="現金資産", color="blue")
ax.plot(ages, history_invest, label="投資資産", color="green")
ax.plot(ages, history_total, label="総資産", color="red")

ax.set_xlabel("年齢")
ax.set_ylabel("資産額（円）")
ax.legend()

st.pyplot(fig)

# ----------------------------------------
# 最終結果の表示
# ----------------------------------------
st.subheader("最終結果")

st.write(f"最終的な現金資産：{history_cash[-1]:,.0f} 円")
st.write(f"最終的な投資資産：{history_invest[-1]:,.0f} 円")
st.write(f"最終的な総資産：{history_total[-1]:,.0f} 円")