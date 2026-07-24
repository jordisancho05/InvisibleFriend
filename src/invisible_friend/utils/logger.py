"""Centralized project logger.

`get_logger()` returns the standard per-module logger; the handlers live on the
package logger and are attached once by `configure_logging()`, which the CLI
calls before anything else. Nothing is configured at import time, so importing
the package neither creates `logs/` nor writes a line.

The level is the privacy switch: the assignment detail is logged at DEBUG, so a
normal run (INFO) never records who was drawn for whom. Only `--debug` does.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

PACKAGE_LOGGER = "invisible_friend"
DEFAULT_LOG_DIR = Path("logs")
LOG_FILENAME = "invisible_friend.log"
MAX_BYTES = 1_000_000
BACKUP_COUNT = 3

# Keep the package quiet until the CLI configures it: a library import must not
# emit "no handlers could be found" nor claim stdout.
logging.getLogger(PACKAGE_LOGGER).addHandler(logging.NullHandler())


def get_logger(name: str = PACKAGE_LOGGER) -> logging.Logger:
    """
    Return the logger for `name`.

    Args:
        name: Logger name, normally the caller's `__name__`

    Returns:
        The logger for that name; records propagate to the package logger,
        which owns the handlers
    """
    return logging.getLogger(name)


def configure_logging(debug: bool = False, log_dir: Path = DEFAULT_LOG_DIR) -> None:
    """
    Attach the console and rotating-file handlers to the package logger.

    Idempotent: calling it again updates the level instead of stacking a second
    set of handlers.

    Args:
        debug: If True, record DEBUG (includes the assignment detail);
            otherwise INFO, which never names a receiver
        log_dir: Directory for the log file, created if missing
    """
    level = logging.DEBUG if debug else logging.INFO
    logger = logging.getLogger(PACKAGE_LOGGER)
    logger.setLevel(level)

    configured = [h for h in logger.handlers if not isinstance(h, logging.NullHandler)]
    if configured:
        for handler in configured:
            handler.setLevel(level)
        return

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    # Force UTF-8 on Windows: the console output carries emoji.
    if hasattr(console_handler.stream, "reconfigure"):
        console_handler.stream.reconfigure(encoding="utf-8", errors="replace")
    logger.addHandler(console_handler)

    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        log_dir / LOG_FILENAME,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
