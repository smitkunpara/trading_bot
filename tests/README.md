# Test Structure

This project has two types of tests:

## 📁 tests/unit/
**Mock tests** - Fast, isolated tests using mocked dependencies

- Don't require API credentials
- Don't make network calls
- Run quickly (< 1 second)
- Safe to run anytime

**Run unit tests:**
```bash
uv run pytest tests/unit/ -v
```

## 📁 tests/integration/
**Integration tests** - Real API tests using Binance Futures Testnet

- Require valid API credentials in `.env`
- Make actual API calls to Binance Testnet
- Place and cancel real orders
- Take longer to run (3-10 seconds)
- Consume testnet balance

**Run integration tests:**
```bash
uv run pytest tests/integration/ -v -s
```

### Integration Test Coverage

1. **test_get_account_info** - Verifies account info retrieval
2. **test_get_ticker_price** - Checks price fetching
3. **test_place_and_cancel_limit_order** - Places limit order and cancels it
4. **test_place_market_order_and_verify_position** - Places market order, verifies position, closes it

## 🎯 Run All Tests

**Unit tests only (default):**
```bash
uv run pytest tests/unit/
```

**Integration tests only:**
```bash
uv run pytest tests/integration/
```

**Both unit and integration:**
```bash
uv run pytest
```

## ⚠️ Notes

- Integration tests will skip if credentials are missing
- Integration tests place small orders (0.002 BTC) to minimize costs
- Integration tests clean up after themselves (cancel orders, close positions)
