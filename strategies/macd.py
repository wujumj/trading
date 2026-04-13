import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    return create_engine(url)


def get_signals(ticker: str, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """
    MACD strategy.
    Buy when the MACD line crosses above the signal line.
    Sell when the MACD line crosses below the signal line.
    """
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(
            text("SELECT time, close FROM prices WHERE ticker = :ticker ORDER BY time ASC"),
            conn,
            params={"ticker": ticker},
        )

    ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow, adjust=False).mean()

    df["macd"] = ema_fast - ema_slow
    df["macd_signal"] = df["macd"].ewm(span=signal, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]

    # Signal fires on crossover
    df["position"] = (df["macd"] > df["macd_signal"]).astype(int)
    df["signal"] = df["position"].diff().map({1.0: "BUY", -1.0: "SELL"}).fillna("")

    return df.reset_index(drop=True)


if __name__ == "__main__":
    for ticker in ["AAPL", "TSLA", "NVDA", "SPY"]:
        df = get_signals(ticker)
        signals = df[df["signal"] != ""][["time", "close", "macd", "macd_signal", "signal"]]
        print(f"\n{ticker} — MACD(12/26/9) signals:")
        print(signals.to_string(index=False))
