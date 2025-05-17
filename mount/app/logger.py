import logging
import sys
from typing import Optional

# Logger configuration
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
LOG_LEVEL = logging.INFO  # Adjust as needed
LOG_FILE: Optional[str] = "app.log"  # e.g., "app.log" to enable file logging

logger = logging.getLogger("school_logger")
logger.setLevel(LOG_LEVEL)

# Disable uvicorn logger
uvicorn_access = logging.getLogger("uvicorn.access")
uvicorn_access.disabled = True

if not logger.handlers:
    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if LOG_FILE:
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

# Logging convenience functions
def debug(msg: str):
    """Log a debug level message."""
    logger.debug(msg)

def info(msg: str):
    """Log an info level message."""
    logger.info(msg)

def warning(msg: str):
    """Log a warning level message."""
    logger.warning(msg)

def error(msg: str):
    """Log an error level message."""
    logger.error(msg)

def critical(msg: str):
    """Log a critical level message."""
    logger.critical(msg)

def exception(msg: str, exc: Optional[Exception] = None):
    """
    Log an exception with traceback.

    Args:
        msg (str): Custom message to log with the exception.
        exc (Exception, optional): The exception instance (if available). If not provided, logs the current exception.
    """
    if exc:
        logger.error(f"{msg}: {str(exc)}", exc_info=exc)
    else:
        logger.error(msg, exc_info=True)
