import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from strategies import sma, rsi, macd

load_dotenv()

API_KEY    = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

client = TradingClient(API_KEY, SECRET_KEY, paper=True)

WATCHLIST = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "META", "AMZN",
    "JPM", "GS", "BAC",
    "TSLA", "F", "GM",
    "JNJ", "UNH", "PFE",
    "XOM", "CVX",
    "SPY", "QQQ", "IWM",
    "WMT", "RBLX", "SONY", "BABA", "BIDU",
]

STRATEGIES = {
    "SMA": sma.get_signals,
    "RSI": rsi.get_signals,
    "MACD": macd.get_signals,
}

# Strategy to use for live signals
ACTIVE_STRATEGY = "SMA"

# Dollar amount per trade
TRADE_AMOUNT = 1000.0


def get_account():
    account = client.get_account()
    print(f"Account: {account.id}")
    print(f"Cash:    ${float(account.cash):,.2f}")
    print(f"Equity:  ${float(account.equity):,.2f}")
    return account


def get_open_positions():
    positions = client.get_all_positions()
    return {p.symbol: p for p in positions}


def place_order(symbol: str, side: OrderSide, notional: float = TRADE_AMOUNT):
    order = MarketOrderRequest(
        symbol=symbol,
        notional=round(notional, 2),  # dollar amount (fractional shares)
        side=side,
        time_in_force=TimeInForce.DAY,
    )
    result = client.submit_order(order)
    print(f"  Order placed: {side.value.upper()} ${notional:.2f} of {symbol} — id: {result.id}")
    return result


def run_signals():
    """
    Check today's signals for all tickers and place paper orders accordingly.
    """
    print(f"\n=== Paper Trader — Strategy: {ACTIVE_STRATEGY} ===\n")
    get_account()
    print()

    positions = get_open_positions()
    get_signals = STRATEGIES[ACTIVE_STRATEGY]

    for ticker in WATCHLIST:
        df = get_signals(ticker)
        latest = df.iloc[-1]
        signal = latest["signal"]

        if signal == "BUY" and ticker not in positions:
            print(f"{ticker}: BUY signal")
            try:
                place_order(ticker, OrderSide.BUY)
            except Exception as e:
                print(f"  Error: {e}")

        elif signal == "SELL" and ticker in positions:
            print(f"{ticker}: SELL signal — closing position")
            try:
                client.close_position(ticker)
                print(f"  Position closed for {ticker}")
            except Exception as e:
                print(f"  Error: {e}")

        else:
            if signal:
                print(f"{ticker}: {signal} signal but {'already holding' if signal == 'BUY' else 'no position'} — skipping")

    print("\nDone.")


if __name__ == "__main__":
    run_signals()
