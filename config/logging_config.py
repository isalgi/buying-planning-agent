from loguru import logger
import sys
import os
from .settings import settings

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Remove default handler
logger.remove()

# Add console handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)

# Add file handler
logger.add(
    settings.LOG_FILE,
    rotation="500 MB",
    retention="10 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=settings.LOG_LEVEL
)

def get_logger(name):
    return logger.bind(name=name)