"""Configuration management for the medical NLP system."""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment."""

    # API Settings
    API_TITLE: str = "HELIX Medical NLP Engine"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    PORT: int = int(os.getenv("PORT", "8000"))

    # Model Settings
    USE_SCISPACY: bool = os.getenv("USE_SCISPACY", "false").lower() == "true"
    SCISPACY_MODEL: str = "en_core_sci_md"
    USE_BIOBERT: bool = True

    # Summarization Model
    _model_env = os.getenv("SUMMARIZATION_MODEL", "default")
    SUMMARIZATION_MODEL: Optional[str] = None if _model_env == "default" else _model_env
    MAX_SUMMARY_LENGTH: int = 150
    MIN_SUMMARY_LENGTH: int = 50
    MAX_INPUT_LENGTH: int = 1024

    # Medical entity extraction settings
    CONFIDENCE_THRESHOLD: float = 0.5
    MIN_ENTITY_CONFIDENCE: float = 0.3

    # History/Context Settings
    MAX_HISTORY_RECORDS: int = 5
    HISTORY_TIME_WINDOW_DAYS: int = 365

    # Batch Processing
    BATCH_SIZE: int = 32
    CHUNK_SIZE: int = 500

    # Device Settings
    DEVICE: str = os.getenv("DEVICE", "cpu")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = "logs/medical_nlp.log"

    # Paths
    MODEL_CACHE_DIR: str = os.getenv("MODEL_CACHE_DIR", "./checkpoints")
    DATA_DIR: str = "./data"
    PATIENT_RECORDS_DIR: str = "./data/patient_records"

    # API Request limits
    MAX_REQUEST_SIZE_MB: int = 10
    REQUEST_TIMEOUT_SECONDS: int = 300

    # Confidence Scoring
    MIN_RISK_SCORE: float = 0.4
    CRITICAL_RISK_THRESHOLD: float = 0.8

    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        dirs = [
            self.MODEL_CACHE_DIR,
            self.DATA_DIR,
            self.PATIENT_RECORDS_DIR,
            "logs",
        ]

        for dir_path in dirs:
            try:
                os.makedirs(dir_path, exist_ok=True)
            except Exception as e:
                print(f"Warning: Could not create directory {dir_path}: {e}")


# Create settings instance
settings = Settings()
