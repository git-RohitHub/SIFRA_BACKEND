import logging
from logging.handlers import RotatingFileHandler

def get_logger(name, filepath, level=logging.INFO):
    logger = logging.getLogger(name)  # Create a logger with a unique name.
    logger.setLevel(level)

    # Check if the logger already has handlers to avoid duplicates.
    if not logger.handlers:
        handler = RotatingFileHandler(filepath, mode='w', backupCount=0)
        formatter = logging.Formatter(
            "[%(asctime)s.%(msecs)03d] %(levelname)s [%(thread)d] - %(message)s", 
            "%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
