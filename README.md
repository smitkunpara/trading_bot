# Binance Futures Testnet Trading Bot

A Python CLI application to place Market and Limit orders on the Binance Futures Testnet.

## Prerequisites

- Python 3.x
- `uv` (for dependency management)
- Binance Futures Testnet Account

## Setup

1.  **Clone the repository** (if applicable) or navigate to the project directory.

2.  **Initialize and Install Dependencies**:
    ```bash
    uv sync
    ```
    Or if starting fresh:
    ```bash
    uv init
    uv add python-binance python-dotenv click
    ```

3.  **Configuration**:
    Create a `.env` file in the `trading_bot` directory with your API credentials:
    ```env
    BINANCE_API_KEY=your_api_key
    BINANCE_SECRET_KEY=your_secret_key
    BINANCE_TESTNET=True
    ```

## Usage

Run the CLI tool using `uv run python cli.py`.

### Market Order
Place a Market BUY order for BTCUSDT:
```bash
uv run python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Limit Order
Place a Limit SELL order for BTCUSDT:
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 50000
```

### Help
View all available options:
```bash
uv run python cli.py --help
```

## Testing

Run the test suite using `pytest`:
```bash
PYTHONPATH=. uv run pytest
```

## Logs

Logs are saved to `trading_bot.log` in the project directory. They contain details of all API requests and responses.

## Structure

- `bot/`: Core logic package.
    - `client.py`: Binance client wrapper.
    - `orders.py`: Order placement logic.
    - `validators.py`: Input validation.
    - `logging_config.py`: Logging setup.
- `cli.py`: CLI entry point.
- `tests/`: Test suite.
