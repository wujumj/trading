import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
from strategies import sma, rsi, macd

WATCHLIST = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "META", "AMZN",
    "JPM", "GS", "BAC",
    "TSLA", "F", "GM",
    "JNJ", "UNH", "PFE",
    "XOM", "CVX",
    "SPY", "QQQ", "IWM",
    "WMT", "RBLX", "SONY", "BABA", "BIDU",
]
INITIAL_CAPITAL = 10_000.0  # per ticker per strategy run


def run(df: pd.DataFrame, initial_capital: float = INITIAL_CAPITAL) -> dict:
    """
    Simulate trades from a signal DataFrame.
    Expects columns: time, close, signal (BUY / SELL / "")
    Returns a dict of performance metrics.
    """
    capital = initial_capital
    shares = 0.0
    trades = []
    entry_price = None

    for _, row in df.iterrows():
        if row["signal"] == "BUY" and shares == 0:
            shares = capital / row["close"]
            entry_price = row["close"]
            capital = 0.0

        elif row["signal"] == "SELL" and shares > 0:
            capital = shares * row["close"]
            pnl = capital - initial_capital
            trades.append({
                "entry": entry_price,
                "exit": row["close"],
                "pnl": pnl,
                "return_pct": (row["close"] - entry_price) / entry_price * 100,
            })
            shares = 0.0
            entry_price = None

    # If still holding at end, mark to market
    if shares > 0:
        capital = shares * df.iloc[-1]["close"]

    total_return = (capital - initial_capital) / initial_capital * 100

    # Daily portfolio value for drawdown + Sharpe
    portfolio = []
    cap = initial_capital
    sh = 0.0
    for _, row in df.iterrows():
        if row["signal"] == "BUY" and sh == 0:
            sh = cap / row["close"]
            cap = 0.0
        elif row["signal"] == "SELL" and sh > 0:
            cap = sh * row["close"]
            sh = 0.0
        portfolio.append(cap + sh * row["close"])

    portfolio = pd.Series(portfolio)
    daily_returns = portfolio.pct_change().dropna()

    # Max drawdown
    rolling_max = portfolio.cummax()
    drawdown = (portfolio - rolling_max) / rolling_max
    max_drawdown = drawdown.min() * 100

    # Sharpe ratio (annualised, assumes 252 trading days)
    sharpe = (
        daily_returns.mean() / daily_returns.std() * np.sqrt(252)
        if daily_returns.std() > 0 else 0.0
    )

    win_rate = (
        len([t for t in trades if t["pnl"] > 0]) / len(trades) * 100
        if trades else 0.0
    )

    return {
        "total_return_pct": round(total_return, 2),
        "max_drawdown_pct": round(max_drawdown, 2),
        "sharpe_ratio": round(sharpe, 2),
        "num_trades": len(trades),
        "win_rate_pct": round(win_rate, 2),
        "final_capital": round(capital if shares == 0 else shares * df.iloc[-1]["close"], 2),
    }


STRATEGIES = {
    "SMA(20/50)": sma.get_signals,
    "RSI(14)":    rsi.get_signals,
    "MACD(12/26/9)": macd.get_signals,
}


if __name__ == "__main__":
    rows = []

    for ticker in WATCHLIST:
        for strategy_name, get_signals in STRATEGIES.items():
            df = get_signals(ticker)
            metrics = run(df)
            rows.append({
                "Ticker":      ticker,
                "Strategy":    strategy_name,
                "Return %":    metrics["total_return_pct"],
                "Max DD %":    metrics["max_drawdown_pct"],
                "Sharpe":      metrics["sharpe_ratio"],
                "Trades":      metrics["num_trades"],
                "Win Rate %":  metrics["win_rate_pct"],
                "Final $":     metrics["final_capital"],
            })

    results = pd.DataFrame(rows)
    pd.set_option("display.float_format", "{:.2f}".format)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 120)
    print("\n=== Backtest Results (starting capital: $10,000 per run) ===\n")
    print(results.to_string(index=False))
