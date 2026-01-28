"""
Order placement and management logic.
"""

from typing import Optional
from dataclasses import dataclass

from bot.client import BinanceClient, BinanceClientError
from bot.validators import OrderValidator, OrderParams
from bot.logging_config import get_logger


@dataclass
class OrderResult:
    """Result of an order operation."""
    success: bool
    order_id: Optional[int] = None
    status: Optional[str] = None
    symbol: Optional[str] = None
    side: Optional[str] = None
    order_type: Optional[str] = None
    quantity: Optional[float] = None
    executed_qty: Optional[float] = None
    price: Optional[float] = None
    avg_price: Optional[float] = None
    error_message: Optional[str] = None
    raw_response: Optional[dict] = None


class OrderManager:
    """
    Manages order placement and tracking.
    """
    
    def __init__(self, client: Optional[BinanceClient] = None):
        """
        Initialize order manager.
        
        Args:
            client: Binance client instance (creates new if not provided)
        """
        self.client = client or BinanceClient()
        self.logger = get_logger()
    
    def _parse_order_response(self, response: dict) -> OrderResult:
        """
        Parse order response into OrderResult.
        
        Args:
            response: API response dictionary
        
        Returns:
            OrderResult with parsed data
        """
        return OrderResult(
            success=True,
            order_id=response.get("orderId"),
            status=response.get("status"),
            symbol=response.get("symbol"),
            side=response.get("side"),
            order_type=response.get("type"),
            quantity=float(response.get("origQty", 0)),
            executed_qty=float(response.get("executedQty", 0)),
            price=float(response.get("price", 0)) if response.get("price") else None,
            avg_price=float(response.get("avgPrice", 0)) if response.get("avgPrice") else None,
            raw_response=response
        )
    
    def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float
    ) -> OrderResult:
        """
        Place a market order.
        
        Args:
            symbol: Trading pair symbol
            side: Order side (BUY or SELL)
            quantity: Order quantity
        
        Returns:
            OrderResult with order details
        """
        self.logger.info(f"Placing MARKET order: {side} {quantity} {symbol}")
        
        # Get current price for validation
        try:
            current_price = self.get_current_price(symbol)
            if not current_price:
                return OrderResult(success=False, error_message="Could not fetch current price for validation")
        except Exception as e:
            self.logger.error(f"Failed to get current price: {e}")
            return OrderResult(success=False, error_message="Could not fetch current price for validation")
        
        # Validate inputs
        is_valid, order_params, errors = OrderValidator.validate_order(
            symbol=symbol,
            side=side,
            order_type="MARKET",
            quantity=quantity,
            current_price=current_price
        )
        
        if not is_valid:
            error_msg = "; ".join(errors)
            self.logger.error(f"Validation failed: {error_msg}")
            return OrderResult(success=False, error_message=error_msg)
        
        try:
            response = self.client.place_order(
                symbol=order_params.symbol,
                side=order_params.side.value,
                order_type="MARKET",
                quantity=order_params.quantity
            )
            
            result = self._parse_order_response(response)
            self.logger.info(f"MARKET order placed successfully. Order ID: {result.order_id}")
            return result
            
        except BinanceClientError as e:
            self.logger.error(f"Failed to place MARKET order: {e}")
            return OrderResult(success=False, error_message=str(e), raw_response=e.response)
    
    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC"
    ) -> OrderResult:
        """
        Place a limit order.
        
        Args:
            symbol: Trading pair symbol
            side: Order side (BUY or SELL)
            quantity: Order quantity
            price: Limit price
            time_in_force: Time in force (GTC, IOC, FOK)
        
        Returns:
            OrderResult with order details
        """
        self.logger.info(f"Placing LIMIT order: {side} {quantity} {symbol} @ {price}")
        
        # Get current price for validation
        try:
            current_price = self.get_current_price(symbol)
            if not current_price:
                return OrderResult(success=False, error_message="Could not fetch current price for validation")
        except Exception as e:
            self.logger.error(f"Failed to get current price: {e}")
            return OrderResult(success=False, error_message="Could not fetch current price for validation")
        
        # Validate inputs
        is_valid, order_params, errors = OrderValidator.validate_order(
            symbol=symbol,
            side=side,
            order_type="LIMIT",
            quantity=quantity,
            price=price,
            current_price=current_price
        )
        
        if not is_valid:
            error_msg = "; ".join(errors)
            self.logger.error(f"Validation failed: {error_msg}")
            return OrderResult(success=False, error_message=error_msg)
        
        try:
            response = self.client.place_order(
                symbol=order_params.symbol,
                side=order_params.side.value,
                order_type="LIMIT",
                quantity=order_params.quantity,
                price=order_params.price,
                time_in_force=time_in_force
            )
            
            result = self._parse_order_response(response)
            self.logger.info(f"LIMIT order placed successfully. Order ID: {result.order_id}")
            return result
            
        except BinanceClientError as e:
            self.logger.error(f"Failed to place LIMIT order: {e}")
            return OrderResult(success=False, error_message=str(e), raw_response=e.response)
    
    def place_algo_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        trigger_price: float,
        price: Optional[float] = None,
        working_type: str = "CONTRACT_PRICE",
        price_protect: bool = False,
        callback_rate: Optional[float] = None,
        activate_price: Optional[float] = None
    ) -> OrderResult:
        """
        Place an algo order (STOP_MARKET, TAKE_PROFIT_MARKET, STOP, TAKE_PROFIT, TRAILING_STOP_MARKET).
        
        Args:
            symbol: Trading pair symbol
            side: Order side (BUY or SELL)
            order_type: Algo order type
            quantity: Order quantity
            trigger_price: Trigger price (for STOP/TAKE_PROFIT types)
            price: Limit price (for STOP/TAKE_PROFIT, not MARKET types)
            working_type: MARK_PRICE or CONTRACT_PRICE (default CONTRACT_PRICE)
            price_protect: Enable price protection
            callback_rate: Callback rate for TRAILING_STOP_MARKET (0.1-10%)
            activate_price: Activation price for TRAILING_STOP_MARKET
        
        Returns:
            OrderResult with order details
        """
        self.logger.info(
            f"Placing {order_type} order: {side} {quantity} {symbol} @ trigger={trigger_price}"
        )
        
        # Get current price for validation
        try:
            current_price = self.get_current_price(symbol)
            if not current_price:
                return OrderResult(success=False, error_message="Could not fetch current price for validation")
        except Exception as e:
            self.logger.error(f"Failed to get current price: {e}")
            return OrderResult(success=False, error_message="Could not fetch current price for validation")
        
        # Validate inputs
        is_valid, order_params, errors = OrderValidator.validate_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            current_price=current_price,
            trigger_price=trigger_price,
            callback_rate=callback_rate
        )
        
        if not is_valid:
            error_msg = "; ".join(errors)
            self.logger.error(f"Validation failed: {error_msg}")
            return OrderResult(success=False, error_message=error_msg)
        
        try:
            response = self.client.place_algo_order(
                symbol=order_params.symbol,
                side=order_params.side.value,
                order_type=order_type,
                quantity=order_params.quantity,
                trigger_price=trigger_price,
                price=order_params.price,
                working_type=working_type,
                price_protect=price_protect,
                callback_rate=callback_rate,
                activate_price=activate_price
            )
            
            # Parse algo order response (different structure than regular orders)
            result = OrderResult(
                success=True,
                order_id=response.get("algoId"),
                status=response.get("algoStatus"),
                symbol=response.get("symbol"),
                side=response.get("side"),
                order_type=response.get("orderType"),
                quantity=float(response.get("quantity", 0)),
                executed_qty=0.0,  # Algo orders don't have immediate execution
                price=float(response.get("price", 0)) if response.get("price") else None,
                raw_response=response
            )
            self.logger.info(f"{order_type} order placed successfully. Algo ID: {result.order_id}")
            return result
            
        except BinanceClientError as e:
            self.logger.error(f"Failed to place {order_type} order: {e}")
            return OrderResult(success=False, error_message=str(e), raw_response=e.response)
    
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        trigger_price: Optional[float] = None,
        callback_rate: Optional[float] = None,
        activate_price: Optional[float] = None
    ) -> OrderResult:
        """
        Place an order of any type.
        
        Args:
            symbol: Trading pair symbol
            side: Order side (BUY or SELL)
            order_type: Order type (MARKET, LIMIT, or algo types)
            quantity: Order quantity
            price: Limit price (for LIMIT/STOP/TAKE_PROFIT orders)
            stop_price: Legacy parameter (not used)
            trigger_price: Trigger price (for algo orders)
            callback_rate: Callback rate (for TRAILING_STOP_MARKET)
            activate_price: Activation price (for TRAILING_STOP_MARKET)
        
        Returns:
            OrderResult with order details
        """
        order_type = order_type.upper()
        
        # Check if it's an algo order
        algo_order_types = ["STOP_MARKET", "TAKE_PROFIT_MARKET", "STOP", "TAKE_PROFIT", "TRAILING_STOP_MARKET"]
        
        if order_type in algo_order_types:
            return self.place_algo_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                trigger_price=trigger_price or stop_price,  # Support both parameters
                price=price,
                callback_rate=callback_rate,
                activate_price=activate_price
            )
        elif order_type == "MARKET":
            return self.place_market_order(symbol, side, quantity)
        elif order_type == "LIMIT":
            return self.place_limit_order(symbol, side, quantity, price)
        else:
            return OrderResult(
                success=False,
                error_message=f"Unsupported order type: {order_type}. Supported types: MARKET, LIMIT"
            )
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for a symbol.
        
        Args:
            symbol: Trading pair symbol
        
        Returns:
            Current price or None if error
        """
        try:
            response = self.client.get_ticker_price(symbol)
            return float(response.get("price", 0))
        except BinanceClientError as e:
            self.logger.error(f"Failed to get price for {symbol}: {e}")
            return None
    
    def cancel_order(self, symbol: str, order_id: int) -> OrderResult:
        """
        Cancel an existing order.
        
        Args:
            symbol: Trading pair symbol
            order_id: Order ID to cancel
        
        Returns:
            OrderResult with cancellation status
        """
        self.logger.info(f"Cancelling order {order_id} for {symbol}")
        
        try:
            response = self.client.cancel_order(symbol, order_id)
            result = self._parse_order_response(response)
            self.logger.info(f"Order {order_id} cancelled successfully")
            return result
        except BinanceClientError as e:
            self.logger.error(f"Failed to cancel order {order_id}: {e}")
            return OrderResult(success=False, error_message=str(e), raw_response=e.response)

    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        """Get open orders."""
        try:
            return self.client.get_open_orders(symbol)
        except BinanceClientError as e:
            self.logger.error(f"Failed to get open orders: {e}")
            return []

    def get_order_history(self, symbol: str, limit: int = 50) -> list:
        """Get order history."""
        try:
            return self.client.get_all_orders(symbol, limit)
        except BinanceClientError as e:
            self.logger.error(f"Failed to get order history: {e}")
            return []