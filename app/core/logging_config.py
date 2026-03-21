"""Logging configuration for the medical NLP system."""

import logging
import logging.handlers
import os
from app.core.config import settings

# Ensure logs directory exists
os.makedirs("./logs", exist_ok=True)


def setup_logging() -> logging.Logger:
    """Configure logging for the application."""
    logger = logging.getLogger("helix_medical_nlp")
    logger.setLevel(settings.LOG_LEVEL)

    # File handler
    fh = logging.handlers.RotatingFileHandler(
        "./logs/helix_medical_nlp.log",
        maxBytes=10485760,  # 10MB
        backupCount=5,
    )
    fh.setLevel(settings.LOG_LEVEL)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(settings.LOG_LEVEL)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


logger = setup_logging()
