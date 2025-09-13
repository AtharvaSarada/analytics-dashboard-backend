"""
Logging Configuration
Centralized logging setup for the application.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from app.core.config import settings


def setup_logging(log_file: Optional[str] = None) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        log_file: Optional log file path. If None, uses setting from config.
    """
    # Determine log file path
    if log_file is None:
        log_file = settings.LOG_FILE
    
    # Create log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[]
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter(log_format, date_format)
    )
    
    # Add console handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file:
        try:
            # Ensure log directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(
                logging.Formatter(log_format, date_format)
            )
            root_logger.addHandler(file_handler)
        except Exception as e:
            logging.warning(f"Could not set up file logging to {log_file}: {e}")
    
    # Set specific logger levels
    if settings.DEBUG:
        logging.getLogger("app").setLevel(logging.DEBUG)
        logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    else:
        logging.getLogger("app").setLevel(logging.INFO)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    # Suppress some noisy loggers in development
    if settings.ENVIRONMENT == "development":
        logging.getLogger("faker").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name, typically __name__
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
