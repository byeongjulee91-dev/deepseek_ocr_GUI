"""
Logging configuration for DeepSeek-OCR Desktop
Provides centralized logging with file and console output
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from PySide6.QtCore import QObject, Signal


class QtLogHandler(QObject, logging.Handler):
    """Custom log handler that emits Qt signals for GUI display"""

    log_signal = Signal(str, str)  # (level, message)

    def __init__(self):
        QObject.__init__(self)
        logging.Handler.__init__(self)

    def emit(self, record):
        """Emit log record as Qt signal"""
        try:
            msg = self.format(record)
            # Extract just the message part (without timestamp and level)
            # Format is: "HH:MM:SS | LEVEL | module | message"
            parts = msg.split(' | ', 3)
            if len(parts) >= 4:
                level = record.levelname
                message = parts[3]  # Just the message
            else:
                level = record.levelname
                message = msg

            self.log_signal.emit(level, message)
        except Exception:
            self.handleError(record)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
            )
        return super().format(record)


def setup_logger(name: str = "DeepSeekOCR", level: int = logging.DEBUG, gui_handler=None) -> logging.Logger:
    """
    Set up logger with file and console handlers

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Create logs directory
    log_dir = Path.home() / ".deepseek_ocr" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Log file path with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"deepseek_ocr_{timestamp}.log"

    # File handler (detailed, with rotation)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(funcName)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    # Console handler (less verbose, with colors)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Log initialization
    logger.info(f"Logger initialized. Log file: {log_file}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with the given name

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    # Get the root DeepSeekOCR logger
    root_logger = logging.getLogger("DeepSeekOCR")

    # If root logger not set up yet, set it up
    if not root_logger.handlers:
        setup_logger()

    # Return child logger
    return logging.getLogger(f"DeepSeekOCR.{name}")


# Utility functions for structured logging
def log_function_call(logger: logging.Logger):
    """Decorator to log function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Calling {func.__name__} with args={args[:3]}... kwargs={list(kwargs.keys())}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} completed successfully")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} failed with error: {e}", exc_info=True)
                raise
        return wrapper
    return decorator


def log_pdf_page(logger: logging.Logger, page_num: int, total_pages: int, status: str = "processing"):
    """Log PDF page processing status"""
    logger.info(f"PDF Page {page_num}/{total_pages} - {status}")


def log_ocr_result(logger: logging.Logger, text_length: int, has_boxes: bool = False):
    """Log OCR result summary"""
    logger.debug(f"OCR result: text_length={text_length}, has_bounding_boxes={has_boxes}")


def log_file_operation(logger: logging.Logger, operation: str, file_path: str, success: bool = True):
    """Log file operations"""
    status = "✓" if success else "✗"
    logger.info(f"{status} {operation}: {file_path}")


# Export main functions
__all__ = [
    'setup_logger',
    'get_logger',
    'log_function_call',
    'log_pdf_page',
    'log_ocr_result',
    'log_file_operation'
]
