"""
Tests for Binance client.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import httpx

from bot.client import BinanceClient, BinanceClientError


class TestBinanceClient:
    """Tests for BinanceClient class."""
    
    @patch.dict('os.environ', {
        'BINANCE_API_KEY': 'test_api_key',
        'BINANCE_SECRET_KEY': 'test_secret_key',
        'BINANCE_TESTNET_URL': 'https://testnet.binancefuture.com'
    })
    def test_client_initialization(self):
        """Test client initialization with env variables."""
        client = BinanceClient()
        
        assert client.api_key == 'test_api_key'
        assert client.secret_key == 'test_secret_key'
        assert 'testnet' in client.base_url
    
    def test_client_initialization_with_params(self):
        """Test client initialization with parameters."""
        client = BinanceClient(
            api_key="my_api_key",
            secret_key="my_secret",
            base_url="https://custom.url"
        )
        
        assert client.api_key == "my_api_key"
        assert client.secret_key == "my_secret"
        assert client.base_url == "https://custom.url"
    
    @patch.dict('os.environ', {}, clear=True)
    def test_client_missing_credentials(self):
        """Test client initialization without credentials."""
        with pytest.raises(BinanceClientError) as exc_info:
            BinanceClient()
        
        assert "credentials" in str(exc_info.value).lower()
    
    def test_sign_request(self):
        """Test request signing."""
        client = BinanceClient(
            api_key="test_key",
            secret_key="test_secret"
        )
        
        params = {"symbol": "BTCUSDT", "timestamp": 1234567890}
        signature = client._sign_request(params)
        
        assert signature is not None
        assert len(signature) == 64  # SHA256 hex digest length
    
    @patch.dict('os.environ', {
        'BINANCE_API_KEY': 'test_api_key',
        'BINANCE_SECRET_KEY': 'test_secret_key'
    })
    def test_handle_response_success(self):
        """Test handling successful response."""
        client = BinanceClient()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"orderId": 123}
        
        result = client._handle_response(mock_response)
        
        assert result == {"orderId": 123}
    
    @patch.dict('os.environ', {
        'BINANCE_API_KEY': 'test_api_key',
        'BINANCE_SECRET_KEY': 'test_secret_key'
    })
    def test_handle_response_error(self):
        """Test handling error response."""
        client = BinanceClient()
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"code": -1121, "msg": "Invalid symbol"}
        
        with pytest.raises(BinanceClientError) as exc_info:
            client._handle_response(mock_response)
        
        assert exc_info.value.code == -1121
        assert "Invalid symbol" in str(exc_info.value)


class TestBinanceClientError:
    """Tests for BinanceClientError exception."""
    
    def test_error_creation(self):
        """Test error creation with all parameters."""
        error = BinanceClientError(
            message="Test error",
            code=-1000,
            response={"msg": "Details"}
        )
        
        assert str(error) == "Test error"
        assert error.code == -1000
        assert error.response == {"msg": "Details"}
    
    def test_error_minimal(self):
        """Test error creation with minimal parameters."""
        error = BinanceClientError("Simple error")
        
        assert str(error) == "Simple error"
        assert error.code is None
        assert error.response is None
