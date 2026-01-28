# Binance Futures Trading Bot

A Python CLI trading bot for placing orders on Binance Futures Testnet (USDT-M).

## Features

- ✅ **Single Entry Point CLI**: Intuitive usage with flags.
- ✅ Place **Market** and **Limit** orders.
- ✅ Place **Algo Orders**: STOP_MARKET, TAKE_PROFIT_MARKET, STOP, TAKE_PROFIT, TRAILING_STOP_MARKET
- ✅ Support both **BUY** and **SELL** sides.
- ✅ **Position Management**: View open positions and close them with a single command.
- ✅ **Order Management**: List open/closed orders and cancel active ones.
- ✅ Input validation with clear error messages.
- ✅ Comprehensive logging to file.

### ✅ Algo Order API Integrated

**Stop and Take Profit orders are NOW supported** via the Binance Algo Order API:

**Supported Order Types:**
- `STOP_MARKET` - Stop-loss market order (triggers market order at stop price)
- `TAKE_PROFIT_MARKET` - Take-profit market order
- `STOP` - Stop-loss limit order (triggers limit order at stop price)
- `TAKE_PROFIT` - Take-profit limit order
- `TRAILING_STOP_MARKET` - Dynamic stop that follows price movement

**Key Parameters:**
- `--trigger-price` - Price that triggers the algo order
- `--callback-rate` - For TRAILING_STOP_MARKET (0.1-10, representing 0.1%-10%)
- `--activate-price` - Activation price for TRAILING_STOP_MARKET
- `--working-type` - CONTRACT_PRICE (default) or MARK_PRICE
- `--price-protect` - Enable price protection

**Reference**: [Binance Algo Order API Documentation](https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/New-Algo-Order)


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
uv run python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.002 --price 95000
```

**Stop-Market Order (Algo Order):**
```bash
# BUY STOP: Triggers when price goes UP to trigger price (protective stop for shorts)
uv run python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.002 --trigger-price 95000

# SELL STOP: Triggers when price goes DOWN to trigger price (protective stop for longs)
uv run python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.002 --trigger-price 85000
```

**Take-Profit Market Order (Algo Order):**
```bash
# BUY TAKE_PROFIT: Triggers when price goes DOWN to trigger price
uv run python cli.py --symbol BTCUSDT --side BUY --type TAKE_PROFIT_MARKET --quantity 0.002 --trigger-price 85000

# SELL TAKE_PROFIT: Triggers when price goes UP to trigger price
uv run python cli.py --symbol BTCUSDT --side SELL --type TAKE_PROFIT_MARKET --quantity 0.002 --trigger-price 95000
```

**Stop-Limit Order (Algo Order):**
```bash
# Triggers at stop price, then places limit order at specified price
uv run python cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.002 --trigger-price 85000 --price 84500
```

**Trailing Stop Market (Algo Order):**
```bash
# Follows price by callback rate %, triggers when price reverses
uv run python cli.py --symbol BTCUSDT --side SELL --type TRAILING_STOP_MARKET --quantity 0.002 --callback-rate 1.0 --activate-price 92000
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

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py           # Binance API wrapper (GET/POST/DELETE requests)
│   ├── orders.py           # Order management (place/cancel/query)
│   ├── validators.py       # Input validation (symbols, prices, quantities)
│   └── logging_config.py   # Logging setup
├── tests/
│   ├── unit/              # Mock tests (fast, no API calls)
│   │   ├── test_cli.py
│   │   ├── test_client.py
│   │   ├── test_orders.py
│   │   └── test_validators.py
│   ├── integration/       # Real API tests (requires credentials)
│   │   ├── test_real_orders.py
│   │   └── conftest.py
│   └── README.md          # Test documentation
├── cli.py                 # Main CLI entry point
├── .env.example           # Example environment variables
├── pyproject.toml         # Project dependencies and configuration
└── README.md              # This file
```

## Implementation Details

### API Endpoints Used
- `GET /fapi/v1/ticker/price` - Get current market price
- `GET /fapi/v2/account` - Get account information
- `GET /fapi/v2/positionRisk` - Get position information
- `POST /fapi/v1/order` - Place MARKET/LIMIT orders
- `DELETE /fapi/v1/order` - Cancel orders
- `GET /fapi/v1/openOrders` - List open orders
- `GET /fapi/v1/allOrders` - Get order history

### Order Types Supported
- **MARKET**: Executes immediately at current market price
- **LIMIT**: Executes only at specified price or better
- **STOP_MARKET**: Algo order that triggers market order at trigger price
- **TAKE_PROFIT_MARKET**: Algo order that triggers market order for profit taking
- **STOP**: Algo order that triggers limit order at trigger price
- **TAKE_PROFIT**: Algo order that triggers limit order for profit taking
- **TRAILING_STOP_MARKET**: Dynamic stop that follows price by callback rate

### Order Types NOT Supported
- None - All major order types are now supported via regular and algo order APIs!

## Assumptions

1. **Testnet Environment**: All operations are performed on Binance Futures Testnet.
2. **USDT-M Futures**: Only USDT-margined futures pairs are supported.
3. **Symbol Format**: Symbols must end with "USDT".
4. **Time in Force**: Default is GTC (Good Till Cancel) for limit orders.
5. **Quantity Requirements**: Orders must meet both minimum quantity and minimum notional value ($100) requirements. The bot validates these automatically and provides helpful error messages.
