import streamlit as st
import pandas as pd
import altair as alt

# 1. Config & Style
st.set_page_config(page_title="Make The Switch", page_icon="💸")

# Hide standard Streamlit chrome for a cleaner look
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .css-18e3th9 {padding-top: 0rem;}
    .stApp {background-color: white;}
    </style>
    """, unsafe_allow_html=True)

# 2. The Header
st.title("💸 Make The Switch")
st.markdown("See how much wealth you are losing to hidden trailing commissions.")

# 3. Sidebar Inputs (or Top inputs)
col1, col2 = st.columns(2)

with col1:
    balance = st.number_input("Investable Assets ($)", value=500000, step=10000)
    firm_type = st.selectbox(
        "Current Firm Fee Structure",
        options=["Big Bank (1.0% Hidden Trail)", "Full Service (0.75% Trail)", "High Fee Mutual Fund (2.0%)", "Independent (0.50%)"],
        index=0
    )

with col2:
    horizon = st.radio("Time Horizon", [10, 20, 30], index=1, horizontal=True)
    include_reviews = st.checkbox("Include Annual Review Costs?", value=True)

# 4. The Logic Engine
# Extract fee percentage from the string
if "1.0%" in firm_type: trail = 0.01
elif "0.75%" in firm_type: trail = 0.0075
elif "2.0%" in firm_type: trail = 0.02
else: trail = 0.005

# Constants
growth_rate = 1.06  # 6%
inflation = 1.02    # 2%
plan_fee = 3500     # Every 3 years
review_fee = 200    # Annual

# Calculation Loop
data = []
aum_bal = balance
adv_bal = balance
curr_plan_fee = plan_fee
curr_rev_fee = review_fee

for year in range(horizon + 1):
    if year > 0:
        # Market Growth
        aum_bal = aum_bal * growth_rate
        adv_bal = adv_bal * growth_rate
        
        # AUM Fee Deduction (The Trail)
        aum_bal = aum_bal * (1 - trail)
        
        # Advice-Only Fee Deduction
        if include_reviews:
            adv_bal -= curr_rev_fee
        
        if year % 3 == 0:
            adv_bal -= curr_plan_fee
        
        # Inflation
        curr_plan_fee *= inflation
        curr_rev_fee *= inflation

    data.append({"Year": year, "Portfolio Value": round(aum_bal), "Type": "Traditional AUM"})
    data.append({"Year": year, "Portfolio Value": round(adv_bal), "Type": "Advice-Only"})

# 5. The Results
df = pd.DataFrame(data)
final_aum = df[(df["Year"] == horizon) & (df["Type"] == "Traditional AUM")]["Portfolio Value"].values[0]
final_adv = df[(df["Year"] == horizon) & (df["Type"] == "Advice-Only")]["Portfolio Value"].values[0]
savings = final_adv - final_aum

st.markdown("---")
st.metric(label=f"Additional Wealth Retained over {horizon} Years", value=f"${savings:,.0f}")

# 6. The Chart (Altair)
chart = alt.Chart(df).mark_line(strokeWidth=4).encode(
    x=alt.X("Year", axis=alt.Axis(tickMinStep=1)),
    y=alt.Y("Portfolio Value", axis=alt.Axis(format="$,.0f")),
    color=alt.Color("Type", scale=alt.Scale(domain=['Advice-Only', 'Traditional AUM'], range=['#6366f1', '#ca8a04'])),
    tooltip=["Year", "Type", alt.Tooltip("Portfolio Value", format="$,.0f")]
).properties(
    height=400
).interactive()

st.altair_chart(chart, use_container_width=True)

# 7. Call to Action
st.info("Ready to stop losing money? Book your free discovery call below.")
st.link_button("Book a Call", "https://your-booking-link.com")