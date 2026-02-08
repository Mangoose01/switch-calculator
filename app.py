import streamlit as st
import pandas as pd
import altair as alt

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Making the Switch?",
    page_icon="📈",
    layout="centered"
)

# 2. CUSTOM CSS (The Polish)
st.markdown("""
    <style>
        /* 1. CONTAINER WIDTH ADJUSTMENT */
        .block-container {
            max-width: 1000px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        
        /* 2. COLORS & THEME */
        .stApp { background-color: #ffffff; color: #1e293b; }
        
        /* 3. HIDE STREAMLIT UI */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* 4. TYPOGRAPHY */
        h1 { color: #1e293b; font-weight: 800; letter-spacing: -0.02em; padding-bottom: 0px; }
        h3 { color: #334155; font-size: 1.2rem; font-weight: 600; margin-top: 20px; }
        p { color: #475569; font-size: 1rem; line-height: 1.6; }
        
        /* 5. INPUTS */
        .stSelectbox label, .stNumberInput label { font-weight: 600; color: #475569; }
    </style>
""", unsafe_allow_html=True)

# 3. HEADER & EDUCATION
st.markdown("<h1 style='text-align: center;'>Making the Switch?</h1>", unsafe_allow_html=True)
st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

st.markdown("""
**What does "Making the Switch" mean?** Most Canadian investors pay for financial advice via **Assets Under Management (AUM)** (that's *in addition to* investment management fees, which is a whole other topic...). This means they pay a percentage of their portfolio (usually 1% or more) every single year specifically for financial planning advice. As the market goes up and their wealth increases, the fee grows, even if the level of advice and service stay the same.

**The Advice-Only Model** (a.k.a. fee-only) treats financial planning like a professional service (like a CPA or Lawyer). You pay a flat fee for the advice you receive, decoupling the cost from the value of your portfolio and instead aligning it with the complexity of your situation.
""")

st.info("""
**About the tool belows:** This chart demonstrates the stark difference between the two models from a cost perspective over time, assuming the **exact same level of advice** is received. Use it to determine your "breakeven point", the moment where switching to an advice-only model starts putting significantly more money back in your pocket.

It should be noted that the advice-only fees (financial plan and annual reviews) referenced in these calculations are reflective of non-complex financial plans, which the author estimates applies to 85% of individuals seeking to build a financial plan. More complex scenarios involving corporations, foreign tax obligations, many rental properties, etc. would very likely result in higher advice-only costs. You can change the default advice fee in the calculations to be reflective of your circumstances and the corresponding advice-only pricing. See detailed assumptions made at the bottom of the page.

This chart uses a triennial structure for the financial plan update fees (an update every 3 years) as it tends to be the industry standard at financial institution and full brokerage firms. An annual meeting is however included (which is also an industry standard) although it is added as a default optional feature in the chart below.
""")

st.divider()

# 4. INPUTS
col1, col2 = st.columns(2)

with col1:
    balance = st.number_input("Investable Assets ($)", value=500000, step=10000)
    firm_options = [
        "Most Common (1.00% - Common Bank Mutual Funds)",
        "High (1.25% - Mainstream Brokers - it sometimes includes investment management)",
        "Low (0.75% - High Net Worth / Discounted Wealth Management)"
    ]
    firm_type = st.selectbox("Current Trailing Commission Structure", options=firm_options, index=0)

with col2:
    st.write("Time Horizon")
    horizon = st.radio("Time Horizon", [10, 20, 30], index=1, horizontal=True, label_visibility="collapsed")
    st.write("") 
    include_reviews = st.checkbox("Include Annual Review Costs?", value=True)

# --- NEW: CUSTOM FEE INPUTS ---
# We use an expander to keep the UI clean, but allow customization if clicked.
with st.expander("🔧 Customize Advice-Only Fees (Click to Edit)"):
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        plan_fee = st.number_input("Triennial Plan Fee ($)", value=1000, step=100, help="The cost of the initial plan and the update every 3 years.")
    with f_col2:
        review_fee = st.number_input("Annual Review Fee ($)", value=250, step=50, help="The cost of the optional maintenance review in off-years.")

# 5. LOGIC ENGINE
if "0.75%" in firm_type: trail = 0.0075
elif "1.25%" in firm_type: trail = 0.0125
else: trail = 0.01

# --- UPDATED CONSTANTS (Conservative 5% Growth) ---
growth_rate = 1.05       # 5% Growth
inflation = 1.025        # 2.5% Inflation on fees
hst_rate = 1.13          # 13% HST

