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
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
    }
    .comparison-table th, .comparison-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    .comparison-table tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    .comparison-table th {
        background-color: #3498db;
        color: white;
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
    margin_interest_rate = st.number_input("Annual Margin Interest Rate (%)", min_value=0.0, value=8.0, step=0.1)

# Calculations
def calculate_bond_returns(principal, tenure, yield_rate):
    total_return = principal * (1 + (yield_rate/100))**tenure
    interest_earned = total_return - principal
    return total_return, interest_earned

def calculate_hedging(principal, usdinr_rate, margin_per_lot, hedge_percentage, tenure, margin_interest_rate):
    # USD conversion
    usd_equivalent = (principal / usdinr_rate) * (hedge_percentage/100)
    
    # Hedging calculations
    lots_needed = usd_equivalent / 1000  # Each lot = USD 1000
    full_lots = int(lots_needed)
    total_margin = full_lots * margin_per_lot
    
    # Calculate margin interest cost (simple interest)
    margin_interest_cost = total_margin * (margin_interest_rate/100) * tenure
    
    # Total hedging cost
    total_hedging_cost = margin_interest_cost
    
    unhedged_amount = (principal / usdinr_rate) - (full_lots * 1000)
    
    return usd_equivalent, full_lots, total_margin, total_hedging_cost, unhedged_amount

# Main calculations
total_return, interest_earned = calculate_bond_returns(principal, tenure, yield_rate)
usd_equivalent, full_lots, margin_required, hedging_cost, unhedged_amount = calculate_hedging(
    principal, usdinr_rate, margin_per_lot, hedge_percentage, tenure, margin_interest_rate
)

# Calculate actual returns after hedging costs
return_without_hedging = total_return
return_with_hedging = total_return - hedging_cost

# Calculate annualized returns
annualized_without = ((return_without_hedging / principal) ** (1/tenure) - 1) * 100
annualized_with = ((return_with_hedging / principal) ** (1/tenure) - 1) * 100

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
    
    # USD Conversion Metrics
    st.markdown(f"""
    <div class="metric-box">
        <h3>USD Equivalent (Full Conversion)</h3>
        <h2>${principal/usdinr_rate:,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-box">
        <h3>Hedged Amount ({hedge_percentage}%)</h3>
        <h2>${usd_equivalent:,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-box">
        <h3>Hedging Details</h3>
        <p>Lots Required: {full_lots} (${full_lots * 1000:,.0f})</p>
        <p>Margin Required: ₹{margin_required:,.2f}</p>
        <p>Total Hedging Cost: ₹{hedging_cost:,.2f}</p>
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

# Return Comparison Section
st.markdown("---")
st.header("Return Comparison: With vs Without Hedging")

col3, col4, col5 = st.columns(3)
with col3:
    st.metric("Total Return Without Hedging", f"₹{return_without_hedging:,.2f}", 
              f"{(return_without_hedging/principal - 1)*100:.2f}%")
with col4:
    st.metric("Total Return With Hedging", f"₹{return_with_hedging:,.2f}", 
              f"{(return_with_hedging/principal - 1)*100:.2f}%")
with col5:
    difference = return_without_hedging - return_with_hedging
    st.metric("Hedging Cost Impact", f"₹{difference:,.2f}", 
              f"-{(difference/principal)*100:.2f}%")

# Detailed comparison table
st.markdown(f"""
<table class="comparison-table">
    <tr>
        <th>Metric</th>
        <th>Without Hedging</th>
        <th>With Hedging</th>
        <th>Difference</th>
    </tr>
    <tr>
        <td>Final Value (INR)</td>
        <td>₹{return_without_hedging:,.2f}</td>
        <td>₹{return_with_hedging:,.2f}</td>
        <td>₹{(return_without_hedging - return_with_hedging):,.2f}</td>
    </tr>
    <tr>
        <td>Total Return</td>
        <td>{(return_without_hedging/principal - 1)*100:.2f}%</td>
        <td>{(return_with_hedging/principal - 1)*100:.2f}%</td>
        <td>{((return_without_hedging - return_with_hedging)/principal)*100:.2f}%</td>
    </tr>
    <tr>
        <td>Annualized Return</td>
        <td>{annualized_without:.2f}%</td>
        <td>{annualized_with:.2f}%</td>
        <td>{(annualized_without - annualized_with):.2f}%</td>
    </tr>
</table>
""", unsafe_allow_html=True)

# Explanation
with st.expander("Understanding the Results"):
    st.write(f"""
    **Key Concepts:**
    
    1. **Without Hedging:**
       - Your full investment grows at the bond yield rate
       - You're exposed to USD/INR exchange rate fluctuations
       - If INR appreciates, your USD investment will be worth less in INR terms
    
    2. **With Hedging:**
       - You pay margin costs to protect against currency fluctuations
       - Your net return is bond returns minus hedging costs
       - Protects you if INR appreciates, but costs money if INR depreciates
    
    3. **Hedging Cost Components:**
       - Margin requirement (₹{margin_required:,.0f} upfront)
       - Margin interest cost (₹{hedging_cost:,.0f} over {tenure} years at {margin_interest_rate}%)
    """)
    
    st.write("""
    **When to Hedge:**
    - When you want to lock in current exchange rates
    - When you believe INR might appreciate significantly
    - When currency stability is more important than maximizing returns
    """)

# Additional metrics
st.markdown("---")
st.subheader("Additional Metrics")
col6, col7, col8 = st.columns(3)
with col6:
    st.metric("USD Equivalent (Full)", f"${principal/usdinr_rate:,.2f}")
with col7:
    st.metric("Unhedged USD Amount", f"${max(0, unhedged_amount):,.2f}")
with col8:
    st.metric("Hedging Cost per Year", f"₹{hedging_cost/tenure:,.2f}")
