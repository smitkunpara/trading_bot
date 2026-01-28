from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from bot.logging_config import logger
from typing import Optional, Dict, Any

def place_order(
    client: Client,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None
) -> Dict[str, Any]:
    """
    Places an order on Binance Futures Testnet.
    """
    logger.info(f"Preparing to place order: {side} {quantity} {symbol} @ {order_type} {price if price else ''}")
    
    params = {
        'symbol': symbol,
        'side': side,
        'type': order_type,
        'quantity': quantity,
    }
    
    if order_type == "LIMIT":
        if price is None:
            raise ValueError("Price must be provided for LIMIT orders.")
        params['price'] = price
        params['timeInForce'] = 'GTC'  # Good Till Cancelled is standard for Limit
    
    try:
        logger.info(f"Sending API request with params: {params}")
        
        # Use futures_create_order for USDT-M Futures
        order = client.futures_create_order(**params)
        
        logger.info(f"Order placed successfully: {order['orderId']}")
        logger.debug(f"Full order response: {order}")
        return order
        
    except BinanceAPIException as e:
        logger.error(f"Binance API Error: {e.status_code} - {e.message}")
        raise
    except BinanceRequestException as e:
        logger.error(f"Binance Request Error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        raise
