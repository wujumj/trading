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


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def get_signals(ticker: str, period: int = 14, oversold: int = 30, overbought: int = 70) -> pd.DataFrame:
    """
    RSI strategy.
    Buy when RSI crosses up through the oversold threshold (default 30).
    Sell when RSI crosses down through the overbought threshold (default 70).
    """
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(
            text("SELECT time, close FROM prices WHERE ticker = :ticker ORDER BY time ASC"),
            conn,
            params={"ticker": ticker},
        )

    df["rsi"] = compute_rsi(df["close"], period)

    df["signal"] = ""
    prev_rsi = df["rsi"].shift(1)

    df.loc[(prev_rsi < oversold) & (df["rsi"] >= oversold), "signal"] = "BUY"
    df.loc[(prev_rsi > overbought) & (df["rsi"] <= overbought), "signal"] = "SELL"

    return df.dropna(subset=["rsi"]).reset_index(drop=True)


if __name__ == "__main__":
    for ticker in ["AAPL", "TSLA", "NVDA", "SPY"]:
        df = get_signals(ticker)
        signals = df[df["signal"] != ""][["time", "close", "rsi", "signal"]]
        print(f"\n{ticker} — RSI(14) signals:")
        print(signals.to_string(index=False))
