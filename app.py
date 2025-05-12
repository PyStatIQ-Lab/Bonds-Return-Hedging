import streamlit as st

# Constants
USDINR_RATE = 85
USDINR_LOT_SIZE = 1000  # One lot = $1000
MARGIN_PER_LOT = 2150  # INR per lot

st.title("Bond Investment Return Dashboard with USDINR Hedging")

# Inputs
investment_inr = st.number_input("Investment Amount (INR)", min_value=1000, step=1000)
tenure_years = st.selectbox("Tenure (Years)", [1, 2, 3])
yield_percent = st.number_input("Annual Yield (%)", min_value=0.0, step=0.1)

# Calculate returns
interest_earned = investment_inr * (yield_percent / 100) * tenure_years
total_return_inr = investment_inr + interest_earned

# USD Conversion
investment_usd = investment_inr / USDINR_RATE

# Number of lots needed (ceiling to cover full investment)
import math
num_lots = math.ceil(investment_usd / USDINR_LOT_SIZE)
total_margin_inr = num_lots * MARGIN_PER_LOT

# Return after hedging
actual_return_with_hedging = total_return_inr - total_margin_inr

# Display Results
st.subheader("Investment Summary")
st.write(f"**Investment Amount:** ₹{investment_inr:,.2f}")
st.write(f"**Tenure:** {tenure_years} years")
st.write(f"**Yield:** {yield_percent:.2f}%")
st.write(f"**Interest Earned:** ₹{interest_earned:,.2f}")
st.write(f"**Total Return (INR):** ₹{total_return_inr:,.2f}")

st.subheader("USD Conversion")
st.write(f"**Converted USD Investment:** ${investment_usd:,.2f}")
st.write(f"**USDINR Hedge Lots Required:** {num_lots}")
st.write(f"**Margin Required (INR):** ₹{total_margin_inr:,.2f}")

st.subheader("Final Return")
st.write(f"**Return After Hedging (INR):** ₹{actual_return_with_hedging:,.2f}")
st.write(f"**Return Without Hedging (INR):** ₹{total_return_inr:,.2f}")

# Comparison
st.markdown("---")
st.metric(label="Total Return Without Hedging", value=f"₹{total_return_inr:,.2f}")
st.metric(label="Total Return With Hedging", value=f"₹{actual_return_with_hedging:,.2f}")
st.metric(label="Total Margin Deducted", value=f"₹{total_margin_inr:,.2f}")
