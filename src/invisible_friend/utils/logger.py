"""Centralized project logger."""

import logging
import sys
from pathlib import Path


class LoggerConfig:
    """Configures the project logging."""

    _logger: logging.Logger | None = None

    @classmethod
    def get_logger(cls, name: str = "invisible_friend") -> logging.Logger:
        """
        Get or create the main logger.

        Args:
            name: Logger name

        Returns:
            Configured logger
        """
        if cls._logger is None:
            cls._logger = cls._configure_logger(name)
        return cls._logger

    @staticmethod
    def _configure_logger(name: str) -> logging.Logger:
        """Configure the logger with its handlers and formatter."""
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Avoid duplicate handlers.
        if logger.handlers:
            return logger

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console handler (UTF-8 on Windows).
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        # Force UTF-8 on Windows.
        if hasattr(console_handler.stream, "reconfigure"):
            console_handler.stream.reconfigure(encoding="utf-8", errors="replace")
        logger.addHandler(console_handler)

        # File handler (UTF-8).
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "invisible_friend.log", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger


# Global helper used across the application.
def get_logger(name: str = "invisible_friend") -> logging.Logger:
    """Return the configured logger."""
    return LoggerConfig.get_logger(name)
