import os
from binance.client import Client
from dotenv import load_dotenv
from bot.logging_config import logger

def get_client() -> Client:
    """
    Initializes and returns a Binance Client connected to the Testnet.
    """
    load_dotenv()
    
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_SECRET_KEY")
    
    if not api_key or not api_secret:
        logger.error("API credentials missing in .env file.")
        raise ValueError("Please set BINANCE_API_KEY and BINANCE_SECRET_KEY in .env")

    logger.info("Initializing Binance Client for Testnet...")
    
    # Initialize client with testnet=True
    client = Client(api_key, api_secret, testnet=True)
    
    return client
