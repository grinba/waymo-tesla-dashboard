
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import yfinance as yf
from datetime import datetime
import requests

st.set_page_config(page_title="Waymo IPO & Tesla Competition Dashboard", layout="wide")

st.title("🚗 Waymo IPO Valuation vs Tesla Competition - Interactive Forecasting Tool")

# --- Sidebar Inputs ---
st.sidebar.header("Scenario Settings")
bear_prob = st.sidebar.slider("Bear Case Probability", 0.0, 1.0, 0.2, 0.05)
base_prob = st.sidebar.slider("Base Case Probability", 0.0, 1.0, 0.5, 0.05)
bull_prob = 1.0 - bear_prob - base_prob
st.sidebar.markdown(f"**Bull Case Probability:** {bull_prob:.2f}")

ipo_prices = {
    "Bear": st.sidebar.number_input("Bear Case Price", 10, 200, 50),
    "Base": st.sidebar.number_input("Base Case Price", 10, 200, 90),
    "Bull": st.sidebar.number_input("Bull Case Price", 10, 200, 120),
}

competition_impact = st.sidebar.selectbox("Tesla Competition Impact", {
    "Low Impact (0%)": 0.0,
    "Moderate Impact (-15%)": -0.15,
    "High Impact (-30%)": -0.3
}.keys())

adoption_speed = st.sidebar.slider("Adoption Curve Speed (2030 AV Penetration %)", 5, 50, 20)

# --- Live Tesla Stock Data ---
st.subheader("📈 Live Tesla Stock Price")
try:
    tsla = yf.Ticker("TSLA")
    tsla_price = tsla.history(period="1d")["Close"].iloc[-1]
    st.metric(label="Tesla Stock Price (TSLA)", value=f"${tsla_price:.2f}")
except Exception as e:
    st.warning("Could not fetch live Tesla price in this environment.")

# --- Monte Carlo Simulation ---
st.subheader("📊 IPO Price Simulation")
probs = [bear_prob, base_prob, bull_prob]
scenarios = ["Bear", "Base", "Bull"]
comp_factor = {
    "Low Impact (0%)": 0.0,
    "Moderate Impact (-15%)": -0.15,
    "High Impact (-30%)": -0.3
}[competition_impact]

n_sims = 5000
results = []
for _ in range(n_sims):
    scen = np.random.choice(scenarios, p=probs)
    price = ipo_prices[scen]
    adj_price = price * (1 + comp_factor)
    results.append(adj_price)

df = pd.DataFrame(results, columns=["Final Price"])
avg_price = df["Final Price"].mean()
st.write(f"**Expected IPO Price:** ${avg_price:.2f}")

fig = px.histogram(df, x="Final Price", nbins=30, title="IPO Price Distribution", marginal="box")
st.plotly_chart(fig, use_container_width=True)

# --- Long-term Growth Forecast ---
st.subheader("📈 Long-term Market Cap Forecast (2025–2030)")
years = np.arange(2025, 2031)
waymo_base_cap = avg_price * 500_000_000  # assume 500M shares
waymo_growth = [waymo_base_cap * (1 + adoption_speed/100)**(y-2025) for y in years]
tesla_av_base = 300e9
tesla_growth = [tesla_av_base * (1 + (adoption_speed*0.8)/100)**(y-2025) for y in years]

growth_df = pd.DataFrame({
    "Year": years,
    "Waymo Market Cap": waymo_growth,
    "Tesla AV Segment": tesla_growth
})

fig2 = px.line(growth_df, x="Year", y=["Waymo Market Cap", "Tesla AV Segment"], markers=True)
st.plotly_chart(fig2, use_container_width=True)

# --- News Section ---
st.subheader("📰 Latest News (Sample Data)")
st.write("*(Live news API integration would pull from Google News / NewsAPI)*")
news_data = [
    {"headline": "Waymo expands robotaxi service to Washington D.C. in 2026", "date": "2025-08-01"},
    {"headline": "Tesla Robotaxi faces NHTSA probe after erratic test drives", "date": "2025-07-20"},
    {"headline": "Waymo valuation tops $45B after funding round", "date": "2024-10-15"}
]
for item in news_data:
    st.markdown(f"- **{item['date']}**: {item['headline']}")

# --- Export ---
if st.button("Export Results to CSV"):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download IPO Simulation CSV", data=csv, file_name="ipo_simulation.csv", mime="text/csv")
