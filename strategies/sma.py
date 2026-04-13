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


def get_signals(ticker: str, fast: int = 20, slow: int = 50) -> pd.DataFrame:
    """
    SMA Crossover strategy.
    Buy when the fast MA crosses above the slow MA.
    Sell when the fast MA crosses below the slow MA.
    """
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(
            text("SELECT time, close FROM prices WHERE ticker = :ticker ORDER BY time ASC"),
            conn,
            params={"ticker": ticker},
        )

    df["sma_fast"] = df["close"].rolling(fast).mean()
    df["sma_slow"] = df["close"].rolling(slow).mean()

    # 1 = fast above slow, -1 = fast below slow
    df["position"] = (df["sma_fast"] > df["sma_slow"]).astype(int)

    # Signal fires on the crossover day only
    df["signal"] = df["position"].diff()
    df["signal"] = df["signal"].map({1.0: "BUY", -1.0: "SELL"}).fillna("")

    return df.dropna(subset=["sma_slow"]).reset_index(drop=True)


if __name__ == "__main__":
    for ticker in ["AAPL", "TSLA", "NVDA", "SPY"]:
        df = get_signals(ticker)
        signals = df[df["signal"] != ""][["time", "close", "sma_fast", "sma_slow", "signal"]]
        print(f"\n{ticker} — SMA(20/50) signals:")
        print(signals.to_string(index=False))
