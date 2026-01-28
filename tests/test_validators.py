"""
Tests for input validation.
"""

import pytest
from bot.validators import OrderValidator, OrderSide, OrderType


class TestSymbolValidation:
    """Tests for symbol validation."""
    
    def test_valid_symbol(self):
        """Test valid symbol formats."""
        result = OrderValidator.validate_symbol("BTCUSDT")
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_valid_symbol_lowercase(self):
        """Test that lowercase symbols are accepted."""
        result = OrderValidator.validate_symbol("btcusdt")
        assert result.is_valid is True
    
    def test_valid_symbol_with_spaces(self):
        """Test that symbols with whitespace are trimmed."""
        result = OrderValidator.validate_symbol("  ETHUSDT  ")
        assert result.is_valid is True
    
    def test_invalid_symbol_empty(self):
        """Test empty symbol rejection."""
        result = OrderValidator.validate_symbol("")
        assert result.is_valid is False
        assert "empty" in result.error_message.lower()
    
    def test_invalid_symbol_format(self):
        """Test invalid symbol format rejection."""
        result = OrderValidator.validate_symbol("BTC-USD")
        assert result.is_valid is False
        assert "Invalid symbol" in result.error_message
    
    def test_invalid_symbol_no_usdt(self):
        """Test symbol without USDT suffix."""
        result = OrderValidator.validate_symbol("BTCETH")
        assert result.is_valid is False


class TestSideValidation:
    """Tests for side validation."""
    
    def test_valid_buy(self):
        """Test valid BUY side."""
        result = OrderValidator.validate_side("BUY")
        assert result.is_valid is True
    
    def test_valid_sell(self):
        """Test valid SELL side."""
        result = OrderValidator.validate_side("SELL")
        assert result.is_valid is True
    
    def test_valid_side_lowercase(self):
        """Test lowercase side."""
        result = OrderValidator.validate_side("buy")
        assert result.is_valid is True
    
    def test_invalid_side_empty(self):
        """Test empty side rejection."""
        result = OrderValidator.validate_side("")
        assert result.is_valid is False
    
    def test_invalid_side_value(self):
        """Test invalid side value."""
        result = OrderValidator.validate_side("LONG")
        assert result.is_valid is False
        assert "BUY or SELL" in result.error_message


class TestOrderTypeValidation:
    """Tests for order type validation."""
    
    def test_valid_market(self):
        """Test valid MARKET type."""
        result = OrderValidator.validate_order_type("MARKET")
        assert result.is_valid is True
    
    def test_valid_limit(self):
        """Test valid LIMIT type."""
        result = OrderValidator.validate_order_type("LIMIT")
        assert result.is_valid is True
    
    def test_valid_stop_limit(self):
        """Test valid STOP_LIMIT type."""
        result = OrderValidator.validate_order_type("STOP_LIMIT")
        assert result.is_valid is True
    
    def test_invalid_type(self):
        """Test invalid order type."""
        result = OrderValidator.validate_order_type("TRAILING")
        assert result.is_valid is False


class TestQuantityValidation:
    """Tests for quantity validation."""
    
    def test_valid_quantity(self):
        """Test valid quantity."""
        result = OrderValidator.validate_quantity(0.01)
        assert result.is_valid is True
    
    def test_quantity_too_small(self):
        """Test quantity below minimum."""
        result = OrderValidator.validate_quantity(0.0001)
        assert result.is_valid is False
        assert "minimum" in result.error_message.lower()
    
    def test_quantity_zero(self):
        """Test zero quantity."""
        result = OrderValidator.validate_quantity(0)
        assert result.is_valid is False
    
    def test_quantity_negative(self):
        """Test negative quantity."""
        result = OrderValidator.validate_quantity(-1)
        assert result.is_valid is False
    
    def test_quantity_very_large(self):
        """Test very large but valid quantity."""
        result = OrderValidator.validate_quantity(1000000)
        assert result.is_valid is True
    
    def test_quantity_exceeds_maximum(self):
        """Test quantity exceeding maximum."""
        result = OrderValidator.validate_quantity(100000000)
        assert result.is_valid is False
        assert "maximum" in result.error_message.lower()
    
    def test_quantity_none(self):
        """Test None quantity."""
        result = OrderValidator.validate_quantity(None)
        assert result.is_valid is False
        assert "cannot be empty" in result.error_message.lower()
    
    def test_quantity_string_conversion(self):
        """Test that string values are properly converted."""
        result = OrderValidator.validate_quantity("invalid")
        assert result.is_valid is False
        assert "must be a number" in result.error_message.lower()


