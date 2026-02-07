import streamlit as st
import pandas as pd
import altair as alt

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Make The Switch",
    page_icon="🛡️",
    layout="centered"
)

# 2. CUSTOM CSS (Professional Polish)
st.markdown("""
    <style>
        /* Force Clean White Background */
        .stApp { background-color: #ffffff; color: #1e293b; }
        
        /* Hide Streamlit Chrome */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Typography */
        h1 { color: #1e293b; font-weight: 800; letter-spacing: -0.02em; padding-bottom: 10px; }
        h3 { color: #334155; font-size: 1.2rem; font-weight: 600; margin-top: 20px; }
        p { color: #475569; font-size: 1rem; line-height: 1.6; }
        
        /* Big Metric Style */
        div[data-testid="stMetricValue"] {
            font-size: 4rem !important;
            color: #10b981 !important; /* Green */
            font-weight: 900;
            text-align: center;
        }
        div[data-testid="stMetricLabel"] {
            text-align: center; font-size: 1.1rem !important; color: #64748b !important;
        }
        
        /* Input Styling */
        .stSelectbox label, .stNumberInput label { font-weight: 600; color: #475569; }
        
        /* Container Spacing */
        .block-container { padding-top: 3rem; padding-bottom: 3rem; }
    </style>
""", unsafe_allow_html=True)

# 3. HEADER & EDUCATION
st.title("🛡️ Make The Switch")

st.markdown("""
**What does "Making the Switch" mean?** Most Canadian investors pay for advice via **Assets Under Management (AUM)**. This means you pay a percentage of your portfolio (often 1% or more) every single year. As your wealth grows, your fee grows—even if the service stays the same.

**The Advice-Only Model** treats financial planning like a professional service (like a CPA or Lawyer). You pay a flat fee for the advice you receive, decoupling the cost from your net worth. 
""")

st.divider()

# 4. INPUTS
col1, col2 = st.columns(2)

with col1:
    balance = st.number_input("Investable Assets ($)", value=630000, step=10000)
    firm_options = [
        "Most Common (1.00% - Bank Mutual Funds)",
        "High (1.25% - Mainstream Brokers)",
        "Low (0.75% - High Net Worth / F-Class)"
    ]
    firm_type = st.selectbox("Current Trailing Commission Structure", options=firm_options, index=0)

with col2:
    st.write("Time Horizon")
    # Custom CSS hack to align the radio button nicely
    horizon = st.radio("Time Horizon", [10, 20, 30], index=1, horizontal=True, label_visibility="collapsed")
    st.write("") # Visual spacer
    include_reviews = st.checkbox("Include Annual Review Costs?", value=True)

# 5. LOGIC ENGINE
# Map selection to fee
if "0.75%" in firm_type: trail = 0.0075
elif "1.25%" in firm_type: trail = 0.0125
else: trail = 0.01  # Default to 1.00%

# Assumptions
growth_rate = 1.06      # 6% Market Return
inflation = 1.02        # 2% Inflation
plan_fee = 3500         # Triennial Plan Cost
review_fee = 200        # Annual Review Cost

# Calculation Loop
data = []
# We need a separate list for the area chart (wide format)
area_data = []

aum_bal = balance
adv_bal = balance
curr_plan_fee = plan_fee
curr_rev_fee = review_fee

for year in range(horizon + 1):
    if year > 0:
        # 1. Growth
        aum_bal = aum_bal * growth_rate
        adv_bal = adv_bal * growth_rate
        
        # 2. AUM Fee (Percentage)
        aum_bal = aum_bal * (1 - trail)
        
        # 3. Advice Fee (Flat)
        if include_reviews:
            adv_bal -= curr_rev_fee
        if year % 3 == 0:
            adv_bal -= curr_plan_fee
            
        # 4. Inflation on Fees
        curr_plan_fee *= inflation
        curr_rev_fee *= inflation

    # Store for Line Chart (Long format)
    data.append({"Year": year, "Portfolio Value": round(aum_bal), "Type": "Traditional AUM"})
    data.append({"Year": year, "Portfolio Value": round(adv_bal), "Type": "Advice-Only"})
    
    # Store for Area Chart (Wide format)
    area_data.append({"Year": year, "Traditional": round(aum_bal), "AdviceOnly": round(adv_bal)})

# 6. METRIC DISPLAY
df_lines = pd.DataFrame(data)
df_area = pd.DataFrame(area_data)

final_aum = df_lines[(df_lines["Year"] == horizon) & (df_lines["Type"] == "Traditional AUM")]["Portfolio Value"].values[0]
final_adv = df_lines[(df_lines["Year"] == horizon) & (df_lines["Type"] == "Advice-Only")]["Portfolio Value"].values[0]
savings = final_adv - final_aum

st.markdown("---")
m_c1, m_c2, m_c3 = st.columns([1,4,1])
with m_c2:
    st.metric(label="Additional Wealth Retained", value=f"${savings:,.0f}")

# 7. PROFESSIONAL CHART (Layered)
# Layer 1: The Shaded Area (The Gap)
area = alt.Chart(df_area).mark_area(opacity=0.15, color='#6366f1').encode(
    x=alt.X('Year', axis=alt.Axis(tickMinStep=2, grid=False)),
    y=alt.Y('Traditional', axis=alt.Axis(format='$,.0f', title='Portfolio Value')),
    y2='AdviceOnly'
)

# Layer 2: The Lines
lines = alt.Chart(df_lines).mark_line(strokeWidth=4).encode(
    x='Year',
    y='Portfolio Value',
    color=alt.Color('Type', scale=alt.Scale(domain=['Advice-Only', 'Traditional AUM'], range=['#6366f1', '#ca8a04']), legend=alt.Legend(orient="bottom", title=None)),
    tooltip=[alt.Tooltip('Year'), alt.Tooltip('Portfolio Value', format='$,.0f'), alt.Tooltip('Type')]
)

# Combine
final_chart = (area + lines).properties(
    height=500, # Taller as requested
    background='white'
).configure_axis(
    labelFontSize=12,
    titleFontSize=13,
    grid=True,
    gridColor='#f1f5f9'
).configure_view(
    strokeWidth=0
).interactive()

st.altair_chart(final_chart, use_container_width=True)

# 8. TRANSPARENCY & FOOTER
with st.expander("📝 View Calculation Assumptions"):
    st.markdown(f"""
    This calculator uses conservative estimates to project long-term costs.
    * **Market Growth:** {round((growth_rate-1)*100)}% annually (compounded).
    * **Inflation:** {round((inflation-1)*100)}% annually (applied to Advice fees).
    * **Trailing Commissions:** Applied annually to the full account balance.
    * **Advice-Only Costs:**
        * Initial/Triennial Plan: ${plan_fee:,.0f} (adjusted for inflation).
        * Annual Review: ${review_fee:,.0f} (adjusted for inflation, optional).
    * *Note: This is a projection for illustrative purposes and does not guarantee future returns.*
    """)
