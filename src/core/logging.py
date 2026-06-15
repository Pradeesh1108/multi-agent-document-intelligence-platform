"""
Structured logging configuration for the platform.

Provides consistent, production-quality logging across all modules.
"""

import logging
import sys
from typing import Optional

from src.core.config import get_settings


def setup_logging(level: Optional[str] = None) -> None:
    """
    Configure application-wide logging.

    Args:
        level: Override log level. If None, uses settings.LOG_LEVEL.
    """
    settings = get_settings()
    log_level = getattr(logging, (level or settings.LOG_LEVEL).upper(), logging.INFO)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Console handler with structured format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    formatter = logging.Formatter(
        fmt="%(asctime)s │ %(levelname)-8s │ %(name)-30s │ %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("hpack").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Module name, typically __name__.

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)
