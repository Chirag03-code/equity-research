# Stock analysis using OpenBB: real price data, returns, and risk
from openbb import obb
import matplotlib.pyplot as plt

tickers = ["AAPL", "MSFT", "GOOGL"]
start = "2023-01-01"

results = []
for t in tickers:
    df = obb.equity.price.historical(t, start_date=start, provider="yfinance").to_dataframe()
    df["daily_return"] = df["close"].pct_change()

    total_return = (df["close"].iloc[-1] / df["close"].iloc[0] - 1) * 100
    volatility = df["daily_return"].std() * (252 ** 0.5) * 100  # annualized

    results.append((t, round(total_return, 2), round(volatility, 2)))
    plt.plot(df.index, df["close"] / df["close"].iloc[0], label=t)

print(f"{'Ticker':<8}{'Total Return %':>16}{'Volatility %':>15}")
for t, r, v in results:
    print(f"{t:<8}{r:>16}{v:>15}")

plt.title("Growth of $1 since " + start)
plt.legend()
plt.savefig("01_openbb_analysis/price_comparison.png")
print("Chart saved!")