class TestPriceValidation:
    """Tests for price validation."""
    
    def test_price_not_required_for_market(self):
        """Test that price is not required for MARKET orders."""
        result = OrderValidator.validate_price(None, "MARKET")
        assert result.is_valid is True
    
    def test_price_required_for_limit(self):
        """Test that price is required for LIMIT orders."""
        result = OrderValidator.validate_price(None, "LIMIT")
        assert result.is_valid is False
        assert "required" in result.error_message.lower()
    
    def test_valid_price_for_limit(self):
        """Test valid price for LIMIT order."""
        result = OrderValidator.validate_price(50000.0, "LIMIT")
        assert result.is_valid is True
    
    def test_invalid_price_zero(self):
        """Test zero price rejection."""
        result = OrderValidator.validate_price(0, "LIMIT")
        assert result.is_valid is False
    
    def test_price_negative(self):
        """Test negative price rejection."""
        result = OrderValidator.validate_price(-100, "LIMIT")
        assert result.is_valid is False
    
    def test_price_very_small(self):
        """Test very small valid price."""
        result = OrderValidator.validate_price(0.02, "LIMIT")
        assert result.is_valid is True
    
    def test_price_below_minimum(self):
        """Test price below minimum."""
        result = OrderValidator.validate_price(0.001, "LIMIT")
        assert result.is_valid is False
        assert "minimum" in result.error_message.lower()
    
    def test_price_very_large(self):
        """Test very large but valid price."""
        result = OrderValidator.validate_price(100000, "LIMIT")
        assert result.is_valid is True
    
    def test_price_exceeds_maximum(self):
        """Test price exceeding maximum."""
        result = OrderValidator.validate_price(2000000000, "LIMIT")
        assert result.is_valid is False
        assert "maximum" in result.error_message.lower()


class TestStopPriceValidation:
    """Tests for stop price validation."""
    
    def test_stop_price_required_for_stop_limit(self):
        """Test that stop price is required for STOP_LIMIT orders."""
        result = OrderValidator.validate_stop_price(None, "STOP_LIMIT")
        assert result.is_valid is False
        assert "required" in result.error_message.lower()
    
    def test_stop_price_not_required_for_market(self):
        """Test that stop price is not required for MARKET orders."""
        result = OrderValidator.validate_stop_price(None, "MARKET")
        assert result.is_valid is True
    
    def test_valid_stop_price(self):
        """Test valid stop price."""
        result = OrderValidator.validate_stop_price(50000.0, "STOP_LIMIT")
        assert result.is_valid is True
    
    def test_stop_price_zero(self):
        """Test zero stop price rejection."""
        result = OrderValidator.validate_stop_price(0, "STOP_LIMIT")
        assert result.is_valid is False
    
    def test_stop_price_negative(self):
        """Test negative stop price rejection."""
        result = OrderValidator.validate_stop_price(-100, "STOP_LIMIT")
        assert result.is_valid is False


class TestFullOrderValidation:
    """Tests for complete order validation."""
    
    def test_valid_market_order(self):
        """Test valid market order validation."""
        is_valid, params, errors = OrderValidator.validate_order(
            symbol="BTCUSDT",
            side="BUY",
            order_type="MARKET",
            quantity=0.01
        )
        assert is_valid is True
        assert params is not None
        assert len(errors) == 0
        assert params.symbol == "BTCUSDT"
        assert params.side == OrderSide.BUY
        assert params.order_type == OrderType.MARKET
    
    def test_valid_limit_order(self):
        """Test valid limit order validation."""
        is_valid, params, errors = OrderValidator.validate_order(
            symbol="ETHUSDT",
            side="SELL",
            order_type="LIMIT",
            quantity=0.1,
            price=3000.0
        )
        assert is_valid is True
        assert params is not None
        assert params.price == 3000.0
    
    def test_valid_stop_limit_order(self):
        """Test valid stop-limit order validation."""
        is_valid, params, errors = OrderValidator.validate_order(
            symbol="BTCUSDT",
            side="BUY",
            order_type="STOP_LIMIT",
            quantity=0.01,
            price=55000.0,
            stop_price=54000.0
        )
        assert is_valid is True
        assert params is not None
        assert params.price == 55000.0
        assert params.stop_price == 54000.0
    
    def test_invalid_order_missing_price(self):
        """Test limit order without price."""
        is_valid, params, errors = OrderValidator.validate_order(
            symbol="BTCUSDT",
            side="BUY",
            order_type="LIMIT",
            quantity=0.01
        )
        assert is_valid is False
        assert params is None
        assert len(errors) > 0
    
    def test_invalid_stop_limit_missing_stop_price(self):
        """Test stop-limit order without stop price."""
        is_valid, params, errors = OrderValidator.validate_order(
            symbol="BTCUSDT",
            side="BUY",
            order_type="STOP_LIMIT",
            quantity=0.01,
            price=55000.0
        )
        assert is_valid is False
        assert params is None
        assert any("Stop price" in err for err in errors)
    
    def test_multiple_validation_errors(self):
        """Test order with multiple errors."""
        is_valid, params, errors = OrderValidator.validate_order(
            symbol="",
            side="INVALID",
            order_type="LIMIT",
            quantity=-1
        )
        assert is_valid is False
        assert len(errors) >= 3
    
    def test_symbol_case_insensitive(self):
        """Test that symbols are properly normalized to uppercase."""
        is_valid, params, errors = OrderValidator.validate_order(
            symbol="btcusdt",
            side="buy",
            order_type="market",
            quantity=0.01
        )
        assert is_valid is True
        assert params.symbol == "BTCUSDT"
        assert params.side == OrderSide.BUY
        assert params.order_type == OrderType.MARKET
