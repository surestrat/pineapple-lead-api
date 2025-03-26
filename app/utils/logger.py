import logging
import sys
from rich.logging import RichHandler
from rich.console import Console
from app.config.settings import settings

console = Console()


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


logging.setLoggerClass(RichLogger)
logger = logging.getLogger(__name__)

# Set the log level from the environment variable
try:
    logger.setLevel(settings.log_level)
except ValueError:
    logger.setLevel(logging.INFO)  # Default to INFO if invalid log level
    logger.warning("Invalid log level specified in LOG_LEVEL. Defaulting to INFO.")
