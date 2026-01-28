"""
Input validation for trading bot parameters.
"""

import re
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class OrderSide(str, Enum):
    """Order side enumeration."""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Order type enumeration."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    # Algo Order Types
    STOP_MARKET = "STOP_MARKET"
    TAKE_PROFIT_MARKET = "TAKE_PROFIT_MARKET"
    STOP = "STOP"
    TAKE_PROFIT = "TAKE_PROFIT"
    TRAILING_STOP_MARKET = "TRAILING_STOP_MARKET"


@dataclass
class ValidationResult:
    """Result of validation check."""
    is_valid: bool
    error_message: Optional[str] = None


@dataclass
class OrderParams:
    """Validated order parameters."""
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "GTC"
    # Algo order parameters
    trigger_price: Optional[float] = None
    working_type: str = "CONTRACT_PRICE"
    price_protect: bool = False
    callback_rate: Optional[float] = None
    activate_price: Optional[float] = None


class OrderValidator:
    """Validates order parameters before submission."""
    
    # Common trading pairs on Binance Futures
    VALID_SYMBOLS_PATTERN = re.compile(r"^[A-Z]{2,10}USDT$")
    
    # Minimum quantity for most pairs
    MIN_QUANTITY = 0.001
    MAX_QUANTITY = 10000000
    
    # Price constraints
    MIN_PRICE = 0.01
    MAX_PRICE = 1000000000
    
    @classmethod
    def validate_symbol(cls, symbol: str) -> ValidationResult:
        """
        Validate trading symbol format.
        
        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT)
        
        Returns:
            ValidationResult with status and error message if invalid
        """
        if not symbol:
            return ValidationResult(False, "Symbol cannot be empty")
        
        symbol = symbol.upper().strip()
        
        if not cls.VALID_SYMBOLS_PATTERN.match(symbol):
            return ValidationResult(
                False, 
                f"Invalid symbol format: {symbol}. Expected format: XXXUSDT (e.g., BTCUSDT)"
            )
        
        return ValidationResult(True)
    
    @classmethod
    def validate_side(cls, side: str) -> ValidationResult:
        """
        Validate order side.
        
        Args:
            side: Order side (BUY or SELL)
        
        Returns:
            ValidationResult with status and error message if invalid
        """
        if not side:
            return ValidationResult(False, "Side cannot be empty")
        
        side = side.upper().strip()
        
        try:
            OrderSide(side)
            return ValidationResult(True)
        except ValueError:
            return ValidationResult(
                False, 
                f"Invalid side: {side}. Must be BUY or SELL"
            )
    
    @classmethod
    def validate_order_type(cls, order_type: str) -> ValidationResult:
        """
        Validate order type.
        
        Args:
            order_type: Type of order (MARKET, LIMIT, STOP_MARKET)
        
        Returns:
            ValidationResult with status and error message if invalid
        """
        if not order_type:
            return ValidationResult(False, "Order type cannot be empty")
        
        order_type = order_type.upper().strip()
        
        try:
            OrderType(order_type)
            return ValidationResult(True)
        except ValueError:
            valid_types = ", ".join([t.value for t in OrderType])
            return ValidationResult(
                False, 
                f"Invalid order type: {order_type}. Must be one of: {valid_types}"
            )
    
    @classmethod
    def validate_quantity(cls, quantity: float, current_price: Optional[float] = None) -> ValidationResult:
        """
        Validate order quantity.
        
        Args:
            quantity: Order quantity
            current_price: Current market price for notional value validation
        
        Returns:
            ValidationResult with status and error message if invalid
        """
        if quantity is None:
            return ValidationResult(False, "Quantity cannot be empty")
        
        try:
            qty = float(quantity)
        except (ValueError, TypeError):
            return ValidationResult(False, f"Invalid quantity: {quantity}. Must be a number")
        
        if qty <= 0:
            return ValidationResult(False, "Quantity must be greater than 0")
        
        if qty < cls.MIN_QUANTITY:
            return ValidationResult(
                False, 
                f"Quantity {qty} is below minimum: {cls.MIN_QUANTITY}"
            )
        
        if qty > cls.MAX_QUANTITY:
            return ValidationResult(
                False, 
                f"Quantity {qty} exceeds maximum: {cls.MAX_QUANTITY}"
            )
        
        # Check minimum notional value ($100) if price is available
        if current_price is not None:
            notional_value = qty * current_price
            min_notional = 100.0  # Binance minimum notional value
            if notional_value < min_notional:
                min_qty_needed = min_notional / current_price
                return ValidationResult(
                    False,
                    f"Order notional value (${notional_value:.2f}) is below minimum: ${min_notional}. "
                    f"Minimum quantity needed: {min_qty_needed:.6f}"
                )
        
        return ValidationResult(True)
    
    @classmethod
    def validate_price(cls, price: Optional[float], order_type: str) -> ValidationResult:
        """
        Validate order price.
        
        Args:
            price: Order price (required for LIMIT orders)
            order_type: Type of order
        
        Returns:
            ValidationResult with status and error message if invalid
        """
        order_type = order_type.upper().strip() if order_type else ""
        
        # Price is required for LIMIT orders only
        if order_type == "LIMIT":
            if price is None:
                return ValidationResult(
                    False, 
                    f"Price is required for {order_type} orders"
                )
            
            try:
                p = float(price)
            except (ValueError, TypeError):
                return ValidationResult(False, f"Invalid price: {price}. Must be a number")
            
            if p <= 0:
                return ValidationResult(False, "Price must be greater than 0")
            
            if p < cls.MIN_PRICE:
                return ValidationResult(
                    False, 
                    f"Price {p} is below minimum: {cls.MIN_PRICE}"
                )
            
            if p > cls.MAX_PRICE:
                return ValidationResult(
                    False, 
                    f"Price {p} exceeds maximum: {cls.MAX_PRICE}"
                )
        
        return ValidationResult(True)
    
    @classmethod
    def validate_trigger_price(cls, trigger_price: Optional[float], order_type: str) -> ValidationResult:
        """
        Validate trigger price for algo orders.
        
        Args:
            trigger_price: Trigger price
            order_type: Type of order
        
        Returns:
            ValidationResult with status and error message if invalid
        """
        order_type = order_type.upper().strip() if order_type else ""
        
        # Trigger price required for these algo order types
        if order_type in ["STOP_MARKET", "TAKE_PROFIT_MARKET", "STOP", "TAKE_PROFIT"]:
            if trigger_price is None:
                return ValidationResult(
                    False,
                    f"Trigger price is required for {order_type} orders"
                )
            
            try:
                tp = float(trigger_price)
            except (ValueError, TypeError):
                return ValidationResult(False, f"Invalid trigger price: {trigger_price}. Must be a number")
            
            if tp <= 0:
                return ValidationResult(False, "Trigger price must be greater than 0")
        
        return ValidationResult(True)
    
    @classmethod
    def validate_callback_rate(cls, callback_rate: Optional[float], order_type: str) -> ValidationResult:
        """
        Validate callback rate for TRAILING_STOP_MARKET orders.
        
        Args:
            callback_rate: Callback rate (0.1-10, representing 0.1%-10%)
            order_type: Type of order
        
        Returns:
            ValidationResult with status and error message if invalid
        """
        order_type = order_type.upper().strip() if order_type else ""
        
        if order_type == "TRAILING_STOP_MARKET":
            if callback_rate is None:
                return ValidationResult(
                    False,
                    "Callback rate is required for TRAILING_STOP_MARKET orders"
                )
            
            try:
                cr = float(callback_rate)
            except (ValueError, TypeError):
                return ValidationResult(False, f"Invalid callback rate: {callback_rate}. Must be a number")
            
            if cr < 0.1 or cr > 10:
                return ValidationResult(
                    False,
                    "Callback rate must be between 0.1 and 10 (representing 0.1%-10%)"
                )
        
        return ValidationResult(True)
    
    @classmethod
    def validate_order(
        cls,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        current_price: Optional[float] = None,
        trigger_price: Optional[float] = None,
        callback_rate: Optional[float] = None
    ) -> tuple[bool, Optional[OrderParams], list[str]]:
        """
        Validate all order parameters.
        
        Args:
            symbol: Trading pair symbol
            side: Order side (BUY/SELL)
            order_type: Order type (MARKET/LIMIT or algo types)
            quantity: Order quantity
            price: Order price (for LIMIT/STOP/TAKE_PROFIT orders)
            stop_price: Stop price (legacy, not used)
            current_price: Current market price for notional validation
            trigger_price: Trigger price (for algo orders)
            callback_rate: Callback rate (for TRAILING_STOP_MARKET)
        
        Returns:
            Tuple of (is_valid, OrderParams or None, list of error messages)
        """
        errors = []
        
        # Validate each field
        symbol_result = cls.validate_symbol(symbol)
        if not symbol_result.is_valid:
            errors.append(symbol_result.error_message)
        
        side_result = cls.validate_side(side)
        if not side_result.is_valid:
            errors.append(side_result.error_message)
        
        type_result = cls.validate_order_type(order_type)
        if not type_result.is_valid:
            errors.append(type_result.error_message)
        
        qty_result = cls.validate_quantity(quantity, current_price)
        if not qty_result.is_valid:
            errors.append(qty_result.error_message)
        
        price_result = cls.validate_price(price, order_type)
        if not price_result.is_valid:
            errors.append(price_result.error_message)
        
        # Validate trigger price for algo orders
        trigger_result = cls.validate_trigger_price(trigger_price, order_type)
        if not trigger_result.is_valid:
            errors.append(trigger_result.error_message)
        
        # Validate callback rate for TRAILING_STOP_MARKET
        callback_result = cls.validate_callback_rate(callback_rate, order_type)
        if not callback_result.is_valid:
            errors.append(callback_result.error_message)
        
        if errors:
            return False, None, errors
        
        # Create validated order params
        order_params = OrderParams(
            symbol=symbol.upper().strip(),
            side=OrderSide(side.upper().strip()),
            order_type=OrderType(order_type.upper().strip()),
            quantity=float(quantity),
            price=float(price) if price is not None else None,
            stop_price=None,
            trigger_price=float(trigger_price) if trigger_price is not None else None,
            callback_rate=float(callback_rate) if callback_rate is not None else None
        )
        
        return True, order_params, []