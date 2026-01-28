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

## 📋 Test Results

All tests passing:
- ✅ 36 validator tests + 26 other unit tests = 62 unit tests (mock)
- ✅ 4 integration tests (real API)
- **Total: 66 tests**

**Note**: Tests cover MARKET, LIMIT orders and basic validation. Algo order tests (STOP_MARKET, TAKE_PROFIT_MARKET, etc.) can be added for comprehensive coverage.

## ⚠️ Important Notes

### Integration Tests
- Integration tests will skip if credentials are missing
- Integration tests place small orders (0.002 BTC) to minimize costs
- Integration tests clean up after themselves (cancel orders, close positions)

### Algo Orders Now Supported
**Stop orders (STOP_MARKET, TAKE_PROFIT_MARKET, STOP, TAKE_PROFIT, TRAILING_STOP_MARKET) are NOW implemented** using the Binance Algo Order API:

- Endpoint: `POST /fapi/v1/algoOrder`
- Uses `algoType="CONDITIONAL"`
- Requires `triggerPrice` parameter
- Supports `workingType` (CONTRACT_PRICE or MARK_PRICE)
- TRAILING_STOP_MARKET uses `callbackRate` and `activatePrice`

**To add algo order integration tests**, create tests for:
- Placing STOP_MARKET orders
- Placing TAKE_PROFIT_MARKET orders
- Placing TRAILING_STOP_MARKET orders
- Canceling algo orders via `/fapi/v1/algoOrder`
- Querying algo orders

**Reference**: [Binance Algo Order API](https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/New-Algo-Order)
