"""
Logging configuration for the trading bot.
"""

import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration with both file and console handlers.
    Respects DEBUG_FILE and DEBUG_TERMINAL environment variables.
    
    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    # Read debug settings from environment (default to false)
    debug_file = os.getenv("DEBUG_FILE", "false").lower() in ("true", "1", "yes")
    debug_terminal = os.getenv("DEBUG_TERMINAL", "false").lower() in ("true", "1", "yes")
    
    # Create logger
    logger = logging.getLogger("trading_bot")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    simple_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    )
    
    # File handler - only if DEBUG_FILE=true
    if debug_file:
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Create a unique log file name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"trading_bot_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        # Only log file creation if terminal debug is enabled
        if debug_terminal:
            logger.info(f"Logging initialized. Log file: {log_file}")
    
    # Console handler - only if DEBUG_TERMINAL=true
    if debug_terminal:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if log_level.upper() == "DEBUG" else logging.INFO)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_logger() -> logging.Logger:
    """
    Get the trading bot logger instance.
    
    Returns:
        Logger instance
    """
    return logging.getLogger("trading_bot")