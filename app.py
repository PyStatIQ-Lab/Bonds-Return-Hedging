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
    .highlight {
        background-color: #fffacd;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("📊 Bond Investment & USD/INR Hedging Dashboard")

# Practical Example Section
st.markdown("---")
st.header("💡 Practical Example: ₹85,000 / $1,000 Investment")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Investment Details:**
    - Initial investment: ₹85,000 or $1,000 (at 85 USD/INR)
    - Annual bond yield: 10%
    - Investment period: 1 year
    - No hedging applied initially
    """)

with col2:
    st.markdown("""
    **After 1 Year (No Currency Change):**
    - Interest earned: ₹8,500 or $100
    - Total return: ₹93,500 or $1,100
    - USD/INR rate remains at 85
    """)

# Currency Change Scenarios
st.subheader("Currency Risk Scenarios")

rates = [75, 85, 95]
scenario_data = []

for rate in rates:
    principal_usd = 1000
    interest_usd = 100
    total_usd = principal_usd + interest_usd
    
    # Calculate converted amounts
    converted_inr = total_usd * rate
    effective_yield = (converted_inr - 85000)/85000*100
    usd_value = 1100 * (85/rate)  # Adjust USD value based on new rate
    
    scenario_data.append({
        'Scenario': 'INR Appreciates' if rate < 85 else 'INR Depreciates' if rate > 85 else 'No Change',
        'USD/INR Rate': rate,
        'Total USD Value': f"${usd_value:,.2f}",
        'Converted to INR': f"₹{converted_inr:,.2f}",
        'Effective Yield': f"{effective_yield:.1f}%",
        'Gain/Loss vs Original': f"₹{converted_inr-93500:,.0f}"
    })

df_scenarios = pd.DataFrame(scenario_data)
st.table(df_scenarios.style.applymap(lambda x: 'background-color: #fffacd' if x == 'INR Appreciates' or x == 'INR Depreciates' else '', subset=['Scenario']))

st.markdown("""
**Key Observations:**
- When **INR appreciates to 75**, your $1,100 is worth only ₹82,500 (effective yield -2.9%)
- When **INR depreciates to 95**, your $1,100 becomes ₹104,500 (effective yield 22.9%)
- The investor faces significant currency risk without hedging
""")

# Hedging Solution
st.markdown("---")
st.header("🛡️ Hedging Solution with USD/INR Futures")

with st.expander("How Futures Hedging Works", expanded=True):
    st.markdown("""
    **To protect against currency risk, the investor can:**
    1. **Sell USD/INR futures** to lock in the current exchange rate
    2. The futures position will gain/lose value opposite to the spot rate movement
    3. At maturity, the futures gains will offset the currency losses
    """)
    
    # Hedging calculation example
    st.subheader("Hedging Example for $1,000 Investment")
    
    hedge_data = []
    for rate in rates:
        # Calculate spot loss/gain
        spot_change = (rate - 85)/85 * 100
        spot_result = 1100 * (rate - 85)
        
        # Futures position would be opposite
        futures_result = -spot_result
        
        hedge_data.append({
            'USD/INR Rate': rate,
            'Spot Change': f"{spot_change:.1f}%",
            'Spot P&L': f"₹{spot_result:,.0f}",
            'Futures P&L': f"₹{futures_result:,.0f}",
            'Net Effect': f"₹{spot_result + futures_result:,.0f}"
        })
    
    df_hedge = pd.DataFrame(hedge_data)
    st.table(df_hedge)
    
    st.markdown("""
    **How This Works:**
    - At 75 USD/INR (INR appreciates):
        - Spot position loses ₹11,000 (your $1,100 is worth less)
        - Futures position gains ₹11,000
        - Net effect: ₹0 (fully hedged)
    - At 95 USD/INR (INR depreciates):
        - Spot position gains ₹11,000 (your $1,100 is worth more)
        - Futures position loses ₹11,000
        - Net effect: ₹0 (fully hedged)
    """)

# Implementation Details
with st.container():
    st.subheader("Implementation Steps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **1. Determine Hedge Amount:**
        - Investment: $1,000
        - Return after 1 year: $1,100
        - Hedge amount: $1,100
        
        **2. Calculate Number of Lots:**
        - USD/INR lot size: $1,000
        - Number of lots: 1.1 (round up to 2 lots)
        """)
    
    with col2:
        st.markdown("""
        **3. Margin Requirements:**
        - Margin per lot: ₹2,150
        - Total margin: ₹4,300
        
        **4. Costs:**
        - Brokerage fees
        - Rollover costs if needed
        """)
    
    st.markdown("""
    **Result:** By hedging, the investor locks in the ₹93,500 return regardless of currency movements.
    """)

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #7f8c8d; font-size: 0.8em;">
    <p>Dashboard last updated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Note: This is a simplified example. Actual trading costs may apply.</p>
</div>
""", unsafe_allow_html=True)
