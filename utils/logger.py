"""
Structured logging utility for Life Cockpit automation.

Provides consistent logging across all automation scripts with:
- Structured JSON logging
- File rotation
- Console output with colors
- Configurable log levels
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import structlog
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class ColoredConsoleRenderer:
    """Custom console renderer with colors for better readability."""
    
    def __init__(self):
        self.colors = {
            'DEBUG': Fore.BLUE,
            'INFO': Fore.GREEN,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRITICAL': Fore.MAGENTA + Style.BRIGHT,
        }
    
    def __call__(self, logger, method_name, event_dict):
        # Get the log level
        level = event_dict.get('level', 'INFO')
        color = self.colors.get(level, Fore.WHITE)
        
        # Format the message
        timestamp = event_dict.get('timestamp', datetime.now().isoformat())
        module = event_dict.get('module', 'unknown')
        message = event_dict.get('event', '')
        
        # Add extra fields if present
        extra_fields = []
        for key, value in event_dict.items():
            if key not in ['level', 'timestamp', 'module', 'event']:
                extra_fields.append(f"{key}={value}")
        
        extra_str = f" | {' | '.join(extra_fields)}" if extra_fields else ""
        
        # Format the output
        formatted = f"{color}[{timestamp}] {level:8} | {module:15} | {message}{extra_str}{Style.RESET_ALL}"
        
        return formatted


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> structlog.BoundLogger:
    """
    Set up structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
    
    Returns:
        Configured structured logger
    """
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            ColoredConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Create the logger
    logger = structlog.get_logger()
    
    # Add file handler if log_file is specified
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        # Get the underlying stdlib logger and add the file handler
        stdlib_logger = logging.getLogger()
        stdlib_logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Module name (optional, will be inferred if not provided)
    
    Returns:
        Structured logger instance
    """
    if name is None:
        # Get the calling module name
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'unknown')
    
    return structlog.get_logger(name)


# Convenience functions for common log levels
def log_info(message: str, **kwargs):
    """Log an info message."""
    logger = get_logger()
    logger.info(message, **kwargs)


def log_warning(message: str, **kwargs):
    """Log a warning message."""
    logger = get_logger()
    logger.warning(message, **kwargs)


def log_error(message: str, **kwargs):
    """Log an error message."""
    logger = get_logger()
    logger.error(message, **kwargs)


def log_debug(message: str, **kwargs):
    """Log a debug message."""
    logger = get_logger()
    logger.debug(message, **kwargs)


# Initialize default logger
logger = get_logger(__name__)
