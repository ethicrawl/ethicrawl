import logging
from colorama import Fore, Back, Style, init

# Initialize colorama (this handles Windows terminals properly)
init(autoreset=True)


class ColorFormatter(logging.Formatter):
    """
    Formatter that adds colors to log levels when outputting to console.
    Uses standard formatting for file outputs.
    """

    COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    def __init__(self, fmt=None, datefmt=None, style="%", use_colors=True):
        super().__init__(fmt, datefmt, style)
        self.use_colors = use_colors

    def format(self, record):
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
