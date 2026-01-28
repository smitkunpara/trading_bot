"""
Pytest configuration for integration tests.
"""

import pytest
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@pytest.fixture(scope="session")
def check_testnet_credentials():
    """Verify that testnet credentials are available."""
    api_key = os.getenv("BINANCE_API_KEY")
    secret_key = os.getenv("BINANCE_SECRET_KEY")
    
    if not api_key or not secret_key:
        pytest.skip("Testnet API credentials not found in .env file")
    
    return api_key, secret_key


@pytest.fixture
def test_symbol():
    """Standard test symbol for integration tests."""
    return "BTCUSDT"


@pytest.fixture
def small_quantity():
    """Small quantity for test orders to minimize costs."""
    return 0.002
