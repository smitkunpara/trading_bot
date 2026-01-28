import logging
import sys
from pathlib import Path

def setup_logging(log_file: str = "trading_bot.log"):
    """Configures logging to file and console."""
    
    # Create logger
    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.INFO)
    
    # Formatters
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    
    # File Handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

# Initialize logger instance
logger = setup_logging()