data = []
area_data = []

aum_bal = balance
adv_bal = balance
curr_plan_fee = plan_fee # Takes value from the new input
curr_rev_fee = review_fee # Takes value from the new input

for year in range(horizon + 1):
    if year > 0:
        # 1. Growth
        aum_bal = aum_bal * growth_rate
        adv_bal = adv_bal * growth_rate
        
        # 2. AUM Fee deduction (Percentage)
        aum_bal = aum_bal * (1 - trail)
        
        # 3. Advice Fee deduction (Flat Fees + HST)
        if include_reviews:
            # Annual Review Fee (Every Year)
            adv_bal -= (curr_rev_fee * hst_rate)
            
        # Triennial Plan Fee (Year 1, 4, 7...)
        if (year - 1) % 3 == 0:
            adv_bal -= (curr_plan_fee * hst_rate)
            
        # 4. Inflation Adjustment
        curr_plan_fee *= inflation
        curr_rev_fee *= inflation

    data.append({"Year": year, "Portfolio Value": round(aum_bal), "Type": "Traditional AUM"})
    data.append({"Year": year, "Portfolio Value": round(adv_bal), "Type": "Advice-Only"})
    
    # Wide format for the area chart
    area_data.append({
        "Year": year, 
        "Traditional AUM": round(aum_bal), 
        "Advice-Only": round(adv_bal)
    })

df_lines = pd.DataFrame(data)
df_area = pd.DataFrame(area_data)

final_aum = df_lines[(df_lines["Year"] == horizon) & (df_lines["Type"] == "Traditional AUM")]["Portfolio Value"].values[0]
final_adv = df_lines[(df_lines["Year"] == horizon) & (df_lines["Type"] == "Advice-Only")]["Portfolio Value"].values[0]
savings = final_adv - final_aum

st.markdown("---")

# 6. METRIC DISPLAY (CUSTOM HTML FIX)
st.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <div style="font-size: 1.4rem; color: #64748b; font-weight: 600; margin-bottom: 5px;">
            Additional Wealth Retained
        </div>
        <div style="font-size: 4.5rem; color: #10b981; font-weight: 900; line-height: 1;">
            ${savings:,.0f}
        </div>
    </div>
""", unsafe_allow_html=True)

# 7. PROFESSIONAL CHART (Locked & Fixed Tooltips)
# Layer 1: Area (Disabled Tooltip)
area = alt.Chart(df_area).mark_area(opacity=0.15, color='#6366f1').encode(
    x=alt.X('Year', axis=alt.Axis(tickMinStep=2, grid=False)),
    y=alt.Y('Traditional AUM', axis=alt.Axis(format='$,.0f', title='Portfolio Value')),
    y2='Advice-Only',
    tooltip=[] 
)

# Layer 2: Lines (Enabled Tooltip)
lines = alt.Chart(df_lines).mark_line(strokeWidth=4).encode(
    x='Year',
    y='Portfolio Value',
    color=alt.Color('Type', scale=alt.Scale(domain=['Advice-Only', 'Traditional AUM'], range=['#6366f1', '#ca8a04']), legend=alt.Legend(orient="bottom", title=None)),
    tooltip=[
        alt.Tooltip('Year'), 
        alt.Tooltip('Portfolio Value', format='$,.0f'), 
        alt.Tooltip('Type')
    ]
)

# Combine & Lock Interaction
final_chart = (area + lines).properties(
    height=500, 
    background='white'
).configure_axis(
    labelFontSize=12,
    titleFontSize=13,
    grid=True,
    gridColor='#f1f5f9'
).configure_view(
    strokeWidth=0
).interactive(bind_y=False, bind_x=False)

st.altair_chart(final_chart, use_container_width=True)

# 8. FOOTER
# Updated to use the variables directly from the inputs
with st.expander("📝 View Calculation Assumptions"):
    st.markdown(f"""
    This calculator uses conservative estimates to project long-term costs.
    * **Market Growth:** {round((growth_rate-1)*100)}% annually (compounded).
    * **Inflation:** {round((inflation-1)*100)}% annually (applied to Advice fees).
    * **Trailing Commissions:** Applied annually to the full account balance.
    * **Advice-Only Costs:** * Initial/Triennial Plan: **${plan_fee:,.0f}** (indexed to inflation) + 13% HST.
        * Annual Review: **${review_fee:,.0f}** (indexed to inflation, optional) + 13% HST.
    * *Note: This is a projection for illustrative purposes and does not guarantee future returns.*
    """)


