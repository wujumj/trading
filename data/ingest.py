import os
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

WATCHLIST = ["AAPL", "TSLA", "NVDA", "SPY"]

def get_engine():
    url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)


def setup_db(engine):
    with engine.connect() as conn:
        # Create the TimescaleDB extension if not already enabled
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))

        # Create the prices table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS prices (
                time        TIMESTAMPTZ NOT NULL,
                ticker      TEXT        NOT NULL,
                open        DOUBLE PRECISION,
                high        DOUBLE PRECISION,
                low         DOUBLE PRECISION,
                close       DOUBLE PRECISION,
                volume      BIGINT
            );
        """))

        # Check if hypertable already exists before converting
        result = conn.execute(text("""
            SELECT COUNT(*) FROM timescaledb_information.hypertables
            WHERE hypertable_name = 'prices';
        """))
        if result.scalar() == 0:
            conn.execute(text(
                "SELECT create_hypertable('prices', 'time');"
            ))

        # Unique constraint to prevent duplicate rows on re-runs
        conn.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS prices_time_ticker_idx
            ON prices (time, ticker);
        """))

        conn.commit()
    print("Database ready.")


def ingest(engine, ticker: str, period: str = "2y"):
    print(f"Downloading {ticker}...")
    df = yf.download(ticker, period=period, auto_adjust=True, progress=False)

    if df.empty:
        print(f"  No data returned for {ticker}, skipping.")
        return

    # Flatten multi-level columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    })
    df.index.name = "time"
    df = df.reset_index()
    df["ticker"] = ticker
    df["time"] = pd.to_datetime(df["time"], utc=True)
    df = df[["time", "ticker", "open", "high", "low", "close", "volume"]]

    with engine.connect() as conn:
        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT INTO prices (time, ticker, open, high, low, close, volume)
                VALUES (:time, :ticker, :open, :high, :low, :close, :volume)
                ON CONFLICT (time, ticker) DO NOTHING;
            """), row.to_dict())
        conn.commit()

    print(f"  Inserted {len(df)} rows for {ticker}.")


if __name__ == "__main__":
    engine = get_engine()
    setup_db(engine)
    for ticker in WATCHLIST:
        ingest(engine, ticker)
    print("Done.")
