"""
Pytest configuration and fixtures.
"""

import pytest
import logging
from unittest.mock import patch


@pytest.fixture(autouse=True)
def setup_test_logging():
    """Configure logging for tests."""
    logging.getLogger("trading_bot").setLevel(logging.DEBUG)
    logging.getLogger("trading_bot").handlers = []


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict('os.environ', {
        'BINANCE_API_KEY': 'test_api_key',
        'BINANCE_SECRET_KEY': 'test_secret_key',
        'BINANCE_TESTNET_URL': 'https://testnet.binancefuture.com'
    }):
        yield
