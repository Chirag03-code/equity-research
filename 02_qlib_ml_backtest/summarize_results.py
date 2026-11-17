# Summarize the latest Qlib run: signal quality, backtest metrics, and a performance chart
# Run from the project root:  python 02_qlib_ml_backtest/summarize_results.py
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

FOLDER = Path("02_qlib_ml_backtest")

# ---------- 1. Find the most recent experiment run ----------
runs = sorted(FOLDER.glob("mlruns/*/*/artifacts/portfolio_analysis"), key=lambda p: p.stat().st_mtime)
if not runs:
    raise SystemExit("No Qlib results found. Run qrun first.")
art = runs[-1].parent

# ---------- 2. Signal quality: does the model rank stocks well? ----------
ic = pd.read_pickle(art / "sig_analysis/ic.pkl")     # daily correlation: prediction vs. actual return
ric = pd.read_pickle(art / "sig_analysis/ric.pkl")   # same, using ranks
signal = pd.Series({
    "IC": ic.mean(),
    "ICIR": ic.mean() / ic.std(),
    "Rank IC": ric.mean(),
    "Rank ICIR": ric.mean() / ric.std(),
})

# ---------- 3. Backtest: excess return over the CSI 300 index ----------
port = pd.read_pickle(art / "portfolio_analysis/port_analysis_1day.pkl")["risk"]
backtest = pd.DataFrame({
    "Without costs": port["excess_return_without_cost"],
    "With costs": port["excess_return_with_cost"],
}).drop("mean")

print("\nSignal quality (test period):")
print(signal.round(4).to_string())
print("\nExcess return vs. CSI 300 benchmark:")
print(backtest.round(4).to_string())

summary = pd.concat([signal.rename("value").to_frame(),
                     backtest.stack().rename("value").to_frame().set_axis(
                         [f"{m} ({c})" for m, c in backtest.stack().index])])
summary.round(4).to_csv(FOLDER / "results_summary.csv")

# ---------- 4. Chart: strategy vs. benchmark ----------
report = pd.read_pickle(art / "portfolio_analysis/report_normal_1day.pkl")
strategy = (1 + report["return"] - report["cost"]).cumprod()   # net of trading costs
benchmark = (1 + report["bench"]).cumprod()

plt.figure(figsize=(10, 5))
plt.plot(strategy.index, strategy, label="LightGBM top-50 strategy (after costs)")
plt.plot(benchmark.index, benchmark, "--", color="black", label="CSI 300 benchmark")
plt.title("Backtest: growth of 1 unit, 2017 to 2020")
plt.legend()
plt.tight_layout()
plt.savefig(FOLDER / "backtest_performance.png", dpi=150)

print(f"\nSaved: {FOLDER}/results_summary.csv and {FOLDER}/backtest_performance.png")