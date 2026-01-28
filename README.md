# Binance Futures Trading Bot

A Python CLI trading bot for placing orders on Binance Futures Testnet (USDT-M).

## Features

- ✅ Place **Market** and **Limit** orders
- ✅ Support both **BUY** and **SELL** sides
- ✅ **Stop-Limit** orders (Bonus feature)
- ✅ Input validation with clear error messages
- ✅ Comprehensive logging to file
- ✅ Rich CLI with colored output
- ✅ Proper error handling with custom `httpx` client

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package init
│   ├── client.py             # Binance API client wrapper (httpx based)
│   ├── orders.py             # Order placement logic
│   ├── validators.py         # Input validation
│   └── logging_config.py     # Logging configuration
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_validators.py    # Validator tests
│   ├── test_orders.py        # Order manager tests
│   ├── test_client.py        # Client tests
│   └── test_cli.py           # CLI tests
├── logs/                     # Log files directory
├── cli.py                    # CLI entry point
├── .env                      # Environment variables
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## Setup

### 1. Install uv (if not installed)

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Initialize the project

```bash
# Clone or extract the project
cd trading_bot

# Sync dependencies
uv sync
```

### 3. Configure Environment

Create a `.env` file in the project root with your credentials:

```env
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
BINANCE_TESTNET_URL=https://testnet.binancefuture.com
```

## Usage

### Place a Market Order

```bash
# BUY 0.01 BTC at market price
uv run python cli.py order BTCUSDT BUY MARKET 0.01

# SELL 0.1 ETH at market price
uv run python cli.py order ETHUSDT SELL MARKET 0.1
```

### Place a Limit Order

```bash
# BUY 0.01 BTC at $50,000
uv run python cli.py order BTCUSDT BUY LIMIT 0.01 --price 50000

# SELL 0.1 ETH at $3,500
uv run python cli.py order ETHUSDT SELL LIMIT 0.1 --price 3500
```

### Place a Stop-Limit Order (Bonus)

```bash
# BUY 0.01 BTC with stop at $55,000, limit at $55,500
uv run python cli.py order BTCUSDT BUY STOP_LIMIT 0.01 --price 55500 --stop-price 55000
```

### Get Current Price

```bash
uv run python cli.py price BTCUSDT
```

### View Account Info

```bash
uv run python cli.py account
```

### Cancel an Order

```bash
uv run python cli.py cancel BTCUSDT 12345678
```

### Enable Debug Logging

```bash
uv run python cli.py order BTCUSDT BUY MARKET 0.01 --debug
```

### View Help

```bash
uv run python cli.py --help
uv run python cli.py order --help
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v
```

## Log Files

Log files are automatically created in the `logs/` directory with timestamps.

## Assumptions

1. **Testnet Environment**: All operations are performed on Binance Futures Testnet.
2. **USDT-M Futures**: Only USDT-margined futures pairs are supported.
3. **Symbol Format**: Symbols must end with "USDT".
4. **Time in Force**: Default is GTC (Good Till Cancel) for limit orders.