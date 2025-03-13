import logging
from colorama import Fore, Back, Style, init
import random

# Initialize colorama (this handles Windows terminals properly)
init(autoreset=True)


# Please don't actually use this
class GeoCitiesFormatter(logging.Formatter):
    """
    Easter egg formatter that mimics the glory days of GeoCities websites.
    WARNING: May cause eye strain, confusion, and flashbacks to the 90s.
    Use only for nostalgic purposes or to punish overly curious developers.
    """

    RANDOM_COLORS = [
        Fore.RED,
        Fore.GREEN,
        Fore.YELLOW,
        Fore.BLUE,
        Fore.MAGENTA,
        Fore.CYAN,
    ]

    BACKGROUNDS = [
        Back.BLACK,
        Back.RED,
        Back.GREEN,
        Back.YELLOW,
        Back.BLUE,
        Back.MAGENTA,
        Back.CYAN,
    ]

    DIVIDERS = [
        "~*~*~*~*~*~*~*~*~",
        "·°·°·°·°·°·°·°·°·",
        "¯\\_(ツ)_/¯",
        "★★★★★★★★★",
        "▁▂▃▄▅▆▇█▇▆▅▄▃▂▁",
        "⋆｡°✩☆✮★⋆｡°✩",
    ]

    def __init__(self, fmt=None, datefmt=None):
        if fmt is None:
            fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        super().__init__(fmt, datefmt)

    def format(self, record):
        # First get the original formatted message
        msg = super().format(record)

        # Add level-specific formatting
        if record.levelname == "DEBUG":
            return f"{random.choice(self.RANDOM_COLORS)}{msg}{Style.RESET_ALL}"

        elif record.levelname == "INFO":
            divider = random.choice(self.DIVIDERS)
            return f"{Fore.CYAN}{divider}{Style.RESET_ALL} {Fore.GREEN} {msg} {Style.RESET_ALL} {Fore.CYAN}{divider}{Style.RESET_ALL}"

        elif record.levelname == "WARNING":
            parts = []
            for i, char in enumerate(msg):
                if i % 2 == 0:
                    parts.append(f"{Fore.YELLOW}{char}")
                else:
                    parts.append(f"{Fore.WHITE}{char}")
            return "".join(parts) + Style.RESET_ALL

        elif record.levelname == "ERROR":
            bg = random.choice(self.BACKGROUNDS)
            return f"{bg}{Fore.WHITE}{Style.BRIGHT}!!! {msg} !!!{Style.RESET_ALL}"

        elif record.levelname == "CRITICAL":
            # The famous blinking effect (simulated with text markers)
            return f"{Fore.MAGENTA}{Style.BRIGHT}*BLINK* {msg} *BLINK*{Style.RESET_ALL}"

        # Default case
        return msg


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
