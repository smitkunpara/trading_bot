# Binance Futures Trading Bot

Python CLI for Binance Futures Testnet with support for Market, Limit, and Algo orders (Stop, Take Profit, Trailing Stop).

## Features

- ✅ Market & Limit orders
- ✅ Algo orders (Stop Market, Take Profit, Trailing Stop)
- ✅ Position management
- ✅ Order management
- ✅ Account information

## Setup

### 1. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Install Dependencies

```bash
cd trading_bot
uv sync
```

### 3. Configure API Keys

```bash
cp .env.example .env
# Edit .env with  Binance API credentials
```

## Quick Start

**Check Price:**
```bash
uv run python cli.py --symbol BTCUSDT
```

**Market Order:**
```bash
uv run python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
```

**Limit Order:**
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.002 --price 95000
```

**Stop Market:**
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.002 --trigger-price 85000
```

**Trailing Stop:**
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type TRAILING_STOP_MARKET --quantity 0.002 --callback-rate 1.5
```

**View Positions:**
```bash
uv run python cli.py --positions
```

For more examples, see [EXAMPLES.md](EXAMPLES.md)

## CLI Arguments

| Argument | Description |
|----------|-------------|
| `--symbol` | Trading pair (e.g., BTCUSDT) |
| `--side` | BUY or SELL |
| `--type` | Order type: MARKET, LIMIT, STOP_MARKET, TAKE_PROFIT_MARKET, STOP, TAKE_PROFIT, TRAILING_STOP_MARKET |
| `--quantity` | Order quantity |
| `--price` | Limit price (for LIMIT, STOP, TAKE_PROFIT orders) |
| `--trigger-price` | Trigger price for algo orders |
| `--callback-rate` | Callback rate for TRAILING_STOP_MARKET (0.1-10%) |
| `--activate-price` | Activation price for TRAILING_STOP_MARKET |
| `--working-type` | CONTRACT_PRICE or MARK_PRICE (default: CONTRACT_PRICE) |
| `--price-protect` | Enable price protection for algo orders |
| `--orders` | List orders: open, close, or all |
| `--cancel` | Cancel order by ID |
| `--positions` | Show open positions |
| `--close-position` | Close position for symbol |
| `--account` | Show account information |

## Development

**Install Dependencies:**
```bash
uv sync --group dev
```

**Run Tests:**
```bash
uv run pytest
```

Tests are automated via GitHub Actions. See test results in the [Actions tab](https://github.com/smitkunpara/trading_bot/actions).

