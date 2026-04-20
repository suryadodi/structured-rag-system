import logging
from logging.handlers import RotatingFileHandler
import os

if not os.path.exists("logs"):
    os.makedirs("logs")

def get_logger(name:str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

#Driver -1 Terminal Handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

#Driver 2 Rotating File Handling
        file_handler = RotatingFileHandler("logs/app.log",maxBytes=5000000,backupCount=5)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

    return logger
    
     