"""
Logging utilities
"""
import logging
import sys
from typing import Optional


def setup_logger(name: str = "schemasync",
                level: str = "INFO",
                format_str: Optional[str] = None,
                log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup logger with console and optional file handler

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        format_str: Log format string
        log_file: Optional log file path

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Default format
    if format_str is None:
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(format_str)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
