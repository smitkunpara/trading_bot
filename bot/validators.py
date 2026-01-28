from typing import Optional

def validate_symbol(symbol: str) -> str:
    """Validates the trading symbol."""
    if not symbol or not isinstance(symbol, str):
        raise ValueError("Symbol must be a non-empty string.")
    return symbol.upper()

def validate_side(side: str) -> str:
    """Validates the order side (BUY or SELL)."""
    side_upper = side.upper()
    if side_upper not in ["BUY", "SELL"]:
        raise ValueError("Side must be 'BUY' or 'SELL'.")
    return side_upper

def validate_order_type(order_type: str) -> str:
    """Validates the order type (MARKET or LIMIT)."""
    type_upper = order_type.upper()
    if type_upper not in ["MARKET", "LIMIT"]:
        raise ValueError("Order type must be 'MARKET' or 'LIMIT'.")
    return type_upper

def validate_quantity(quantity: float) -> float:
    """Validates that quantity is a positive number."""
    try:
        qty = float(quantity)
        if qty <= 0:
            raise ValueError
        return qty
    except (ValueError, TypeError):
        raise ValueError("Quantity must be a positive number.")

def validate_price(price: Optional[float], order_type: str) -> Optional[float]:
    """Validates price for LIMIT orders."""
    if order_type.upper() == "LIMIT":
        try:
            p = float(price)
            if p <= 0:
                raise ValueError
            return p
        except (ValueError, TypeError):
            raise ValueError("Price is required and must be positive for LIMIT orders.")
    return None
