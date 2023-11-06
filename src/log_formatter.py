import logging
from colorama import Fore, Style, init

init()

class CustomFormatter(logging.Formatter):
    """Logging Formatter to add emoji based on log levels and custom color support"""

    EMOJI_MAP = {
        logging.DEBUG: "🐛",
        logging.INFO: "ℹ️",
        logging.WARNING: "⚠️",
        logging.ERROR: "❗",
        logging.CRITICAL: "🔥",
    }

    COLOR_MAP = {
        logging.DEBUG: Fore.LIGHTBLACK_EX,
        logging.INFO: Fore.WHITE,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.LIGHTRED_EX,
    }
    
    def __init__(self, default_color=Fore.CYAN):
        self.default_color = default_color

    def format(self, record):
        emoji = self.EMOJI_MAP.get(record.levelno, "❓")
        color = self.COLOR_MAP.get(record.levelno, self.default_color)
        
        return f"{emoji} {color}{record.msg}{Style.RESET_ALL}"