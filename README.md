# Trading — Automated Stock Trading System

A Python-based algorithmic trading system for US stocks. Pulls real market data, runs trading strategies, backtests them on historical data, and displays results in a Streamlit dashboard. Built to eventually support paper trading and live execution.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.11+ |
| Database | TimescaleDB (PostgreSQL 16 + time-series extension) |
| Market Data | `yfinance` |
| Backtesting | `vectorbt` |
| UI/Dashboard | `Streamlit` |
| Charts | `plotly` |
| Paper Trading (later) | Alpaca API |

---

## Prerequisites

- Python 3.11+
- Docker Desktop (Apple Silicon build for M/A-series Macs)
- Git

---

## Project Structure

```
trading/
├── .env                  # local credentials (never commit)
├── .gitignore
├── requirements.txt
├── data/
│   └── ingest.py         # pulls data from yfinance → DB
├── strategies/
│   └── sma.py            # SMA crossover strategy
├── backtest/
│   └── engine.py         # backtesting engine
└── app/
    └── main.py           # Streamlit UI entry point
```

---

## Database Setup (TimescaleDB via Docker)

### Start the database

```bash
docker run -d \
  --name stockdb \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=stockpass \
  timescale/timescaledb:latest-pg16
```

This downloads the TimescaleDB image and starts a PostgreSQL 16 server accessible at `localhost:5432`.

### Useful Docker commands

```bash
docker ps               # check if stockdb is running
docker start stockdb    # start after Mac restart
docker stop stockdb     # stop the container
docker logs stockdb     # view container logs
```

> Every time you restart your Mac, run `docker start stockdb` to bring the database back up.

### Connect with pgAdmin

- Host: `localhost`
- Port: `5432`
- Username: `postgres`
- Password: `stockpass`

---

## Environment Setup

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/trading.git
cd trading
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install yfinance psycopg2-binary sqlalchemy \
            pandas vectorbt streamlit plotly \
            python-dotenv
pip freeze > requirements.txt
```

### 4. Create `.env` file

```
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=stockpass
DB_NAME=stocks
```

> Make sure `.env` is listed in `.gitignore`.

---

## Running the App

```bash
source venv/bin/activate
streamlit run app/main.py
```

---

## Roadmap

- [x] Project scaffold and database setup
- [ ] Data ingestion — pull historical prices into TimescaleDB
- [ ] Strategy 1 — SMA Crossover
- [ ] Strategy 2 — RSI
- [ ] Strategy 3 — MACD
- [ ] Backtesting engine with metrics (return, drawdown, Sharpe ratio)
- [ ] Streamlit dashboard — signal viewer and portfolio tracker
- [ ] Paper trading via Alpaca API
- [ ] Live trading (after paper trading validation)
