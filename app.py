import streamlit as st
import math
from datetime import datetime

# Constants
USDINR_RATE = 85
USDINR_LOT_SIZE = 1000  # One lot = $1000
MARGIN_PER_LOT = 2150  # INR per lot

# Page configuration
st.set_page_config(page_title="Bond Investment Dashboard", layout="wide")

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
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("💰 Bond Investment Return Dashboard")
st.markdown("""
Calculate your potential bond investment returns with USDINR currency hedging to mitigate forex risk.
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
        st.markdown("*Note: These values can be adjusted in the code*")

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

# Display Results
st.markdown("---")
st.header("📈 Investment Results")

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["Summary", "Detailed Breakdown", "Comparison"])

with tab1:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Initial Investment", f"₹{investment_inr:,.2f}")
    
    with col2:
        delta_color = "normal"
        if return_pct_without_hedging < 0:
            delta_color = "inverse"
        st.metric("Return Without Hedging", 
                 f"₹{total_return_inr:,.2f}", 
                 f"{return_pct_without_hedging:.2f}%",
                 delta_color=delta_color)
    
    with col3:
        delta_color = "normal"
        if return_pct_with_hedging < 0:
            delta_color = "inverse"
        st.metric("Return With Hedging", 
                 f"₹{actual_return_with_hedging:,.2f}", 
                 f"{return_pct_with_hedging:.2f}%",
                 delta_color=delta_color)
    
    st.markdown("---")
    st.subheader("Hedging Impact")
    st.markdown(f"""
    - **Hedging Cost:** ₹{total_margin_inr:,.2f} ({hedging_cost_pct:.2f}% of investment)
    - **Forex Protection:** Your returns are protected against USD/INR rate fluctuations
    - **Net Hedging Benefit:** ₹{actual_return_with_hedging - total_return_inr:,.2f}
    """)

with tab2:
    st.subheader("Investment Breakdown")
    st.markdown(f"""
    - **Principal Amount:** ₹{investment_inr:,.2f}
    - **Annual Interest Rate:** {yield_percent:.2f}%
    - **Investment Tenure:** {tenure_years} years
    - **Total Interest Earned:** ₹{interest_earned:,.2f}
    """)
    
    st.subheader("USD Conversion Details")
    st.markdown(f"""
    - **Converted USD Amount:** ${investment_usd:,.2f}
    - **USD/INR Exchange Rate:** {USDINR_RATE}
    """)
    
    st.subheader("Hedging Details")
    st.markdown(f"""
    - **Number of Lots Required:** {num_lots}
    - **Margin per Lot:** ₹{MARGIN_PER_LOT}
    - **Total Margin Requirement:** ₹{total_margin_inr:,.2f}
    """)

with tab3:
    st.subheader("Return Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Without Hedging
        - **Potential Risk:** Exchange rate fluctuations
        - **Potential Reward:** No hedging costs
        - **Best Case:** If INR depreciates
        - **Worst Case:** If INR appreciates
        """)
    
    with col2:
        st.markdown("""
        ### With Hedging
        - **Risk Mitigation:** Fixed exchange rate
        - **Cost:** Margin requirement
        - **Best Case:** Predictable returns
        - **Worst Case:** Opportunity cost if INR depreciates
        """)
    
    st.markdown("---")
    st.subheader("Hedging Recommendation")
    if hedging_cost_pct < 1:
        st.success("✅ Hedging is recommended as the cost is relatively low compared to your investment.")
    else:
        st.warning("⚠️ Consider whether hedging is necessary as the cost is significant relative to your investment.")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #7f8c8d; font-size: 0.8em;">
    <p>Dashboard last updated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Note: This is a simplified calculation. Actual market conditions may vary.</p>
</div>
""", unsafe_allow_html=True)
