# Command Examples

This guide demonstrates commands in the order you would use them for actual trading.

## 1. Check Account Balance

Start by viewing your account balance and available funds.
```bash
uv run python cli.py --account
```

## 2. Check Current Price

Check the current market price before placing orders.
```bash
uv run python cli.py --symbol BTCUSDT
```

## 3. Place Orders

### Market Order
Execute immediate buy at current market price.
```bash
uv run python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
```

### Limit Order
Place sell order at specific price.
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.002 --price 95000
```

### Stop Market Order (Protective Stop)
Triggers market sell when price drops to trigger price (protects long position).
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.002 --trigger-price 85000
```

### Take Profit Market Order
Triggers market sell when price rises to take profit.
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type TAKE_PROFIT_MARKET --quantity 0.002 --trigger-price 95000
```

### Stop Limit Order
Triggers limit order when price reaches stop trigger.
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.002 --trigger-price 85000 --price 84500
```

### Take Profit Limit Order
Triggers limit order to take profit at specific price.
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type TAKE_PROFIT --quantity 0.002 --trigger-price 95000 --price 95500
```

### Trailing Stop Market Order
Follows price up by callback rate, triggers when price drops by that percentage.
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type TRAILING_STOP_MARKET --quantity 0.002 --callback-rate 1.5
```

### Trailing Stop with Activation Price
Only activates trailing when price reaches activation price.
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type TRAILING_STOP_MARKET --quantity 0.002 --callback-rate 1.5 --activate-price 92000
```

## 4. View Orders

After placing orders, view them to confirm.

### List Open Orders
View all active orders waiting to be filled.
```bash
uv run python cli.py --symbol BTCUSDT --orders open
```

### List Closed Orders
View filled or canceled orders.
```bash
uv run python cli.py --symbol BTCUSDT --orders close
```

### List All Orders
View complete order history.
```bash
uv run python cli.py --symbol BTCUSDT --orders all
```

## 5. Cancel Order

Cancel a specific order using its ID.
```bash
uv run python cli.py --symbol BTCUSDT --cancel 12345678
```

## 6. View Positions

After orders are filled, check your positions.

### View All Positions
Display all open positions across symbols.
```bash
uv run python cli.py --positions
```

### View Specific Symbol Position
Display position for a specific trading pair.
```bash
uv run python cli.py --symbol BTCUSDT --positions
```

## 7. Close Position

Automatically close entire position for a symbol.
```bash
uv run python cli.py --symbol BTCUSDT --close-position
```

## 8. Advanced Options

### Using Mark Price
Use mark price for trigger instead of last price.
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.002 --trigger-price 85000 --working-type MARK_PRICE
```

### Enable Price Protection
Adds price protection to prevent trigger during extreme volatility.
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.002 --trigger-price 85000 --price-protect
```

## 9. Help

View all available commands and options.
```bash
uv run python cli.py --help
```

