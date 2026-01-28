"""
Integration tests for order placement using real Binance Futures Testnet API.

WARNING: These tests place actual orders on Binance Futures Testnet.
They require valid API credentials and will consume testnet balance.
"""

import pytest
import time
from bot.client import BinanceClient, BinanceClientError
from bot.orders import OrderManager


class TestRealOrderPlacement:
    """Test actual order placement on Binance Futures Testnet."""
    
    def test_place_and_cancel_limit_order(self, check_testnet_credentials, test_symbol, small_quantity):
        """
        Test placing a LIMIT order and then canceling it.
        
        This test:
        1. Places a LIMIT order far from current price (won't fill)
        2. Verifies order was created
        3. Cancels the order
        4. Verifies cancellation
        """
        manager = OrderManager()
        
        # Get current price
        current_price = manager.get_current_price(test_symbol)
        assert current_price is not None, "Failed to fetch current price"
        
        # Place limit SELL order 5% above current price (won't fill immediately)
        # Round to proper tick size (0.1 for BTCUSDT)
        limit_price = round(current_price * 1.05, 1)
        
        # Place order
        result = manager.place_limit_order(
            symbol=test_symbol,
            side="SELL",  # SELL order above current price
            quantity=small_quantity,
            price=limit_price
        )
        
        # Verify order was placed successfully
        assert result.success is True, f"Order placement failed: {result.error_message}"
        assert result.order_id is not None, "Order ID not returned"
        assert result.status in ["NEW", "PARTIALLY_FILLED"], f"Unexpected status: {result.status}"
        assert result.symbol == test_symbol
        assert result.side == "SELL"
        
        order_id = result.order_id
        print(f"\n✅ Order placed successfully. Order ID: {order_id}")
        
        # Wait a moment to ensure order is registered
        time.sleep(1)
        
        # Verify order appears in open orders
        open_orders = manager.get_open_orders(test_symbol)
        order_ids = [o.get("orderId") for o in open_orders]
        assert order_id in order_ids, "Order not found in open orders"
        print(f"✅ Order found in open orders list")
        
        # Cancel the order
        cancel_result = manager.cancel_order(test_symbol, order_id)
        assert cancel_result.success is True, f"Order cancellation failed: {cancel_result.error_message}"
        assert cancel_result.status == "CANCELED", f"Order not canceled properly: {cancel_result.status}"
        print(f"✅ Order canceled successfully")
        
        # Wait a moment for cancellation to register
        time.sleep(1)
        
        # Verify order no longer in open orders
        open_orders_after = manager.get_open_orders(test_symbol)
        order_ids_after = [o.get("orderId") for o in open_orders_after]
        assert order_id not in order_ids_after, "Canceled order still in open orders"
        print(f"✅ Order removed from open orders list")
    
    def test_place_market_order_and_verify_position(self, check_testnet_credentials, test_symbol, small_quantity):
        """
        Test placing a MARKET order and verifying position is created.
        
        This test:
        1. Places a MARKET BUY order
        2. Verifies order is filled
        3. Checks that position exists
        4. Closes the position
        5. Verifies position is closed
        """
        client = BinanceClient()
        manager = OrderManager(client=client)
        
        # Place market order
        result = manager.place_market_order(
            symbol=test_symbol,
            side="BUY",
            quantity=small_quantity
        )
        
        # Verify order was placed and filled
        assert result.success is True, f"Order placement failed: {result.error_message}"
        assert result.order_id is not None, "Order ID not returned"
        # MARKET orders should fill immediately or be NEW
        assert result.status in ["FILLED", "NEW"], f"Unexpected status: {result.status}"
        print(f"\n✅ Market order placed. Order ID: {result.order_id}, Status: {result.status}")
        
        # Wait for order to fill
        time.sleep(2)
        
        # Check position was created
        positions = client.get_position_info(test_symbol)
        btc_position = None
        for pos in positions:
            if pos.get("symbol") == test_symbol:
                btc_position = pos
                break
        
        assert btc_position is not None, f"Position not found for {test_symbol}"
        position_amt = float(btc_position.get("positionAmt", 0))
        assert position_amt != 0, "Position amount is zero"
        assert position_amt > 0, "Expected LONG position"
        print(f"✅ Position created: {position_amt} {test_symbol}")
        
        # Close the position
        close_result = client.close_position(test_symbol)
        assert close_result is not None, "Close position returned None"
        print(f"✅ Position close order placed. Order ID: {close_result.get('orderId')}")
        
        # Wait for position to close
        time.sleep(2)
        
        # Verify position is closed
        positions_after = client.get_position_info(test_symbol)
        btc_position_after = None
        for pos in positions_after:
            if pos.get("symbol") == test_symbol:
                btc_position_after = pos
                break
        
        if btc_position_after:
            position_amt_after = float(btc_position_after.get("positionAmt", 0))
            assert position_amt_after == 0, f"Position not fully closed: {position_amt_after}"
        
        print(f"✅ Position closed successfully")


class TestRealAPIConnectivity:
    """Test basic API connectivity and data retrieval."""
    
    def test_get_account_info(self, check_testnet_credentials):
        """Test fetching account information."""
        client = BinanceClient()
        
        account_info = client.get_account_info()
        
        assert account_info is not None, "Account info is None"
        assert "assets" in account_info, "No assets in account info"
        assert isinstance(account_info["assets"], list), "Assets is not a list"
        
        # Check for USDT asset
        usdt_asset = None
        for asset in account_info["assets"]:
            if asset.get("asset") == "USDT":
                usdt_asset = asset
                break
        
        assert usdt_asset is not None, "USDT asset not found"
        print(f"\n✅ Account info retrieved. USDT Balance: {usdt_asset.get('walletBalance')}")
    
    def test_get_ticker_price(self, check_testnet_credentials, test_symbol):
        """Test fetching ticker price."""
        client = BinanceClient()
        
        price_info = client.get_ticker_price(test_symbol)
        
        assert price_info is not None, "Price info is None"
        assert "price" in price_info, "No price in response"
        assert "symbol" in price_info, "No symbol in response"
        
        price = float(price_info["price"])
        assert price > 0, "Price is not positive"
        
        print(f"\n✅ Ticker price retrieved. {test_symbol}: ${price:,.2f}")
