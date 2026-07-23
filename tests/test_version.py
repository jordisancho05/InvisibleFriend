"""Test that the version has a single source of truth."""

from importlib.metadata import version

import invisible_friend


def test_version_matches_metadata() -> None:
    """__version__ comes from the package metadata, not a hand-written copy."""
    assert invisible_friend.__version__ == version("invisible-friend")


def test_version_is_not_empty() -> None:
    """The installed package reports a real version."""
    assert invisible_friend.__version__
    assert invisible_friend.__version__ != "0.0.0.dev0"
