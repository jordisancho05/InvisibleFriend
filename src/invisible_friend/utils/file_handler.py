"""File handler for saving and loading data."""

import json
from pathlib import Path
from typing import Any

from invisible_friend.exceptions import InvisibleFriendError
from invisible_friend.utils.logger import get_logger

logger = get_logger(__name__)


class FileHandler:
    """Handles reading and writing data to files."""

    @staticmethod
    def save_json(path: Path, data: dict[str, Any]) -> None:
        """
        Save data as JSON.

        Args:
            path: File path
            data: Data to save

        Raises:
            InvisibleFriendError: If saving fails
        """
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {path}")
        except Exception as e:
            logger.error(f"Error saving file {path}: {e}")
            raise InvisibleFriendError(f"Error saving JSON: {e}") from e

    @staticmethod
    def load_json(path: Path) -> dict[str, Any]:
        """
        Load data from JSON.

        Args:
            path: File path

        Returns:
            Loaded data

        Raises:
            InvisibleFriendError: If loading fails
        """
        try:
            if not path.exists():
                raise InvisibleFriendError(f"File not found: {path}")

            with open(path, encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)
            logger.info(f"Data loaded from {path}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON {path}: {e}")
            raise InvisibleFriendError(f"Error loading JSON: {e}") from e
        except Exception as e:
            logger.error(f"Error loading file {path}: {e}")
            raise InvisibleFriendError(f"Error loading file: {e}") from e

    @staticmethod
    def save_assignments(path: Path, assignments: dict[str, str]) -> None:
        """
        Save assignments as human-readable JSON.

        Args:
            path: File path
            assignments: Assignments dict {giver: receiver}
        """
        data = {"assignments": assignments, "total_participants": len(assignments)}
        FileHandler.save_json(path, data)
