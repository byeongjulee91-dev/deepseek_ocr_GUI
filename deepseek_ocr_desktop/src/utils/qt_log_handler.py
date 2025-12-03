"""
Qt Log Handler
Custom logging handler that emits Qt signals for GUI integration
"""

import logging
from PySide6.QtCore import QObject, Signal


class QtLogHandler(QObject, logging.Handler):
    """
    Custom logging handler that emits Qt signals
    Allows logging messages to be displayed in GUI widgets
    """

    # Signal emitted when a log record is created
    log_signal = Signal(str, str)  # (level, message)

    def __init__(self):
        QObject.__init__(self)
        logging.Handler.__init__(self)

        # Set formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        self.setFormatter(formatter)

    def emit(self, record):
        """
        Emit a log record as a Qt signal

        Args:
            record: LogRecord instance
        """
        try:
            # Format the message
            message = self.format(record)

            # Emit signal with level and message
            self.log_signal.emit(record.levelname, message)

        except Exception:
            self.handleError(record)


# Global instance
_qt_handler = None


def get_qt_log_handler() -> QtLogHandler:
    """
    Get or create the global Qt log handler

    Returns:
        QtLogHandler instance
    """
    global _qt_handler

    if _qt_handler is None:
        _qt_handler = QtLogHandler()

    return _qt_handler


def attach_qt_handler_to_logger(logger_name: str = "DeepSeekOCR"):
    """
    Attach Qt log handler to a logger

    Args:
        logger_name: Name of the logger to attach to
    """
    logger = logging.getLogger(logger_name)
    qt_handler = get_qt_log_handler()

    # Check if already attached
    if qt_handler not in logger.handlers:
        logger.addHandler(qt_handler)


def detach_qt_handler_from_logger(logger_name: str = "DeepSeekOCR"):
    """
    Detach Qt log handler from a logger

    Args:
        logger_name: Name of the logger to detach from
    """
    logger = logging.getLogger(logger_name)
    qt_handler = get_qt_log_handler()

    if qt_handler in logger.handlers:
        logger.removeHandler(qt_handler)
