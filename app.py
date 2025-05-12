import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Page configuration
st.set_page_config(page_title="Bond Investment Dashboard", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stNumberInput, .stSelectbox {
        background-color: white;
    }
    .metric-box {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .header {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("📊 Bond Investment Dashboard with USD/INR Hedging")

# Sidebar for inputs
with st.sidebar:
    st.header("Investment Parameters")
    
    # Bond investment inputs
    principal = st.number_input("Investment Amount (INR)", min_value=1000, value=500000, step=1000)
    tenure = st.selectbox("Tenure (Years)", [1, 2, 3], index=2)
    yield_rate = st.number_input("Annual Yield (%)", min_value=0.1, value=7.5, step=0.1)
    
    st.header("USD/INR Hedging Parameters")
    usdinr_rate = st.number_input("Current USD/INR Rate", min_value=1.0, value=85.0, step=0.1)
    hedge_percentage = st.slider("Hedge Percentage (%)", 0, 100, 100)
    margin_per_lot = st.number_input("Margin per Lot (INR)", min_value=1000, value=2150, step=50)

# Calculations
def calculate_bond_returns(principal, tenure, yield_rate):
    total_return = principal * (1 + (yield_rate/100))**tenure
    interest_earned = total_return - principal
    return total_return, interest_earned

def calculate_hedging(principal, usdinr_rate, margin_per_lot, hedge_percentage):
    usd_equivalent = (principal / usdinr_rate) * (hedge_percentage/100)
    lots_needed = usd_equivalent / 1000  # Each lot = USD 1000
    full_lots = int(lots_needed)
    margin_required = full_lots * margin_per_lot
    unhedged_amount = (principal / usdinr_rate) - (full_lots * 1000)
    return usd_equivalent, full_lots, margin_required, unhedged_amount

total_return, interest_earned = calculate_bond_returns(principal, tenure, yield_rate)
usd_equivalent, full_lots, margin_required, unhedged_amount = calculate_hedging(
    principal, usdinr_rate, margin_per_lot, hedge_percentage
)

# Dashboard layout
col1, col2 = st.columns(2)

with col1:
    st.header("Investment Returns")
    
    # Metrics
    st.markdown(f"""
    <div class="metric-box">
        <h3>Principal Amount</h3>
        <h2>₹{principal:,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-box">
        <h3>Maturity Value ({tenure} year{'s' if tenure > 1 else ''})</h3>
        <h2>₹{total_return:,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-box">
        <h3>Interest Earned</h3>
        <h2>₹{interest_earned:,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Growth chart
    years = list(range(tenure + 1))
    values = [principal * (1 + (yield_rate/100))**year for year in years]
    
    fig1, ax1 = plt.subplots()
    ax1.plot(years, values, marker='o', color='#3498db')
    ax1.set_title('Investment Growth Over Time')
    ax1.set_xlabel('Years')
    ax1.set_ylabel('Value (INR)')
    ax1.grid(True)
    st.pyplot(fig1)

with col2:
    st.header("Currency Hedging")
    
    # Metrics
    st.markdown(f"""
    <div class="metric-box">
        <h3>USD Equivalent</h3>
        <h2>${usd_equivalent:,.2f} (at {usdinr_rate} USD/INR)</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-box">
        <h3>Hedging Required</h3>
        <h2>{full_lots} lot{'s' if full_lots != 1 else ''} (${full_lots * 1000:,.0f} coverage)</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-box">
        <h3>Margin Required</h3>
        <h2>₹{margin_required:,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Pie chart for hedging coverage
    if usd_equivalent > 0:
        labels = ['Hedged Amount', 'Unhedged Amount']
        sizes = [full_lots * 1000, max(0, unhedged_amount)]
        colors = ['#2ecc71', '#e74c3c']
        
        fig2, ax2 = plt.subplots()
        ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax2.axis('equal')
        ax2.set_title('Hedging Coverage')
        st.pyplot(fig2)
    
    # Explanation
    with st.expander("How Hedging Works"):
        st.write("""
        - **Hedging protects** your USD investment against INR appreciation
        - For each USD 1000 invested, you would take a **short position** in USD/INR futures
        - If INR strengthens (USD/INR falls), your futures position will profit, offsetting bond losses
        - The margin is the amount needed to maintain this hedge position
        - You're currently hedging {:.0f}% of your USD exposure
        """.format(hedge_percentage))

# Additional calculations
annualized_return = ((total_return / principal) ** (1/tenure) - 1) * 100

# Footer with additional metrics
st.markdown("---")
col3, col4, col5 = st.columns(3)
with col3:
    st.metric("Effective Annual Return", f"{annualized_return:.2f}%")
with col4:
    st.metric("Total Return", f"{(total_return/principal - 1)*100:.2f}%")
with col5:
    st.metric("Unhedged USD Amount", f"${max(0, unhedged_amount):,.2f}")
