import logging
import sys
from rich.logging import RichHandler
from rich.console import Console

# Create console for rich output
console = Console()


# Set up a default logger with DEBUG level (can be changed later)
class RichLogger(logging.Logger):
    """
    A custom logger class that extends the standard logging.Logger with Rich formatter.

    This logger uses Rich for prettier, more readable console output with support for
    syntax highlighting, tables, and other rich text formatting.

    Attributes:
        rich_handler: RichHandler instance for handling log output
    """

    def __init__(self, name: str, level: int = logging.NOTSET):
        super().__init__(name, level)
        self.rich_handler = RichHandler(console=console)
        formatter = logging.Formatter("%(message)s")
        self.rich_handler.setFormatter(formatter)
        self.addHandler(self.rich_handler)

    # Add the request failure logging method directly to the logger class
    def log_request_failure(self, status_code, path, detail, method="POST"):
        """
        Log detailed information about request failures

        Args:
            status_code (int): HTTP status code of the failed request
            path (str): API endpoint path that failed
            detail (str): Error details or message
            method (str): HTTP method used (default: POST)
        """
        error_msg = f"Request failed: {method} {path} ({status_code})"
        if status_code == 401:
            self.warning(f"{error_msg} - Authentication failed: {detail}")
        elif status_code == 400:
            self.warning(f"{error_msg} - Bad request: {detail}")
        elif status_code == 404:
            self.warning(f"{error_msg} - Not found: {detail}")
        elif status_code == 429:
            self.warning(f"{error_msg} - Rate limit exceeded: {detail}")
        elif status_code >= 500:
            self.error(f"{error_msg} - Server error: {detail}")
        else:
            self.warning(f"{error_msg} - {detail}")


# Set the custom logger class
logging.setLoggerClass(RichLogger)

# Create a logger instance with default level (INFO)
_logger = logging.getLogger("app")
_logger.setLevel(logging.INFO)  # Default to INFO initially

# Ensure our logger has the custom method
if not hasattr(_logger, "log_request_failure"):
    # If the logger doesn't have our custom method, it might not be a RichLogger instance
    # Create a new RichLogger instance manually
    _logger = RichLogger("app")
    _logger.setLevel(logging.INFO)


def get_logger():
    """
    Get the configured logger instance.

    Returns:
        Logger: The configured logger instance
    """
    return _logger


# Function to update logger level after settings are loaded
def configure_logger(log_level_name="INFO"):
    """
    Configure the logger based on the provided log level name.

    Args:
        log_level_name (str): The name of the log level (e.g., "INFO", "DEBUG")

    Returns:
        Logger: The configured logger instance
    """
    global _logger  # Access the global logger
    try:
        # Convert string level name to numeric level
        level = getattr(logging, log_level_name.upper(), logging.INFO)
        _logger.setLevel(level)
        _logger.info(f"Log level set to: {log_level_name}")
    except (AttributeError, ValueError):
        _logger.warning(f"Invalid log level: {log_level_name}. Using INFO.")
        _logger.setLevel(logging.INFO)

    return _logger


# Create the logger instance for easy import
logger = get_logger()


# Fallback implementation for any code that might try to directly access the function
def log_request_failure(status_code, path, detail, method="POST"):
    """
    Legacy/fallback function for request failure logging - delegates to the logger instance
    """
    if hasattr(logger, "log_request_failure") and callable(
        getattr(logger, "log_request_failure", None)
    ):
        return getattr(logger, "log_request_failure")(status_code, path, detail, method)
    else:
        # Fallback implementation if the logger doesn't have the method
        error_msg = f"Request failed: {method} {path} ({status_code})"
        if status_code == 401:
            logger.warning(f"{error_msg} - Authentication failed: {detail}")
        elif status_code == 400:
            logger.warning(f"{error_msg} - Bad request: {detail}")
        elif status_code == 404:
            logger.warning(f"{error_msg} - Not found: {detail}")
        elif status_code == 429:
            logger.warning(f"{error_msg} - Rate limit exceeded: {detail}")
        elif status_code >= 500:
            logger.error(f"{error_msg} - Server error: {detail}")
        else:
            logger.warning(f"{error_msg} - {detail}")
