import streamlit as st
import math
from datetime import datetime
import plotly.express as px
import pandas as pd

# Constants
USDINR_LOT_SIZE = 1000  # One lot = $1000
DEFAULT_USDINR_RATE = 85.0
DEFAULT_MARGIN_PER_LOT = 2150  # INR per lot
DEFAULT_HEDGING_COST_PCT = 0.5  # Annual hedging cost as % of notional

# Page configuration
st.set_page_config(
    page_title="Bond Investment & Hedging Dashboard", 
    layout="wide", 
    page_icon="📊"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stNumberInput, .stSelectbox, .stSlider {
        margin-bottom: 10px;
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
    .stTabs [data-baseweb="tab-list"] {
        margin-bottom: 20px;
    }
    .stPlotlyChart {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .example-box {
        background-color: #f0f8ff;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
        border-left: 5px solid #3498db;
    }
    .hedging-details {
        background-color: #fffaf0;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
        border-left: 5px solid #e67e22;
    }
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th, td {
        padding: 8px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    th {
        background-color: #f1f1f1;
    }
    .dataframe {
        width: 100%;
    }
    .highlight-row {
        background-color: #fffacd;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("📊 Bond Investment & USD/INR Hedging Dashboard")
st.markdown("""
Analyze your bond investment returns with comprehensive USD/INR currency hedging strategies to mitigate forex risk.
""")

# Create columns for layout
col1, col2 = st.columns([1, 1])

with col1:
    with st.container():
        st.header("💰 Investment Parameters")
        investment_inr = st.number_input(
            "**Investment Amount (INR)**", 
            min_value=1000, 
            step=1000, 
            value=1000000
        )
        tenure_years = st.slider(
            "**Tenure (Years)**", 
            min_value=1, 
            max_value=10, 
            value=3
        )
        yield_percent = st.number_input(
            "**Annual Yield (%)**", 
            min_value=0.0, 
            max_value=20.0, 
            step=0.1, 
            value=6.5
        )
        compounding = st.selectbox(
            "**Compounding Frequency**", 
            ["Annually", "Semi-Annually", "Quarterly", "Monthly"], 
            index=0
        )

with col2:
    with st.container():
        st.header("🛡️ Hedging Parameters")
        usdinr_rate = st.number_input(
            "**Current USD/INR Rate**", 
            min_value=70.0,
            max_value=100.0,
            step=0.1, 
            value=DEFAULT_USDINR_RATE,
            format="%.1f"
        )
        st.markdown(f"**USDINR Lot Size:** ${USDINR_LOT_SIZE}")
        margin_per_lot = st.number_input(
            "**Margin Requirement per Lot (INR)**", 
            min_value=1000, 
            step=100, 
            value=DEFAULT_MARGIN_PER_LOT
        )
        hedging_cost_pct = st.number_input(
            "**Annual Hedging Cost (%)**", 
            min_value=0.0, 
            max_value=5.0, 
            step=0.05, 
            value=DEFAULT_HEDGING_COST_PCT
        )
        st.markdown("*Adjust these parameters based on current market conditions*")

# Calculate returns based on compounding frequency
compounding_freq_map = {
    "Annually": 1,
    "Semi-Annually": 2,
    "Quarterly": 4,
    "Monthly": 12
}
n = compounding_freq_map[compounding]

if compounding == "Annually":
    interest_earned = investment_inr * (yield_percent / 100) * tenure_years
else:
    interest_earned = investment_inr * (1 + (yield_percent/100)/n)**(n*tenure_years) - investment_inr

total_return_inr = investment_inr + interest_earned

# USD Conversion
investment_usd = investment_inr / usdinr_rate

# Hedging Calculations
num_lots = math.ceil(investment_usd / USDINR_LOT_SIZE)
total_margin_inr = num_lots * margin_per_lot
total_hedging_cost = investment_usd * (hedging_cost_pct/100) * tenure_years * usdinr_rate
actual_return_with_hedging = total_return_inr - total_margin_inr - total_hedging_cost

# Return Percentages
return_pct_without_hedging = ((total_return_inr - investment_inr) / investment_inr) * 100
return_pct_with_hedging = ((actual_return_with_hedging - investment_inr) / investment_inr) * 100
hedging_cost_pct_of_investment = ((total_margin_inr + total_hedging_cost) / investment_inr) * 100

# Scenario Analysis
def calculate_scenario(inr_appreciation_pct):
    new_rate = usdinr_rate * (1 - inr_appreciation_pct/100)
    unhedged_return_inr = (investment_usd * new_rate) + interest_earned
    unhedged_return_usd = unhedged_return_inr / new_rate
    hedged_return_usd = actual_return_with_hedging / new_rate
    return {
        'unhedged_inr': unhedged_return_inr,
        'hedged_inr': actual_return_with_hedging,
        'unhedged_usd': unhedged_return_usd,
        'hedged_usd': hedged_return_usd,
        'rate': new_rate
    }

scenarios = [-10, -5, 0, 5, 10]  # INR appreciation/depreciation percentages
scenario_data = [calculate_scenario(s) for s in scenarios]

# Create DataFrame for visualization
df_scenarios = pd.DataFrame({
    'INR_Change': scenarios,
    'Unhedged_Return_INR': [d['unhedged_inr'] for d in scenario_data],
    'Hedged_Return_INR': [d['hedged_inr'] for d in scenario_data],
    'Unhedged_Return_USD': [d['unhedged_usd'] for d in scenario_data],
    'Hedged_Return_USD': [d['hedged_usd'] for d in scenario_data],
    'FX_Rate': [d['rate'] for d in scenario_data]
})

# Practical Example Section
st.markdown("---")
st.header("💡 Practical Example: ₹85,000 / $1,000 Investment")

with st.expander("Click to view detailed example calculations", expanded=True):
    st.markdown("""
    **Scenario Parameters:**
    - Initial investment: ₹85,000 or $1,000 (at 85 USD/INR rate)
    - Annual bond yield: 10%
    - Investment period: 1 year
    """)
    
    # Calculate example returns
    example_investment_inr = 85000
    example_investment_usd = 1000
    example_yield = 10
    example_interest_inr = example_investment_inr * (example_yield/100)
    example_interest_usd = example_investment_usd * (example_yield/100)
    example_total_inr = example_investment_inr + example_interest_inr
    example_total_usd = example_investment_usd + example_interest_usd
    
    st.markdown(f"""
    **After 1 Year (No Currency Change at 85 USD/INR):**
    - Interest earned: ₹{example_interest_inr:,.2f} or ${example_interest_usd:,.2f}
    - Total return: ₹{example_total_inr:,.2f} or ${example_total_usd:,.2f}
    """)
    
    # Conversion scenarios
    st.subheader("Currency Risk Without Hedging:")
    rate_changes = [75, 85, 95]
    example_data = []
    
    for rate in rate_changes:
        # Convert USD principal + interest back to INR at new rate
        inr_converted = example_total_usd * rate
        usd_value = example_total_usd * (85/rate)  # Adjusted USD value
        
        # Calculate gain/loss vs original INR investment
        inr_diff = inr_converted - example_total_inr
        pct_diff = (inr_diff / example_total_inr) * 100
        effective_yield = (inr_converted - example_investment_inr)/example_investment_inr*100
        
        example_data.append({
            'Scenario': 'INR Appreciates' if rate < 85 else 'INR Depreciates' if rate > 85 else 'No Change',
            'USD/INR Rate': rate,
            'USD Value': f"${usd_value:,.2f}",
            'Converted to INR': f"₹{inr_converted:,.2f}",
            'Gain/Loss vs Original': f"₹{inr_diff:,.1f} ({pct_diff:.1f}%)",
            'Effective Yield': f"{effective_yield:.1f}%"
        })
    
    # Display as table - FIXED VERSION
    def highlight_row(row):
        if row['Scenario'] in ['INR Appreciates', 'INR Depreciates']:
            return ['background-color: #fffacd'] * len(row)
        return [''] * len(row)
    
    df_example = pd.DataFrame(example_data)
    st.table(df_example.style.apply(highlight_row, axis=1))
    
    # Hedging solution
    st.subheader("🛡️ Hedging Solution with USD/INR Futures")
    
    st.markdown("""
    **To protect against currency risk:**
    1. **Sell USD/INR futures** to lock in current exchange rate
    2. Number of lots: 1 (for $1,000 investment)
    3. Margin required: ₹2,150
    """)
    
    hedge_data = []
    for rate in rate_changes:
        # Calculate spot loss/gain
        spot_change = (rate - 85)/85 * 100
        spot_result = example_total_usd * (rate - 85)
        
        # Futures position would be opposite
        futures_result = -spot_result
        
        hedge_data.append({
            'USD/INR Rate': rate,
            'Spot Change': f"{spot_change:.1f}%",
            'Spot P&L': f"₹{spot_result:,.0f}",
            'Futures P&L': f"₹{futures_result:,.0f}",
            'Net Effect': f"₹{spot_result + futures_result:,.0f}",
            'Locked Value': f"₹{example_total_inr:,.0f}"
        })
    
    df_hedge = pd.DataFrame(hedge_data)
    st.table(df_hedge)
    
    st.markdown("""
    **Result:** By hedging, the investor locks in the ₹93,500 return regardless of currency movements.
    """)

# Display Results
st.markdown("---")
st.header("📈 Investment Analysis")

# Create tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Detailed Breakdown", "Scenario Analysis", "Hedging Strategy"])

with tab1:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Initial Investment", f"₹{investment_inr:,.2f}")
    
    with col2:
        delta_color = "normal"
        if return_pct_without_hedging < 0:
            delta_color = "inverse"
        st.metric(
            "Return Without Hedging", 
            f"₹{total_return_inr:,.2f}", 
            f"{return_pct_without_hedging:.2f}%",
            delta_color=delta_color
        )
    
    with col3:
        delta_color = "normal"
        if return_pct_with_hedging < 0:
            delta_color = "inverse"
        st.metric(
            "Return With Hedging", 
            f"₹{actual_return_with_hedging:,.2f}", 
            f"{return_pct_with_hedging:.2f}%",
            delta_color=delta_color
        )
    
    st.markdown("---")
    
    # Visualization
    fig = px.bar(
        x=["Without Hedging", "With Hedging"],
        y=[total_return_inr, actual_return_with_hedging],
        text=[f"₹{x:,.2f}" for x in [total_return_inr, actual_return_with_hedging]],
        title="Total Returns Comparison",
        labels={'x': 'Strategy', 'y': 'Amount (INR)'}
    )
    fig.update_traces(marker_color=['#3498db', '#2ecc71'])
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Hedging Impact")
    st.markdown(f"""
    - **Total Hedging Cost:** ₹{total_margin_inr + total_hedging_cost:,.2f} ({hedging_cost_pct_of_investment:.2f}% of investment)
        - Margin Requirement: ₹{total_margin_inr:,.2f}
        - Annual Hedging Cost: ₹{total_hedging_cost:,.2f}
    - **Forex Protection:** Your returns are protected against USD/INR rate fluctuations
    - **Net Hedging Impact:** ₹{actual_return_with_hedging - total_return_inr:,.2f}
    """)

with tab2:
    st.subheader("Investment Breakdown")
    st.markdown(f"""
    - **Principal Amount:** ₹{investment_inr:,.2f}
    - **Annual Interest Rate:** {yield_percent:.2f}%
    - **Compounding Frequency:** {compounding}
    - **Investment Tenure:** {tenure_years} years
    - **Total Interest Earned:** ₹{interest_earned:,.2f}
    """)
    
    st.subheader("USD Conversion Details")
    st.markdown(f"""
    - **Converted USD Amount:** ${investment_usd:,.2f}
    - **USD/INR Exchange Rate:** {usdinr_rate:.2f}
    """)
    
    st.subheader("Hedging Details")
    st.markdown(f"""
    - **Number of Lots Required:** {num_lots}
    - **Margin per Lot:** ₹{margin_per_lot}
    - **Total Margin Requirement:** ₹{total_margin_inr:,.2f}
    - **Annual Hedging Cost:** {hedging_cost_pct}% of notional (₹{total_hedging_cost/tenure_years:,.2f}/year)
    - **Total Hedging Cost:** ₹{total_hedging_cost:,.2f}
    """)

with tab3:
    st.subheader("Scenario Analysis: INR Appreciation/Depreciation Impact")
    
    fig_scenario = px.line(
        df_scenarios,
        x='INR_Change',
        y=['Unhedged_Return_INR', 'Hedged_Return_INR'],
        labels={'value': 'Total Return (INR)', 'variable': 'Strategy', 'INR_Change': 'INR Change (%)'},
        title='Returns Under Different INR Movement Scenarios',
        markers=True
    )
    fig_scenario.update_layout(
        hovermode="x",
        yaxis_tickprefix="₹",
        xaxis_ticksuffix="%"
    )
    st.plotly_chart(fig_scenario, use_container_width=True)
    
    st.markdown("""
    **Key Observations:**
    - Hedged returns in INR remain constant regardless of INR movement
    - Unhedged returns benefit from INR depreciation but suffer from INR appreciation
    - The breakeven point shows where hedging becomes advantageous
    - USD returns vary based on the final exchange rate
    """)
    
    # Show detailed scenario table with USD conversions
    st.subheader("Scenario Details")
    df_display = df_scenarios.copy()
    df_display['FX_Rate'] = df_display['FX_Rate'].round(2)
    df_display['Unhedged Return (INR)'] = df_display['Unhedged_Return_INR'].apply(lambda x: f"₹{x:,.2f}")
    df_display['Hedged Return (INR)'] = df_display['Hedged_Return_INR'].apply(lambda x: f"₹{x:,.2f}")
    df_display['Unhedged Return (USD)'] = df_display['Unhedged_Return_USD'].apply(lambda x: f"${x:,.2f}")
    df_display['Hedged Return (USD)'] = df_display['Hedged_Return_USD'].apply(lambda x: f"${x:,.2f}")
    df_display = df_display[['INR_Change', 'FX_Rate', 
                            'Unhedged Return (INR)', 'Hedged Return (INR)',
                            'Unhedged Return (USD)', 'Hedged Return (USD)']]
    df_display.columns = ['INR Change %', 'USD/INR Rate', 
                         'Unhedged (INR)', 'Hedged (INR)',
                         'Unhedged (USD)', 'Hedged (USD)']
    
    # Display the table with improved formatting
    st.dataframe(
        df_display.style.format({
            'INR Change %': '{:.0f}%',
            'USD/INR Rate': '{:.2f}'
        }),
        use_container_width=True
    )
    
    # Specific Rate Examples
    st.subheader("Specific Rate Examples")
    specific_rates = [75, 85, 95]
    specific_data = []
    
    for rate in specific_rates:
        scenario_pct = ((rate - usdinr_rate)/usdinr_rate)*100
        scenario = calculate_scenario(-scenario_pct)  # Negative because our function expects appreciation %
        
        specific_data.append({
            'USD/INR Rate': rate,
            'INR Change': f"{scenario_pct:.1f}%",
            'Unhedged (INR)': f"₹{scenario['unhedged_inr']:,.2f}",
            'Hedged (INR)': f"₹{scenario['hedged_inr']:,.2f}",
            'Unhedged (USD)': f"${scenario['unhedged_usd']:,.2f}",
            'Hedged (USD)': f"${scenario['hedged_usd']:,.2f}",
            'Hedging Benefit': f"₹{scenario['hedged_inr'] - scenario['unhedged_inr']:,.2f}"
        })
    
    df_specific = pd.DataFrame(specific_data)
    st.table(df_specific)

with tab4:
    st.subheader("Hedging Strategy Recommendation")
    
    if hedging_cost_pct_of_investment < 1.5:
        st.success("""
        ✅ **Hedging is recommended**  
        The total hedging cost is relatively low compared to your investment, providing good protection against forex volatility.
        """)
    else:
        st.warning("""
        ⚠️ **Consider partial hedging or alternative strategies**  
        The hedging cost is significant relative to your investment. You might want to:
        - Hedge only a portion of your exposure
        - Use options for cheaper protection
        - Accept some forex risk for higher potential returns
        """)
    
    st.markdown("---")
    st.subheader("Hedging Implementation")
    st.markdown(f"""
    To implement this hedge, you would need to:
    1. Open a futures position for {num_lots} USD/INR lots
    2. Maintain ₹{total_margin_inr:,.2f} as margin
    3. Pay approximately ₹{total_hedging_cost/tenure_years:,.2f} annually in hedging costs
    
    **Monitoring Requirements:**
    - Track mark-to-market on your futures position
    - Maintain adequate margin levels
    - Consider rolling over positions as contracts expire
    
    **Tax Implications:**
    - Hedging costs may be tax-deductible as business expenses
    - Consult with a tax advisor for your specific situation
    """)
    
    st.markdown("---")
    st.subheader("Alternative Strategies")
    st.markdown("""
    Consider these alternative approaches if standard hedging is too expensive:
    
    **1. Partial Hedging:**
    - Hedge only 50-70% of your exposure
    - Reduces costs while still providing some protection
    
    **2. Options Strategies:**
    - Buy USD puts/INR calls for downside protection
    - Implement collars (buy puts + sell calls) to reduce costs
    
    **3. Natural Hedging:**
    - Match USD liabilities with USD assets
    - Structure cash flows to naturally offset currency risk
    """)

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #7f8c8d; font-size: 0.8em;">
    <p>Dashboard last updated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Note: This is a simplified calculation. Actual market conditions, brokerage fees, and taxes may affect results.</p>
    <p>Consult with a financial advisor before making investment decisions.</p>
</div>
""", unsafe_allow_html=True)
