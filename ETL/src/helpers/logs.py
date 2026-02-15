import sys
import logging

class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors"""

    grey = "\x1b[38;5;244m" 
    blue = "\x1b[34m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    bold_red = "\x1b[31;1m"
    green = "\x1b[32m"
    reset = "\x1b[0m"
    
    format_str = "%(asctime)s | %(levelname)-8s | %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: blue + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)

def init_logger() -> None:
    logger = logging.getLogger("gps-logger")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        c_handler = logging.StreamHandler(sys.stdout)
        c_handler.setFormatter(CustomFormatter())
        logger.addHandler(c_handler)
    
    logger.propagate = False

def die(msg: str) -> None:
    logging.getLogger("gps-logger").error(f"FATAL: {msg}")
    sys.exit(1)

def info(msg: str) -> None:
    logging.getLogger("gps-logger").info(msg)

def done(msg: str) -> None:
    logging.getLogger("gps-logger").info(f"SUCCESS: {msg}")
    sys.exit(0)