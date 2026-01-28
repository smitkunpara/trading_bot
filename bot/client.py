"""
Binance Futures API client wrapper.
"""

import os
import time
import hmac
import hashlib
from typing import Any, Optional
from urllib.parse import urlencode

import httpx
from dotenv import load_dotenv

from bot.logging_config import get_logger


# Load environment variables
load_dotenv()


class BinanceClientError(Exception):
    """Custom exception for Binance API errors."""
    
    def __init__(self, message: str, code: Optional[int] = None, response: Optional[dict] = None):
        super().__init__(message)
        self.code = code
        self.response = response


class BinanceClient:
    """
    Wrapper for Binance Futures Testnet API.
    
    Handles authentication, request signing, and API communication.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize Binance client.
        
        Args:
            api_key: Binance API key (defaults to env variable)
            secret_key: Binance secret key (defaults to env variable)
            base_url: API base URL (defaults to testnet)
        """
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.secret_key = secret_key or os.getenv("BINANCE_SECRET_KEY")
        self.base_url = base_url or os.getenv("BINANCE_TESTNET_URL", "https://testnet.binancefuture.com")
        
        self.logger = get_logger()
        
        if not self.api_key or not self.secret_key:
            raise BinanceClientError(
                "API credentials not found. Set BINANCE_API_KEY and BINANCE_SECRET_KEY in .env"
            )
        
        # HTTP client with timeout
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=30.0,
            headers={
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        
        self.logger.info(f"Binance client initialized with base URL: {self.base_url}")
    
    def _get_timestamp(self) -> int:
        """Get current timestamp in milliseconds."""
        return int(time.time() * 1000)
    
    def _sign_request(self, params: dict) -> str:
        """
        Sign request parameters with HMAC SHA256.
        
        Args:
            params: Request parameters
        
        Returns:
            Signature string
        """
        query_string = urlencode(params)
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _handle_response(self, response: httpx.Response) -> dict:
        """
        Handle API response and raise appropriate errors.
        
        Args:
            response: HTTP response object
        
        Returns:
            Response JSON data
        
        Raises:
            BinanceClientError: If API returns an error
        """
        try:
            data = response.json()
        except Exception:
            data = {"raw_response": response.text}
        
        self.logger.debug(f"API Response Status: {response.status_code}")
        self.logger.debug(f"API Response Data: {data}")
        
        if response.status_code >= 400:
            error_code = data.get("code", response.status_code)
            error_msg = data.get("msg", "Unknown error")
            
            self.logger.error(f"API Error [{error_code}]: {error_msg}")
            
            raise BinanceClientError(
                message=f"Binance API Error [{error_code}]: {error_msg}",
                code=error_code,
                response=data
            )
        
        return data
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        signed: bool = True
    ) -> dict:
        """
        Make API request.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint
            params: Request parameters
            signed: Whether to sign the request
        
        Returns:
            Response data
        """
        params = params or {}
        
        if signed:
            params["timestamp"] = self._get_timestamp()
            params["signature"] = self._sign_request(params)
        
        if endpoint.startswith("/fapi/"):
            url = endpoint
        else:
            url = f"/fapi/v1{endpoint}"
        
        self.logger.info(f"API Request: {method} {url}")
        self.logger.debug(f"Request params: {params}")
        
        try:
            if method.upper() == "GET":
                response = self.client.get(url, params=params)
            elif method.upper() == "POST":
                response = self.client.post(url, data=params)
            elif method.upper() == "DELETE":
                response = self.client.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return self._handle_response(response)
            
        except httpx.TimeoutException:
            self.logger.error("Request timed out")
            raise BinanceClientError("Request timed out. Please try again.")
        except httpx.NetworkError as e:
            self.logger.error(f"Network error: {e}")
            raise BinanceClientError(f"Network error: {e}")
    
    def get_exchange_info(self) -> dict:
        """Get exchange information."""
        return self._request("GET", "/exchangeInfo", signed=False)
    
    def get_account_info(self) -> dict:
        """Get account information."""
        return self._request("GET", "/fapi/v2/account")
    
    def get_ticker_price(self, symbol: str) -> dict:
        """
        Get current price for a symbol.
        
        Args:
            symbol: Trading pair symbol
        
        Returns:
            Price information
        """
        return self._request("GET", "/ticker/price", {"symbol": symbol}, signed=False)
    
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "GTC"
    ) -> dict:
        """
        Place an order on Binance Futures.
        
        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT)
            side: Order side (BUY or SELL)
            order_type: Order type (MARKET, LIMIT, STOP)
            quantity: Order quantity
            price: Limit price (required for LIMIT orders)
            stop_price: Stop price (for STOP orders)
            time_in_force: Time in force (GTC, IOC, FOK)
        
        Returns:
            Order response data
        """
        params = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": quantity
        }
        
        # Handle different order types
        if order_type.upper() == "LIMIT":
            params["price"] = price
            params["timeInForce"] = time_in_force
        elif order_type.upper() == "STOP_LIMIT":
            params["type"] = "STOP"
            params["price"] = price
            params["stopPrice"] = stop_price
            params["timeInForce"] = time_in_force
        
        self.logger.info(f"Placing {order_type} order: {side} {quantity} {symbol}")
        
        return self._request("POST", "/order", params)
    
    def get_order(self, symbol: str, order_id: int) -> dict:
        """
        Get order details.
        
        Args:
            symbol: Trading pair symbol
            order_id: Order ID
        
        Returns:
            Order details
        """
        params = {
            "symbol": symbol.upper(),
            "orderId": order_id
        }
        return self._request("GET", "/order", params)
    
    def cancel_order(self, symbol: str, order_id: int) -> dict:
        """
        Cancel an order.
        
        Args:
            symbol: Trading pair symbol
            order_id: Order ID
        
        Returns:
            Cancellation response
        """
        params = {
            "symbol": symbol.upper(),
            "orderId": order_id
        }
        return self._request("DELETE", "/order", params)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        """
        Get all open orders.
        
        Args:
            symbol: Optional trading pair symbol
        
        Returns:
            List of open orders
        """
        params = {}
        if symbol:
            params["symbol"] = symbol.upper()
        return self._request("GET", "/openOrders", params)

    def get_all_orders(self, symbol: str, limit: int = 50) -> list:
        """
        Get all orders (active, canceled, or filled).
        
        Args:
            symbol: Trading pair symbol
            limit: Limit the number of orders returned (max 1000)
        
        Returns:
            List of orders
        """
        params = {
            "symbol": symbol.upper(),
            "limit": limit
        }
        return self._request("GET", "/allOrders", params)

    def get_position_risk(self, symbol: Optional[str] = None) -> list:
        """
        Get current position information.

        Args:
            symbol: Optional trading pair symbol

        Returns:
            List of positions
        """
        params = {}
        if symbol:
            params["symbol"] = symbol.upper()
        return self._request("GET", "/fapi/v2/positionRisk", params)
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
        self.logger.info("Binance client closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()