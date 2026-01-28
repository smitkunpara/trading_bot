import pytest
from unittest.mock import MagicMock, patch
from bot.validators import validate_symbol, validate_side, validate_quantity, validate_price
from bot.orders import place_order
from click.testing import CliRunner
from cli import main

# --- Validator Tests ---

def test_validate_symbol():
    assert validate_symbol("btcusdt") == "BTCUSDT"
    with pytest.raises(ValueError):
        validate_symbol("")

def test_validate_side():
    assert validate_side("buy") == "BUY"
    assert validate_side("SELL") == "SELL"
    with pytest.raises(ValueError):
        validate_side("HOLD")

def test_validate_quantity():
    assert validate_quantity(0.1) == 0.1
    assert validate_quantity("0.5") == 0.5
    with pytest.raises(ValueError):
        validate_quantity(-1)

def test_validate_price():
    assert validate_price(50000, "LIMIT") == 50000.0
    with pytest.raises(ValueError):
        validate_price(None, "LIMIT")
    assert validate_price(None, "MARKET") is None

# --- Order Logic Tests ---

def test_place_order_market():
    mock_client = MagicMock()
    mock_client.futures_create_order.return_value = {'orderId': 123, 'status': 'NEW'}
    
    result = place_order(mock_client, "BTCUSDT", "BUY", "MARKET", 0.001)
    
    mock_client.futures_create_order.assert_called_with(
        symbol="BTCUSDT", side="BUY", type="MARKET", quantity=0.001
    )
    assert result['orderId'] == 123

def test_place_order_limit():
    mock_client = MagicMock()
    mock_client.futures_create_order.return_value = {'orderId': 123}
    
    place_order(mock_client, "BTCUSDT", "SELL", "LIMIT", 0.001, 50000)
    
    mock_client.futures_create_order.assert_called_with(
        symbol="BTCUSDT", side="SELL", type="LIMIT", quantity=0.001, price=50000, timeInForce="GTC"
    )

# --- CLI Tests ---

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert "CLI Tool to place orders" in result.output

@patch('cli.place_order')
@patch('cli.get_client')
def test_cli_market_order(mock_get_client, mock_place_order):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_place_order.return_value = {
        'orderId': 12345,
        'status': 'FILLED',
        'executedQty': 0.001,
        'avgPrice': 50000
    }
    
    runner = CliRunner()
    result = runner.invoke(main, [
        '--symbol', 'BTCUSDT',
        '--side', 'BUY',
        '--type', 'MARKET',
        '--quantity', '0.001'
    ])
    
    assert result.exit_code == 0
    assert "SUCCESS: Order Placed" in result.output
    assert "Order ID:     12345" in result.output
