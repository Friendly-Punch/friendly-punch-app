import streamlit as st
import matplotlib.pyplot as plt
import random

st.header("💰 収入設定")
start_age = st.number_input("開始年齢", 18, 80, 25)
goal_age = st.number_input("終了年齢", start_age+1, 100, 65)
current_salary = st.number_input("月給（手取り 円）", 0, step=10000, value=300000)

bonus_multiplier = st.slider("ボーナス倍率（何か月分）", 0.0, 6.0, 2.5)
bonus_spend_ratio = st.slider("ボーナス支出割合（%）", 0, 100, 30)
bonus_cash_ratio = st.slider("ボーナス現金貯金割合（%）", 0, 100, 40)
bonus_invest_ratio = 100 - bonus_spend_ratio - bonus_cash_ratio
annual_bonus = current_salary * bonus_multiplier * 2

st.header("📦 固定支出設定")

housing = st.number_input("住居費（月額 円）", 0, step=1000, value=80000)
food = st.number_input("食費（月額 円）", 0, step=1000, value=60000)

utilities_base = st.number_input("水道光熱費（月額 円）", 0, step=1000, value=20000)
utilities_growth = st.slider("水道光熱費 年間増減率（%）", -5.0, 10.0, 1.5)

comm_base = st.number_input("通信費（月額 円）", 0, step=1000, value=12000)
comm_growth = st.slider("通信費 年間増減率（%）", -5.0, 10.0, 1.0)

transport_base = st.number_input("交通費（月額 円）", 0, step=1000, value=20000)
transport_growth = st.slider("交通費 年間増減率（%）", -5.0, 10.0, 1.5)

insurance_base = st.number_input("保険料（月額 円）", 0, step=1000, value=30000)
insurance_growth = st.slider("保険料 年間増減率（%）", -5.0, 10.0, 1.0)

misc_base = st.number_input("その他雑費（月額 円）", 0, step=1000, value=50000)
misc_growth = st.slider("その他雑費 年間増減率（%）", -5.0, 10.0, 1.0)

st.header("📈 投資設定")

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

def expense_with_growth(base: float, growth: float, years: int) -> float:
    """
    年間増減率を反映して、指定年数後の支出額を計算する関数。

    Parameters:
    - base: 初年度の支出額（円）
    - growth: 年間増減率（%）
    - years: 開始からの経過年数

    Returns:
    - 増加後の支出額（float）
    """
    return base * ((1 + growth / 100) ** years)

st.header("💼 業種選択（昇給カーブ）")

industry = st.selectbox(
    "あなたの業種を選んでください",
    ["メーカー", "IT・Web", "公務員", "介護・福祉", "飲食・小売"]
)
def salary_growth_manufacturer(age):
    if age < 30:
        return 3.0
    elif age < 45:
        return 2.0
    elif age < 55:
        return 1.0
    else:
        return 0.5

def salary_growth_it(age):
    if age < 30:
        return 5.0
    elif age < 45:
        return 3.0
    elif age < 55:
        return 1.5
    else:
        return 1.0

def salary_growth_public(age):
    if age < 40:
        return 1.5
    elif age < 55:
        return 1.0
    else:
        return 0.5

def salary_growth_care(age):
    if age < 40:
        return 1.0
    elif age < 55:
        return 0.8
    else:
        return 0.5

def salary_growth_retail(age):
    if age < 40:
        return 1.0
    elif age < 55:
        return 0.5
    else:
        return 0.0
def get_salary_growth(age, industry):
    if industry == "メーカー":
        return salary_growth_manufacturer(age)
    elif industry == "IT・Web":
        return salary_growth_it(age)
    elif industry == "公務員":
        return salary_growth_public(age)
    elif industry == "介護・福祉":
        return salary_growth_care(age)
    elif industry == "飲食・小売":
        return salary_growth_retail(age)
    return 0

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

# ----------------------------------------
# Step 2：イベントリスト生成
# ----------------------------------------

events = []

# -----------------------------
# 車購入（5年ごと）
# -----------------------------
age = car_first_age
while age <= goal_age:
    events.append({
        "type": "car",
        "age": age,
        "cost": car_cost,
        "loan": True,
        "loan_years": 5
    })
    age += 5

# -----------------------------
# 結婚
# -----------------------------
events.append({
    "type": "marriage",
    "age": marriage_age,
    "cost": marriage_cost,
    "loan": True,
    "loan_years": 5
})

# -----------------------------
# 子ども（人数分）
# -----------------------------
for i, child in enumerate(children):
    birth_age = child["birth_age"]

    # 出産イベント（費用なし）
    events.append({
        "type": "birth",
        "age": birth_age,
        "cost": 0,
        "loan": False
    })

    # 小→中（12歳）
    events.append({
        "type": "edu_small_to_junior",
        "age": birth_age + 12,
        "cost": 200000,
        "loan": False
    })

    # 中→高（15歳）
    events.append({
        "type": "edu_junior_to_high",
        "age": birth_age + 15,
        "cost": 200000,
        "loan": False
    })

    # 高→大（18歳）
    events.append({
        "type": "edu_high_to_univ",
        "age": birth_age + 18,
        "cost": 500000,
        "loan": True,
        "loan_years": 10
    })

    # 大学学費（18〜21歳の4年間）
    for y in range(4):
        events.append({
            "type": "univ_tuition",
            "age": birth_age + 18 + y,
            "cost": 600000,
            "loan": True,
            "loan_years": 10
        })

# -----------------------------
# 住宅購入（頭金20%）
# -----------------------------
events.append({
    "type": "house",
    "age": house_age,
    "cost": house_cost,
    "down_payment_ratio": house_down_payment_ratio,
    "loan": True,
    "loan_years": 30
})

# ----------------------------------------
# イベントを年齢順にソート
# ----------------------------------------
events = sorted(events, key=lambda x: x["age"])

# デバッグ表示（任意）
st.subheader("生成されたイベント一覧（デバッグ用）")
for e in events:
    st.write(e)

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
        growth_rate = get_salary_growth(age, industry)
        monthly_income = current_salary * ((1 + growth_rate / 100) ** (age - start_age))
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