import logging
from typing import Literal
from colorama import Fore, Style, init

# Initialize colorama (this handles Windows terminals properly)
init(autoreset=True)


class ColorFormatter(logging.Formatter):
    """Formatter that adds colors to log levels in console output.

    This formatter extends the standard logging.Formatter to add color-coding
    to log level names when outputting to the console. Different colors are
    used for different log levels to improve readability and visual distinction.

    The formatter can be configured to disable colors when needed (e.g., for
    environments where color codes might cause issues).

    Attributes:
        COLORS: Dictionary mapping log level names to colorama color codes
        use_colors: Boolean flag indicating whether to apply color formatting

    Example:
        >>> import logging
        >>> from ethicrawl.logger import ColorFormatter
        >>>
        >>> # Create a console handler with color formatting
        >>> handler = logging.StreamHandler()
        >>> formatter = ColorFormatter(
        ...     fmt="%(levelname)s: %(message)s",
        ...     use_colors=True
        ... )
        >>> handler.setFormatter(formatter)
        >>>
        >>> # Add the handler to a logger
        >>> logger = logging.getLogger("example")
        >>> logger.addHandler(handler)
        >>>
        >>> # Log messages will have colored level names
        >>> logger.warning("This warning will be yellow")
        >>> logger.error("This error will be red")
    """

    COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    def __init__(
        self,
        fmt=None,
        datefmt=None,
        style: Literal["%", "{", "$"] = "%",
        use_colors=True,
    ):
        """Initialize the color formatter.

        Args:
            fmt: Format string for log messages
            datefmt: Format string for dates
            style: Style of format string ('%', '{', or '$')
            use_colors: Whether to apply color formatting
        """
        super().__init__(fmt, datefmt, style)
        self.use_colors = use_colors

    def format(self, record):
        """Format the log record with colored level name if enabled.

        Args:
            record: LogRecord to format

        Returns:
            Formatted log message string with colored level name if enabled
        """
        # First, format the message using the parent formatter
        formatted_message = super().format(record)

        # Only add colors if requested and we have a color for this level
        if self.use_colors and record.levelname in self.COLORS:
            # Add color to the level name within the formatted message
            levelname_with_color = (
                f"{self.COLORS[record.levelname]}{record.levelname}{Style.RESET_ALL}"
            )
            formatted_message = formatted_message.replace(
                record.levelname, levelname_with_color
            )

        return formatted_message
