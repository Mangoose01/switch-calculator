import streamlit as st
import pandas as pd
import altair as alt

# 1. PAGE CONFIGURATION (Force Light Mode & Title)
st.set_page_config(
    page_title="Make The Switch Calculator",
    page_icon="💸",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. CUSTOM CSS (The "Polish")
# This hides the top bar, footer, and styles the big number
st.markdown("""
    <style>
        /* Force Light Background */
        .stApp {
            background-color: #ffffff;
            color: #1e293b;
        }
        
        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Style the Header */
        h1 {
            color: #1e293b;
            font-family: -apple-system, sans-serif;
            font-weight: 800;
            text-align: center;
            padding-bottom: 20px;
        }
        
        /* Style the Big Metric */
        div[data-testid="stMetricValue"] {
            font-size: 3.5rem !important;
            color: #10b981 !important; /* Green */
            font-weight: 900;
            text-align: center;
        }
        div[data-testid="stMetricLabel"] {
            text-align: center;
            font-size: 1rem !important;
            color: #64748b !important;
            font-weight: 600;
        }
        
        /* Center the chart */
        canvas {
            margin: 0 auto;
        }
        
        /* Custom Button Style */
        .stButton button {
            background-color: #1e293b;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            border: none;
            width: 100%;
        }
        .stButton button:hover {
            background-color: #334155;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# 3. HEADER
st.title("💸 Make The Switch")
st.markdown(
    "<div style='text-align: center; color: #64748b; margin-bottom: 30px;'>See exactly how much wealth you are losing to hidden trailing commissions.</div>", 
    unsafe_allow_html=True
)

# 4. INPUTS (Card Style)
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        balance = st.number_input("Investable Assets ($)", value=500000, step=10000)
        firm_type = st.selectbox(
            "Current Firm Fee Structure",
            options=["Big Bank (1.0% Hidden Trail)", "Full Service (0.75% Trail)", "High Fee Mutual Fund (2.0%)", "Independent (0.50%)"],
            index=0
        )

    with col2:
        # Custom Horizontal Radio Button
        st.write("Time Horizon")
        horizon = st.radio("Time Horizon", [10, 20, 30], index=1, horizontal=True, label_visibility="collapsed")
        st.write("") # Spacer
        include_reviews = st.checkbox("Include Annual Review Costs?", value=True)

# 5. LOGIC ENGINE
# Extract fee
if "1.0%" in firm_type: trail = 0.01
elif "0.75%" in firm_type: trail = 0.0075
elif "2.0%" in firm_type: trail = 0.02
else: trail = 0.005

# Constants
growth_rate = 1.06  # 6%
inflation = 1.02    # 2%
plan_fee = 3500     # Every 3 years
review_fee = 200    # Annual

# Loop
data = []
aum_bal = balance
adv_bal = balance
curr_plan_fee = plan_fee
curr_rev_fee = review_fee

for year in range(horizon + 1):
    if year > 0:
        aum_bal = aum_bal * growth_rate * (1 - trail)
        
        if include_reviews:
            adv_bal -= curr_rev_fee
        if year % 3 == 0:
            adv_bal -= curr_plan_fee
            
        adv_bal = adv_bal * growth_rate
        
        curr_plan_fee *= inflation
        curr_rev_fee *= inflation

    data.append({"Year": year, "Portfolio Value": round(aum_bal), "Type": "Traditional AUM"})
    data.append({"Year": year, "Portfolio Value": round(adv_bal), "Type": "Advice-Only"})

# 6. RESULTS & METRIC
df = pd.DataFrame(data)
final_aum = df[(df["Year"] == horizon) & (df["Type"] == "Traditional AUM")]["Portfolio Value"].values[0]
final_adv = df[(df["Year"] == horizon) & (df["Type"] == "Advice-Only")]["Portfolio Value"].values[0]
savings = final_adv - final_aum

st.markdown("---")

# Use columns to center the metric visually
m_col1, m_col2, m_col3 = st.columns([1,2,1])
with m_col2:
    st.metric(label=f"Additional Wealth Retained", value=f"${savings:,.0f}")

# 7. CHART (Clean & Branded)
# Define colors: Purple (Advice) vs Gold (Bank)
domain = ["Advice-Only", "Traditional AUM"]
range_ = ["#6366f1", "#ca8a04"]

chart = alt.Chart(df).mark_line(strokeWidth=4).encode(
    x=alt.X("Year", axis=alt.Axis(tickMinStep=5, grid=False, domain=False)),
    y=alt.Y("Portfolio Value", axis=alt.Axis(format="$,.0f", grid=True, domain=False)),
    color=alt.Color("Type", scale=alt.Scale(domain=domain, range=range_), legend=alt.Legend(orient="bottom", title=None)),
    tooltip=["Year", "Type", alt.Tooltip("Portfolio Value", format="$,.0f")]
).properties(
    height=350,
    background='#ffffff'
).configure_view(
    strokeWidth=0  # Removes the border box around the chart
).configure_axis(
    labelFontSize=12,
    titleFontSize=14,
    labelColor="#64748b",
    titleColor="#64748b"
).interactive()

st.altair_chart(chart, use_container_width=True)

# 8. CALL TO ACTION
st.markdown("<br>", unsafe_allow_html=True)
st.info("💡 **Ready to stop losing money?** Book your free discovery call below.")
# Link button is new in Streamlit
st.link_button("Book a Call", "https://your-booking-link.com", use_container_width=True)
