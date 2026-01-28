# Command Examples

## Basic Commands

### Check Current Price
Shows current market price and helpful suggestions.
```bash
uv run python cli.py --symbol BTCUSDT
```

### View Account Information
Display account balance and available funds.
```bash
uv run python cli.py --account
```

## Market Orders

### Buy Market Order
Execute immediate buy at current market price.
```bash
uv run python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
```

### Sell Market Order
Execute immediate sell at current market price.
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.002
```

## Limit Orders

### Buy Limit Order
Place buy order at specific price or lower.
```bash
uv run python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.002 --price 85000
```

### Sell Limit Order
Place sell order at specific price or higher.
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.002 --price 95000
```

## Stop Market Orders (Algo)

### Sell Stop Market (Protective Stop for Longs)
Triggers market sell when price drops to trigger price.
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.002 --trigger-price 85000
```

### Buy Stop Market (Protective Stop for Shorts)
Triggers market buy when price rises to trigger price.
```bash
uv run python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.002 --trigger-price 95000
```

## Take Profit Market Orders (Algo)

### Sell Take Profit Market
Triggers market sell when price rises to take profit.
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type TAKE_PROFIT_MARKET --quantity 0.002 --trigger-price 95000
```

### Buy Take Profit Market
Triggers market buy when price drops to take profit.
```bash
uv run python cli.py --symbol BTCUSDT --side BUY --type TAKE_PROFIT_MARKET --quantity 0.002 --trigger-price 85000
```

## Stop Limit Orders (Algo)

### Sell Stop Limit
Triggers limit order when price reaches stop trigger.
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.002 --trigger-price 85000 --price 84500
```

### Buy Stop Limit
Triggers limit order when price reaches stop trigger.
```bash
uv run python cli.py --symbol BTCUSDT --side BUY --type STOP --quantity 0.002 --trigger-price 95000 --price 95500
```

## Take Profit Limit Orders (Algo)

### Sell Take Profit Limit
Triggers limit order to take profit at specific price.
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type TAKE_PROFIT --quantity 0.002 --trigger-price 95000 --price 95500
```

### Buy Take Profit Limit
Triggers limit order to take profit at specific price.
```bash
uv run python cli.py --symbol BTCUSDT --side BUY --type TAKE_PROFIT --quantity 0.002 --trigger-price 85000 --price 84500
```

## Trailing Stop Market Orders (Algo)

### Sell Trailing Stop
Follows price up by callback rate, triggers when price drops by that percentage.
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type TRAILING_STOP_MARKET --quantity 0.002 --callback-rate 1.5
```

### Buy Trailing Stop
Follows price down by callback rate, triggers when price rises by that percentage.
```bash
uv run python cli.py --symbol BTCUSDT --side BUY --type TRAILING_STOP_MARKET --quantity 0.002 --callback-rate 1.5
```

### Trailing Stop with Activation Price
Only activates trailing when price reaches activation price.
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type TRAILING_STOP_MARKET --quantity 0.002 --callback-rate 1.5 --activate-price 92000
```

## Order Management

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
View complete order history (open + closed).
```bash
uv run python cli.py --symbol BTCUSDT --orders all
```

### Cancel Order
Cancel specific order by ID.
```bash
uv run python cli.py --symbol BTCUSDT --cancel 12345678
```

## Position Management

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

### Close Position
Automatically close entire position for symbol.
```bash
uv run python cli.py --symbol BTCUSDT --close-position
```

## Advanced Options

### Using Mark Price (Instead of Contract Price)
Use mark price for trigger instead of last price.
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.002 --trigger-price 85000 --working-type MARK_PRICE
```

### Enable Price Protection
Adds price protection to prevent trigger during extreme volatility.
```bash
uv run python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.002 --trigger-price 85000 --price-protect
```

## Help

### View All Options
Display complete list of available commands and arguments.
```bash
uv run python cli.py --help
```
