import logging
import colorlog

def setup_logging():
    """
    Sets up the logging with colored output using colorlog.
    Removes all existing handlers and adds a new one to ensure
    only the desired handler is active.
    """
    logger = logging.getLogger()
    
    # Remove all existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    handler = logging.StreamHandler()
    
    # Define a format for the log messages
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s%(log_color)s:%(reset)s     %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    )
    
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
