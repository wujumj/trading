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

## Alpaca Paper Trading Setup

### 1. Create an Alpaca account

Go to [alpaca.markets](https://alpaca.markets) and sign up. Choose **"Stock trading for individuals and business accounts"**.

### 2. Generate paper trading API keys

1. Log in to [app.alpaca.markets](https://app.alpaca.markets)
2. Make sure the top-left shows **Paper** (not Live)
3. Click **API** in the left sidebar
4. Click **Generate New Key** — copy both the Key ID and Secret Key (secret shown once only)

### 3. Add keys to `.env`

```
ALPACA_API_KEY=PKxxxxxxxxxxxxxxxx
ALPACA_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

### 4. Run the paper trader manually

```bash
source venv/bin/activate
python paper/trader.py
```

---

## Cron Job — Daily Auto-Run

The system is set up to automatically ingest fresh market data and run the paper trader every weekday at **2pm PT (5pm ET)**, one hour after US market close.

### View the current cron job

```bash
crontab -l
```

### Remove the cron job

```bash
crontab -e
```
Delete the line that contains `daily_run.sh`, save and exit.

Or remove it in one command:

```bash
crontab -l | grep -v "daily_run.sh" | crontab -
```

### Check the run log

```bash
cat "/Users/jerrymao/Documents/Jiren Mao/trading/scripts/daily_run.log"
```

### Re-add the cron job (if removed)

```bash
(crontab -l 2>/dev/null; echo '0 14 * * 1-5 "/Users/jerrymao/Documents/Jiren Mao/trading/scripts/daily_run.sh" >> "/Users/jerrymao/Documents/Jiren Mao/trading/scripts/daily_run.log" 2>&1') | crontab -
```

> Note: cron only runs when the Mac is awake. If the Mac is asleep at 2pm, run `python data/ingest.py` manually that day.

---

## Roadmap

- [x] Project scaffold and database setup
- [x] Data ingestion — pull historical prices into TimescaleDB
- [x] Strategy 1 — SMA Crossover
- [x] Strategy 2 — RSI
- [x] Strategy 3 — MACD
- [x] Backtesting engine with metrics (return, drawdown, Sharpe ratio)
- [x] Streamlit dashboard — signal viewer and portfolio tracker
- [x] Paper trading via Alpaca API
- [ ] Live trading (after paper trading validation)
