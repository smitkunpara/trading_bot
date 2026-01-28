"""
Tests for order management.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from bot.orders import OrderManager, OrderResult
from bot.client import BinanceClient, BinanceClientError


@pytest.fixture
def mock_client():
    """Create a mock Binance client."""
    client = Mock(spec=BinanceClient)
    return client


@pytest.fixture
def order_manager(mock_client):
    """Create an order manager with mock client."""
    manager = OrderManager(client=mock_client)
    return manager


class TestOrderManager:
    """Tests for OrderManager class."""
    
    def test_place_market_order_success(self, order_manager, mock_client):
        """Test successful market order placement."""
        mock_client.place_order.return_value = {
            "orderId": 123456,
            "status": "FILLED",
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "MARKET",
            "origQty": "0.01",
            "executedQty": "0.01",
            "avgPrice": "50000.00"
        }
        
        result = order_manager.place_market_order("BTCUSDT", "BUY", 0.01)
        
        assert result.success is True
        assert result.order_id == 123456
        assert result.status == "FILLED"
        assert result.executed_qty == 0.01
    
    def test_place_market_order_invalid_inputs(self, order_manager):
        """Test market order with invalid inputs."""
        result = order_manager.place_market_order("INVALID", "BUY", 0.01)
        
        assert result.success is False
        assert result.error_message is not None
    
    def test_place_limit_order_success(self, order_manager, mock_client):
        """Test successful limit order placement."""
        mock_client.place_order.return_value = {
            "orderId": 789012,
            "status": "NEW",
            "symbol": "ETHUSDT",
            "side": "SELL",
            "type": "LIMIT",
            "origQty": "0.1",
            "executedQty": "0",
            "price": "3000.00"
        }
        
        result = order_manager.place_limit_order("ETHUSDT", "SELL", 0.1, 3000.0)
        
        assert result.success is True
        assert result.order_id == 789012
        assert result.status == "NEW"
        assert result.price == 3000.0
    
    def test_place_limit_order_missing_price(self, order_manager):
        """Test limit order without price."""
        result = order_manager.place_limit_order("BTCUSDT", "BUY", 0.01, None)
        
        assert result.success is False
        assert "required" in result.error_message.lower()
    
    def test_place_order_api_error(self, order_manager, mock_client):
        """Test order placement with API error."""
        mock_client.place_order.side_effect = BinanceClientError(
            "Insufficient balance",
            code=-2010
        )
        
        result = order_manager.place_market_order("BTCUSDT", "BUY", 1000)
        
        assert result.success is False
        assert "Insufficient balance" in result.error_message
    
    def test_get_current_price_success(self, order_manager, mock_client):
        """Test getting current price."""
        mock_client.get_ticker_price.return_value = {"price": "50123.45"}
        
        price = order_manager.get_current_price("BTCUSDT")
        
        assert price == 50123.45
    
    def test_get_current_price_error(self, order_manager, mock_client):
        """Test getting price with error."""
        mock_client.get_ticker_price.side_effect = BinanceClientError("Symbol not found")
        
        price = order_manager.get_current_price("INVALIDUSDT")
        
        assert price is None
    
    def test_cancel_order_success(self, order_manager, mock_client):
        """Test successful order cancellation."""
        mock_client.cancel_order.return_value = {
            "orderId": 123456,
            "status": "CANCELED",
            "symbol": "BTCUSDT"
        }
        
        result = order_manager.cancel_order("BTCUSDT", 123456)
        
        assert result.success is True
        assert result.status == "CANCELED"


class TestOrderResult:
    """Tests for OrderResult dataclass."""
    
    def test_success_result(self):
        """Test successful order result."""
        result = OrderResult(
            success=True,
            order_id=123,
            status="FILLED",
            symbol="BTCUSDT",
            side="BUY",
            quantity=0.01,
            executed_qty=0.01
        )
        
        assert result.success is True
        assert result.order_id == 123
    
    def test_failure_result(self):
        """Test failed order result."""
        result = OrderResult(
            success=False,
            error_message="Insufficient funds"
        )
        
        assert result.success is False
        assert result.error_message == "Insufficient funds"
