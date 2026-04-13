# Session Summary — Project Kickoff

This file captures the full context of the first planning session so a new conversation can pick up exactly where we left off.

---

## Who the user is

- Name: Jerry (based on system path)
- Experience: Beginner investor. Bought Tesla stock, made ~30% profit passively. No prior algorithmic trading or coding experience mentioned beyond basic Python familiarity implied.
- Goal: Build a fully automated stock trading system to invest ~$40,000 in US stocks using algorithmic strategies. Wants the algorithm to make decisions, not himself.

---

## What we decided to build

An automated US stock trading system with:
- Real market data ingestion
- Multiple trading strategies (start simple, add more over time)
- Backtesting engine to validate strategies on historical data
- A visual dashboard (Streamlit web app) to monitor signals and results
- Paper trading (simulate with live prices before real money)
- Eventually: live trading via broker API

Style: **short-term trading** (days to weeks). Start as a prototype and iterate.

---

## Tech Stack (agreed upon)

| Layer | Tool | Notes |
|---|---|---|
| Language | Python 3.11+ | |
| Database | TimescaleDB (PostgreSQL 16) | User asked for scalable SQL DB over CSV. TimescaleDB chosen because stock data is time-series. |
| Market Data | `yfinance` | Free historical data from Yahoo Finance |
| Backtesting | `vectorbt` | Fast, visual, beginner-friendly |
| UI | `Streamlit` | Python → web app with minimal extra code |
| Charts | `plotly` | Interactive charts |
| Paper Trading (Phase 5) | Alpaca API | Free broker with paper + live trading |
| ORM | `SQLAlchemy` + `psycopg2` | Python ↔ PostgreSQL |

---

## Planned phases

| Phase | Description | Status |
|---|---|---|
| 1 | Data foundation — ingest historical prices into TimescaleDB | Not started |
| 2 | First strategies — SMA crossover, RSI, MACD | Not started |
| 3 | Backtesting engine — P&L, drawdown, Sharpe ratio | Not started |
| 4 | Streamlit dashboard — signals, portfolio tracker | Not started |
| 5 | Paper trading via Alpaca API | Not started |
| 6 | Live trading with real money (cautiously) | Not started |

---

## What has been done so far

- GitHub repo created by user, already set up remotely
- Repo cloned/exists locally at: `/Users/jerrymao/Documents/Jiren Mao/trading`
- Python virtual environment created at `trading/venv`
- Docker Desktop installed (Apple Silicon build — user is on MacBook Neo with A19 chip, ARM architecture)
- TimescaleDB Docker container created and running:
  ```bash
  docker run -d \
    --name stockdb \
    -p 5432:5432 \
    -e POSTGRES_PASSWORD=stockpass \
    timescale/timescaledb:latest-pg16
  ```
- pgAdmin installed for database GUI access
- `README.md` written to the repo root
- This `start.md` written to capture session context

---

## What to do next (Phase 1)

Pick up here in the next session:

1. Create the project folder structure:
   ```
   data/ingest.py
   strategies/sma.py
   backtest/engine.py
   app/main.py
   ```

2. Create `.env` file:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=stockpass
   DB_NAME=stocks
   ```

3. Add `.env` and `venv/` to `.gitignore`

4. Install Python dependencies:
   ```bash
   source venv/bin/activate
   pip install yfinance psycopg2-binary sqlalchemy pandas vectorbt streamlit plotly python-dotenv
   pip freeze > requirements.txt
   ```

5. Write `data/ingest.py` — connects to TimescaleDB, creates a `prices` hypertable, downloads historical data for a watchlist (AAPL, TSLA, NVDA, SPY) using `yfinance`, and inserts it into the DB.

6. Write a minimal `app/main.py` Streamlit app that queries the DB and renders a price chart for a selected ticker.

---

## Key reminders

- Run `docker start stockdb` after every Mac restart before working
- Never commit `.env` to GitHub
- Paper trade before touching the $40k
- Backtesting pitfalls to watch for: lookahead bias, survivorship bias, overfitting
