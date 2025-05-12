import streamlit as st
import math
import plotly.express as px
from datetime import datetime

# Constants
USDINR_RATE = 85
USDINR_LOT_SIZE = 1000  # One lot = $1000
MARGIN_PER_LOT = 2150  # INR per lot
HISTORICAL_VOLATILITY = 8.5  # Annualized % volatility for USDINR

# Page configuration
st.set_page_config(page_title="Advanced Bond Investment Dashboard", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stNumberInput, .stSelectbox {
        margin-bottom: 20px;
    }
    .metric-box {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .header {
        color: #2c3e50;
    }
    .highlight {
        color: #3498db;
        font-weight: bold;
    }
    .negative {
        color: #e74c3c;
    }
    .positive {
        color: #2ecc71;
    }
    .scenario-box {
        border-left: 4px solid #3498db;
        padding-left: 15px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("💰 Advanced Bond Investment Dashboard")
st.markdown("""
Comprehensive analysis of bond investments with USDINR currency hedging and risk assessment.
""")

# Create columns for layout
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📊 Investment Parameters")
    with st.container():
        investment_inr = st.number_input("**Investment Amount (INR)**", min_value=1000, step=1000, value=1000000)
        tenure_years = st.selectbox("**Tenure (Years)**", [1, 2, 3, 4, 5], index=2)
        yield_percent = st.number_input("**Annual Yield (%)**", min_value=0.0, step=0.1, value=6.5)

with col2:
    st.header("⚙️ Hedging Parameters")
    with st.container():
        st.markdown(f"**Current USD/INR Rate:** {USDINR_RATE}")
        st.markdown(f"**USDINR Lot Size:** ${USDINR_LOT_SIZE}")
        st.markdown(f"**Margin Requirement per Lot:** ₹{MARGIN_PER_LOT}")
        forex_change_pct = st.slider("**Forex Scenario (% USD/INR change)**", -20.0, 20.0, 0.0, 0.5)

# Calculate returns
interest_earned = investment_inr * (yield_percent / 100) * tenure_years
total_return_inr = investment_inr + interest_earned

# USD Conversion
investment_usd = investment_inr / USDINR_RATE

# Hedging Calculations
num_lots = math.ceil(investment_usd / USDINR_LOT_SIZE)
total_margin_inr = num_lots * MARGIN_PER_LOT
actual_return_with_hedging = total_return_inr - total_margin_inr

# Return Percentages
return_pct_without_hedging = ((total_return_inr - investment_inr) / investment_inr) * 100
return_pct_with_hedging = ((actual_return_with_hedging - investment_inr) / investment_inr) * 100
hedging_cost_pct = (total_margin_inr / investment_inr) * 100

# --------------------------
# 1. Forex Risk Analysis
# --------------------------
st.markdown("---")
st.header("🌍 Forex Risk Analysis")

scenario_rate = USDINR_RATE * (1 + forex_change_pct/100)
unhedged_scenario_return = (investment_usd * scenario_rate) + interest_earned
forex_impact = unhedged_scenario_return - total_return_inr

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Unhedged Scenario Return", f"₹{unhedged_scenario_return:,.2f}", 
              f"{(unhedged_scenario_return/investment_inr-1)*100:.2f}%")

with col2:
    st.metric("Forex Impact", f"₹{forex_impact:,.2f}", 
              f"{(forex_impact/investment_inr)*100:.2f}%")

with col3:
    st.metric("Hedged Scenario Return", f"₹{actual_return_with_hedging:,.2f}", 
              f"{return_pct_with_hedging:.2f}%")

# Historical volatility analysis
st.subheader("Historical Volatility Analysis")
st.markdown(f"""
- **1-year historical volatility:** {HISTORICAL_VOLATILITY}%
- **Probable range after {tenure_years} year(s): ±{HISTORICAL_VOLATILITY*math.sqrt(tenure_years):.1f}%
- **95% confidence range:** {USDINR_RATE*(1-HISTORICAL_VOLATILITY/100*math.sqrt(tenure_years)*1.96):.2f} to {USDINR_RATE*(1+HISTORICAL_VOLATILITY/100*math.sqrt(tenure_years)*1.96):.2f}
""")

# --------------------------
# 2. Comparative Analysis
# --------------------------
st.markdown("---")
st.header("📊 Comparative Analysis")

alt_returns = {
    "Strategy": ["Unhedged Bonds", "Hedged Bonds", "Fixed Deposit", "Nifty 50", "Gold"],
    "Return (%)": [return_pct_without_hedging, return_pct_with_hedging, 6.5, 12.0, 9.2],
    "Risk": ["High", "Medium", "Low", "High", "Medium"]
}

fig = px.bar(alt_returns, x="Strategy", y="Return (%)", color="Risk",
             title="Comparative Returns Across Strategies",
             color_discrete_map={"High": "#e74c3c", "Medium": "#f39c12", "Low": "#2ecc71"})
st.plotly_chart(fig, use_container_width=True)

# --------------------------
# 3. Time Value of Money
# --------------------------
st.markdown("---")
st.header("⏳ Time Value of Money")

inflation_rate = st.slider("Expected inflation rate (%)", 2.0, 10.0, 6.0, 0.1)
real_return_hedged = ((1 + return_pct_with_hedging/100) / (1 + inflation_rate/100) - 1) * 100
real_return_unhedged = ((1 + return_pct_without_hedging/100) / (1 + inflation_rate/100) - 1) * 100

col1, col2 = st.columns(2)
with col1:
    st.metric("Nominal Return (Hedged)", f"{return_pct_with_hedging:.2f}%")
    st.metric("Real Return (Hedged)", f"{real_return_hedged:.2f}%", 
              delta_color="inverse" if real_return_hedged < 0 else "normal")

with col2:
    st.metric("Nominal Return (Unhedged)", f"{return_pct_without_hedging:.2f}%")
    st.metric("Real Return (Unhedged)", f"{real_return_unhedged:.2f}%", 
              delta_color="inverse" if real_return_unhedged < 0 else "normal")

# --------------------------
# 4. Risk Metrics
# --------------------------
st.markdown("---")
st.header("⚠️ Risk Metrics")

historical_max_drop = -15.7  # Worst 1-year USD/INR change
stress_return = (investment_usd * USDINR_RATE * (1 + historical_max_drop/100)) + interest_earned
var_95 = investment_inr * (return_pct_without_hedging/100 - 1.96*HISTORICAL_VOLATILITY/100)

st.markdown(f"""
- **Value at Risk (95% confidence):** ₹{max(0, var_95):,.2f}
- **Stress Scenario Return (2008-like):** ₹{stress_return:,.2f} ({(stress_return/investment_inr-1)*100:.2f}%)
- **Sharpe Ratio (vs risk-free):** {(return_pct_with_hedging/100 - 0.065)/ (HISTORICAL_VOLATILITY/100):.2f}
""")

# --------------------------
# 5. Advanced Hedging Analytics
# --------------------------
st.markdown("---")
st.header("📈 Advanced Hedging Analytics")

hedge_efficiency = min(1, (num_lots * USDINR_LOT_SIZE) / investment_usd) * 100
optimal_lots = math.floor(investment_usd / USDINR_LOT_SIZE)
optimal_hedge_return = total_return_inr - (optimal_lots * MARGIN_PER_LOT)

st.markdown(f"""
- **Hedge Efficiency:** {hedge_efficiency:.1f}% of exposure covered
- **Optimal Lot Strategy:** {optimal_lots} lots (covers ${optimal_lots * USDINR_LOT_SIZE:,.0f})
- **Optimal Hedge Return:** ₹{optimal_hedge_return:,.2f} ({(optimal_hedge_return/investment_inr-1)*100:.2f}%)
""")

# --------------------------
# 6. Visualization Enhancements
# --------------------------
st.markdown("---")
st.header("📊 Scenario Analysis Visualizations")

# Create scenario data
scenarios = {
    "Scenario": ["Worst Case (-15%)", "Bear Case (-7.5%)", "Neutral (0%)", 
                 "Bull Case (+7.5%)", "Best Case (+15%)"],
    "USD/INR Rate": [USDINR_RATE*0.85, USDINR_RATE*0.925, USDINR_RATE, 
                     USDINR_RATE*1.075, USDINR_RATE*1.15],
    "Unhedged Return": [
        (investment_usd * USDINR_RATE*0.85 + interest_earned)/investment_inr*100-100,
        (investment_usd * USDINR_RATE*0.925 + interest_earned)/investment_inr*100-100,
        return_pct_without_hedging,
        (investment_usd * USDINR_RATE*1.075 + interest_earned)/investment_inr*100-100,
        (investment_usd * USDINR_RATE*1.15 + interest_earned)/investment_inr*100-100
    ],
    "Hedged Return": [return_pct_with_hedging]*5
}

fig = px.line(scenarios, x="Scenario", y=["Unhedged Return", "Hedged Return"],
              title="Return Scenarios Under Different Forex Conditions",
              labels={"value": "Return (%)", "variable": "Strategy"},
              markers=True)
st.plotly_chart(fig, use_container_width=True)

# Waterfall chart
waterfall_data = {
    "Measure": ["Initial Investment", "Interest Earned", "Forex Impact", "Hedging Cost", "Final Value"],
    "Value": [investment_inr, interest_earned, forex_impact, -total_margin_inr, actual_return_with_hedging]
}

fig = px.waterfall(waterfall_data, x="Measure", y="Value", 
                   title="Investment Value Waterfall")
st.plotly_chart(fig, use_container_width=True)

# --------------------------
# Main Results Display
# --------------------------
st.markdown("---")
st.header("📌 Summary Results")

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Return Without Hedging", 
              f"₹{total_return_inr:,.2f}", 
              f"{return_pct_without_hedging:.2f}%")

with col2:
    st.metric("Total Return With Hedging", 
              f"₹{actual_return_with_hedging:,.2f}", 
              f"{return_pct_with_hedging:.2f}%")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #7f8c8d; font-size: 0.8em;">
    <p>Dashboard last updated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Note: This is for analytical purposes only. Consult a financial advisor before making investment decisions.</p>
</div>
""", unsafe_allow_html=True)
