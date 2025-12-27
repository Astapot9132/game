import logging

from colorama import Style, Fore


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.INFO: Style.NORMAL + Fore.WHITE,
        logging.WARNING: Style.BRIGHT + Fore.CYAN,
        logging.ERROR: Style.BRIGHT + Fore.MAGENTA,
        logging.CRITICAL: Style.BRIGHT + Fore.RED,
        logging.DEBUG: Style.DIM + Fore.WHITE,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, Style.NORMAL)
        message = super().format(record)
        return f"{color}{message}{Style.RESET_ALL}"


def create_logger():
    
    formatter = ColorFormatter('%(asctime)s - %(levelname)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    game_logger = logging.getLogger("battle_cards")
    game_logger.handlers.clear()
    game_logger.addHandler(handler)
    
    return game_logger
    
GLOG = create_logger()

    