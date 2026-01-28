# Binance Futures Trading Bot

A Python CLI trading bot for placing orders on Binance Futures Testnet (USDT-M).

## Features

- ✅ **Single Entry Point CLI**: Intuitive usage with flags.
- ✅ Place **Market** and **Limit** orders.
- ✅ Support both **BUY** and **SELL** sides.
- ✅ **Stop-Limit** orders (Bonus feature).
- ✅ **Order Management**: List open/closed orders and cancel active ones.
- ✅ Input validation with clear error messages.
- ✅ Comprehensive logging to file.


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

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

Then edit `.env` with your actual Binance API credentials.

## Usage

All actions are performed via `cli.py` using specific flags.

### 1. Check Price & Get Suggestions
Simply provide the symbol to see the current price and helpful command suggestions.

```bash
uv run python cli.py --symbol BTCUSDT
```

### 2. Place Orders

**Market Order:**
```bash
uv run python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
```

**Limit Order:**
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.002 --price 50000
```

**Stop-Limit Order:**
```bash
uv run python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.002 --price 55500 --stop-price 55000
```

### 3. Manage Orders

**List Open Orders:**
```bash
uv run python cli.py --symbol BTCUSDT --orders open
```

**List Order History (includes both open/closed):**
```bash
uv run python cli.py --symbol BTCUSDT --orders all
```

**Cancel an Order:**
```bash
uv run python cli.py --symbol BTCUSDT --cancel 12345678
```

### 4. Account Info

```bash
uv run python cli.py --account
```

### 5. Help

View all available options:

```bash
uv run python cli.py --help
```

## Development

### Install Dev Dependencies

To run tests, install the development dependencies:

```bash
uv sync --group dev
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v
```

## Assumptions

1. **Testnet Environment**: All operations are performed on Binance Futures Testnet.
2. **USDT-M Futures**: Only USDT-margined futures pairs are supported.
3. **Symbol Format**: Symbols must end with "USDT".
4. **Time in Force**: Default is GTC (Good Till Cancel) for limit orders.
5. **Quantity Requirements**: Orders must meet both minimum quantity and minimum notional value ($100) requirements. The bot validates these automatically and provides helpful error messages.
