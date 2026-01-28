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
    def test_order_command_market_success(self, mock_manager_class):
        """Test market order command success."""
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
        
        result = runner.invoke(app, ["order", "--symbol", "BTCUSDT", "--side", "BUY", "--type", "MARKET", "--quantity", "0.01"])
        
        assert result.exit_code == 0
        assert "12345" in result.output
        assert "FILLED" in result.output
    
    @patch('cli.OrderManager')
    def test_order_command_limit_success(self, mock_manager_class):
        """Test limit order command success."""
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
            "order", "--symbol", "ETHUSDT", "--side", "SELL", "--type", "LIMIT", "--quantity", "0.1", "--price", "3000"
        ])
        
        assert result.exit_code == 0
        assert "67890" in result.output
    
    @patch('cli.OrderManager')
    def test_order_command_failure(self, mock_manager_class):
        """Test order command failure."""
        mock_manager = Mock()
        mock_manager.place_order.return_value = OrderResult(
            success=False,
            error_message="Insufficient balance"
        )
        mock_manager_class.return_value = mock_manager
        
        result = runner.invoke(app, ["order", "--symbol", "BTCUSDT", "--side", "BUY", "--type", "MARKET", "--quantity", "1000"])
        
        assert result.exit_code == 1
        assert "Insufficient balance" in result.output or "Failed" in result.output
    
    @patch('cli.OrderManager')
    def test_price_command(self, mock_manager_class):
        """Test price command."""
        mock_manager = Mock()
        mock_manager.get_current_price.return_value = 50000.0
        mock_manager_class.return_value = mock_manager
        
        result = runner.invoke(app, ["price", "--symbol", "BTCUSDT"])
        
        assert result.exit_code == 0
        assert "50,000" in result.output or "50000" in result.output
    
    def test_help_command(self):
        """Test help display."""
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "Binance" in result.output
    
    def test_order_help(self):
        """Test order command help."""
        result = runner.invoke(app, ["order", "--help"])
        
        assert result.exit_code == 0
        assert "symbol" in result.output.lower()
        assert "side" in result.output.lower()

    @patch('cli.OrderManager')
    def test_orders_command_history(self, mock_manager_class):
        """Test orders command with history."""
        mock_manager = Mock()
        mock_manager.get_order_history.return_value = [{
            "orderId": 123,
            "type": "MARKET",
            "side": "BUY",
            "price": "0",
            "origQty": "0.1",
            "status": "FILLED",
            "time": 1672531200000
        }]
        mock_manager_class.return_value = mock_manager
        
        result = runner.invoke(app, ["orders", "--symbol", "BTCUSDT", "--history"])
        
        assert result.exit_code == 0
        assert "123" in result.output
        assert "FILLED" in result.output

    @patch('cli.OrderManager')
    def test_positions_command(self, mock_manager_class):
        """Test positions command."""
        mock_manager = Mock()
        mock_manager.get_positions.return_value = [{
            "symbol": "BTCUSDT",
            "positionAmt": "0.1",
            "entryPrice": "50000",
            "markPrice": "51000",
            "unRealizedProfit": "100"
        }]
        mock_manager_class.return_value = mock_manager
        
        result = runner.invoke(app, ["positions"])
        
        assert result.exit_code == 0
        assert "BTCUSDT" in result.output
        assert "100" in result.output