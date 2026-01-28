"""
Tests for CLI interface.
"""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, Mock

from cli import app
from bot.orders import OrderResult


runner = CliRunner()


class TestCLI:
    """Tests for CLI commands."""
    
    @patch('cli.OrderManager')
    def test_place_order_market_success(self, mock_manager_class):
        """Test market order placement."""
        mock_manager = Mock()
        mock_manager.place_order.return_value = OrderResult(
            success=True,
            order_id=12345,
            status="FILLED",
            symbol="BTCUSDT",
            side="BUY",
            order_type="MARKET",
            quantity=0.01,
            executed_qty=0.01
        )
        mock_manager_class.return_value = mock_manager
        
        # New syntax: root command with flags
        result = runner.invoke(app, [
            "--symbol", "BTCUSDT",
            "--side", "BUY",
            "--type", "MARKET",
            "--quantity", "0.01"
        ])
        
        assert result.exit_code == 0
        assert "12345" in result.output
        assert "FILLED" in result.output
    
    @patch('cli.OrderManager')
    def test_place_order_limit_success(self, mock_manager_class):
        """Test limit order placement."""
        mock_manager = Mock()
        mock_manager.place_order.return_value = OrderResult(
            success=True,
            order_id=67890,
            status="NEW",
            symbol="ETHUSDT",
            side="SELL",
            order_type="LIMIT",
            quantity=0.1,
            executed_qty=0,
            price=3000.0
        )
        mock_manager_class.return_value = mock_manager
        
        result = runner.invoke(app, [
            "--symbol", "ETHUSDT",
            "--side", "SELL",
            "--type", "LIMIT",
            "--quantity", "0.1",
            "--price", "3000"
        ])
        
        assert result.exit_code == 0
        assert "67890" in result.output
    
    @patch('cli.OrderManager')
    def test_price_check_and_suggestions(self, mock_manager_class):
        """Test price check and suggestions (when only symbol is provided)."""
        mock_manager = Mock()
        mock_manager.get_current_price.return_value = 50000.0
        mock_manager_class.return_value = mock_manager
        
        result = runner.invoke(app, ["--symbol", "BTCUSDT"])
        
        assert result.exit_code == 0
        assert "50,000" in result.output or "50000" in result.output
        assert "Suggestions:" in result.output
        assert "--side BUY" in result.output

    @patch('cli.OrderManager')
    def test_list_orders_open(self, mock_manager_class):
        """Test listing open orders."""
        mock_manager = Mock()
        mock_manager.get_open_orders.return_value = [{
            "orderId": 111,
            "type": "LIMIT",
            "side": "BUY",
            "price": "40000",
            "origQty": "0.1",
            "status": "NEW",
            "time": 1672531200000
        }]
        mock_manager_class.return_value = mock_manager
        
        result = runner.invoke(app, ["--symbol", "BTCUSDT", "--orders", "open"])
        
        assert result.exit_code == 0
        assert "111" in result.output
        assert "Open Orders" in result.output

    @patch('cli.OrderManager')
    def test_list_orders_history(self, mock_manager_class):
        """Test listing order history."""
        mock_manager = Mock()
        mock_manager.get_order_history.return_value = [{
            "orderId": 222,
            "type": "MARKET",
            "side": "SELL",
            "price": "0",
            "origQty": "0.5",
            "status": "FILLED",
            "time": 1672531200000
        }]
        mock_manager_class.return_value = mock_manager
        
        # Test 'all' shows all orders
        result = runner.invoke(app, ["--symbol", "BTCUSDT", "--orders", "all"])
        
        assert result.exit_code == 0
        assert "222" in result.output
        assert "All Orders" in result.output

    @patch('cli.OrderManager')
    def test_cancel_order(self, mock_manager_class):
        """Test cancelling an order."""
        mock_manager = Mock()
        mock_manager.cancel_order.return_value = OrderResult(
            success=True,
            order_id=999,
            status="CANCELED"
        )
        mock_manager_class.return_value = mock_manager
        
        result = runner.invoke(app, ["--symbol", "BTCUSDT", "--cancel", "999"])
        
        assert result.exit_code == 0
        assert "Order placed successfully" in result.output  # CLI uses generic success message method
        assert "CANCELED" in result.output
        assert "999" in result.output

    @patch('cli.OrderManager')
    def test_missing_symbol_for_orders(self, mock_manager_class):
        """Test error when listing orders without symbol."""
        result = runner.invoke(app, ["--orders", "open"])
        assert result.exit_code == 1
        assert "--symbol is required" in result.output

    def test_help(self):
        """Test help display."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Binance Futures Trading Bot CLI" in result.output
