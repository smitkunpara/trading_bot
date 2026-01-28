# Binance Futures Trading Bot

A Python CLI trading bot for placing orders on Binance Futures Testnet (USDT-M).

## Features

- ✅ **Single Entry Point CLI**: Intuitive usage with flags.
- ✅ Place **Market** and **Limit** orders.
- ✅ Support both **BUY** and **SELL** sides.
- ✅ **Position Management**: View open positions and close them with a single command.
- ✅ **Order Management**: List open/closed orders and cancel active ones.
- ✅ Input validation with clear error messages.
- ✅ Comprehensive logging to file.

**Note:** Stop-Market and Stop-Limit orders require Binance Algo Order API endpoints, which are not currently implemented in this bot.


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

### 3. Manage Orders

**List Open Orders:**
```bash
uv run python cli.py --symbol BTCUSDT --orders open
```

**List Closed Orders (FILLED/CANCELED only):**
```bash
uv run python cli.py --symbol BTCUSDT --orders close
```

**List All Orders (both open and closed):**
```bash
uv run python cli.py --symbol BTCUSDT --orders all
```

**Cancel an Order:**
```bash
uv run python cli.py --symbol BTCUSDT --cancel 12345678
```

### 4. Position Management

**View All Open Positions:**
```bash
uv run python cli.py --positions
```

**View Positions for Specific Symbol:**
```bash
uv run python cli.py --symbol BTCUSDT --positions
```

**Close Position:**
```bash
uv run python cli.py --symbol BTCUSDT --close-position
```

> **Note:** To close a position, you don't need to specify the quantity or side. The bot automatically detects your current position and places a MARKET order in the opposite direction to close it. Each position is identified by its symbol, and closing is done automatically based on the position size.

### 5. Account Info

```bash
uv run python cli.py --account
```

### 6. Help

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

This project has two test suites:

### Unit Tests (Mock)
Fast tests using mocked dependencies (no API calls):

```bash
# Run unit tests
uv run pytest tests/unit/ -v
```

### Integration Tests (Real API)
Tests that make actual calls to Binance Futures Testnet:

```bash
# Run integration tests
uv run pytest tests/integration/ -v -s
```

**Note:** Integration tests require valid API credentials in `.env` and will place/cancel real orders on the testnet.

### Run All Tests

```bash
# Run all tests (unit + integration)
uv run pytest -v
```

**Test Coverage:**
- ✅ 62 unit tests (mock)
- ✅ 4 integration tests (real API)
- **Total: 66 tests**

See [tests/README.md](tests/README.md) for detailed test documentation.

## Assumptions

1. **Testnet Environment**: All operations are performed on Binance Futures Testnet.
2. **USDT-M Futures**: Only USDT-margined futures pairs are supported.
3. **Symbol Format**: Symbols must end with "USDT".
4. **Time in Force**: Default is GTC (Good Till Cancel) for limit orders.
5. **Quantity Requirements**: Orders must meet both minimum quantity and minimum notional value ($100) requirements. The bot validates these automatically and provides helpful error messages.
