"""Tests for the logging setup.

The logger is what decides whether the draw ends up on disk, so its level and
its handlers are pinned here rather than left to chance.
"""

import importlib
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import pytest

from invisible_friend.utils import logger as logger_module
from invisible_friend.utils.logger import PACKAGE_LOGGER, configure_logging, get_logger


def _package_handlers() -> list[logging.Handler]:
    """The real handlers attached to the package logger (the NullHandler aside)."""
    return [
        handler
        for handler in logging.getLogger(PACKAGE_LOGGER).handlers
        if not isinstance(handler, logging.NullHandler)
    ]


def test_get_logger_returns_a_logger_per_name() -> None:
    """Each module gets its own logger: no singleton mislabelling the origin."""
    one = get_logger("invisible_friend.one")
    other = get_logger("invisible_friend.two")

    assert one is not other
    assert one.name == "invisible_friend.one"
    assert other.name == "invisible_friend.two"


def test_configure_logging_does_not_duplicate_handlers(tmp_path: Path) -> None:
    """Calling it twice keeps one set of handlers, not two."""
    configure_logging(log_dir=tmp_path)
    after_first = len(_package_handlers())
    configure_logging(log_dir=tmp_path)

    assert after_first > 0
    assert len(_package_handlers()) == after_first


def test_debug_flag_sets_the_debug_level(tmp_path: Path) -> None:
    """--debug lowers the package logger and every handler to DEBUG."""
    configure_logging(debug=True, log_dir=tmp_path)

    assert logging.getLogger(PACKAGE_LOGGER).level == logging.DEBUG
    assert all(handler.level == logging.DEBUG for handler in _package_handlers())


def test_without_debug_the_level_is_info(tmp_path: Path) -> None:
    """The normal run never records DEBUG, which is where the draw lives."""
    configure_logging(log_dir=tmp_path)

    assert logging.getLogger(PACKAGE_LOGGER).level == logging.INFO
    assert all(handler.level == logging.INFO for handler in _package_handlers())


def test_reconfiguring_updates_the_level(tmp_path: Path) -> None:
    """A second call with debug=True upgrades the handlers already attached."""
    configure_logging(log_dir=tmp_path)
    configure_logging(debug=True, log_dir=tmp_path)

    assert all(handler.level == logging.DEBUG for handler in _package_handlers())


def test_the_log_file_rotates(tmp_path: Path) -> None:
    """The log is bounded: it cannot grow forever holding old draws."""
    configure_logging(log_dir=tmp_path)

    rotating = [h for h in _package_handlers() if isinstance(h, RotatingFileHandler)]

    assert rotating, "the log file handler must rotate"
    assert rotating[0].maxBytes > 0
    assert rotating[0].backupCount > 0


def test_importing_the_module_creates_no_log_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Importing the package has no side effects on the filesystem."""
    monkeypatch.chdir(tmp_path)

    importlib.reload(logger_module)

    assert not (tmp_path / "logs").exists()
