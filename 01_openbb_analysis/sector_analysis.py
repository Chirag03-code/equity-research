# Energy vs. Financials: return, risk, and risk-adjusted performance
# Data: Yahoo Finance via the OpenBB Platform
from openbb import obb
import pandas as pd
import matplotlib.pyplot as plt

# ---------- Settings (change these to analyze other stocks) ----------
START = "2023-01-01"
RISK_FREE = 0.04  # assumed annual risk-free rate (~3-month T-bill)
SECTORS = {
    "Energy": ["XOM", "CVX", "COP"],
    "Financials": ["JPM", "BAC", "GS"],
}
BENCHMARK = "SPY"  # S&P 500 ETF, used for beta and comparison
OUT = "01_openbb_analysis"

# ---------- 1. Download daily closing prices ----------
tickers = [t for group in SECTORS.values() for t in group] + [BENCHMARK]
prices = pd.DataFrame()
for t in tickers:
    df = obb.equity.price.historical(t, start_date=START, provider="yfinance").to_dataframe()
    prices[t] = df["close"]
prices = prices.dropna()
returns = prices.pct_change().dropna()

# ---------- 2. Calculate metrics for each stock ----------
rows = []
for t in tickers:
    r = returns[t]
    total_return = prices[t].iloc[-1] / prices[t].iloc[0] - 1
    years = len(r) / 252
    cagr = (1 + total_return) ** (1 / years) - 1                 # annual growth rate
    volatility = r.std() * 252 ** 0.5                             # annualized risk
    sharpe = (r.mean() * 252 - RISK_FREE) / volatility            # return per unit of risk
    growth = prices[t] / prices[t].iloc[0]                        # growth of $1
    max_drawdown = (growth / growth.cummax() - 1).min()           # worst peak-to-trough fall
    beta = r.cov(returns[BENCHMARK]) / returns[BENCHMARK].var()   # sensitivity to the market
    sector = next((s for s, g in SECTORS.items() if t in g), "Benchmark")
    rows.append({
        "Ticker": t,
        "Sector": sector,
        "Total Return %": total_return * 100,
        "CAGR %": cagr * 100,
        "Volatility %": volatility * 100,
        "Sharpe": sharpe,
        "Max Drawdown %": max_drawdown * 100,
        "Beta": beta,
    })

table = pd.DataFrame(rows).set_index("Ticker").round(2)
sector_avg = table.groupby("Sector").mean(numeric_only=True).round(2)

print(f"\nPeriod: {prices.index[0]} to {prices.index[-1]}\n")
print("Per-stock metrics:")
print(table.to_string())
print("\nSector averages:")
print(sector_avg.to_string())

table.to_csv(f"{OUT}/sector_metrics.csv")

# ---------- 3. Charts ----------
colors = {"Energy": "tab:orange", "Financials": "tab:blue", "Benchmark": "black"}

plt.figure(figsize=(10, 6))
for t in tickers:
    style = "--" if t == BENCHMARK else "-"
    plt.plot(prices.index, prices[t] / prices[t].iloc[0], style,
             color=colors[table.loc[t, "Sector"]], label=t, alpha=0.85)
plt.title(f"Growth of $1 since {START}: Energy vs. Financials vs. S&P 500")
plt.ylabel("Value of $1")
plt.legend(ncol=4)
plt.tight_layout()
plt.savefig(f"{OUT}/sector_growth.png", dpi=150)
plt.close()

plt.figure(figsize=(8, 5))
plt.bar(table.index, table["Sharpe"], color=[colors[s] for s in table["Sector"]])
plt.axhline(0, color="gray", linewidth=0.8)
plt.title(f"Sharpe ratio (risk-free rate = {RISK_FREE:.0%})")
plt.tight_layout()
plt.savefig(f"{OUT}/sharpe_ratios.png", dpi=150)
plt.close()

print(f"\nSaved: {OUT}/sector_metrics.csv, sector_growth.png, sharpe_ratios.png")