"""Centralized configuration manager."""

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import find_dotenv, load_dotenv

from invisible_friend.exceptions import ConfigError
from invisible_friend.models import ConfigData, Person


class Config:
    """Manages the project configuration from YAML and environment variables."""

    def __init__(self, config_path: Path | None = None) -> None:
        """
        Initialize the configuration.

        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = config_path or Path("config/settings.yaml")
        self._config: ConfigData = ConfigData()
        self._load_environment()
        self._load_config()

    def _load_environment(self) -> None:
        """Load the secrets from the project's root .env file.

        Searches upward from the current directory, so the app works both from
        the root and from a subdirectory. Variables already present in the
        environment take precedence and are not overwritten. A missing .env is
        not an error: it just means the secrets must come from the environment.
        """
        env_path = find_dotenv(usecwd=True)
        if env_path:
            load_dotenv(env_path)

    def _load_config(self) -> None:
        """Load the configuration from YAML."""
        if not self.config_path.exists():
            raise ConfigError(f"Configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self._parse_config(data)
        except yaml.YAMLError as e:
            raise ConfigError(f"Error parsing YAML: {e}") from e
        except ConfigError:
            raise
        except Exception as e:
            raise ConfigError(f"Error loading configuration: {e}") from e

    def _parse_config(self, data: dict[str, Any]) -> None:
        """Parse the YAML data into ConfigData."""
        if not data:
            raise ConfigError("Empty configuration file")

        # App settings.
        app_config = data.get("app", {})
        self._config.max_attempts = self._as_int(
            app_config.get("max_attempts", 100), "app.max_attempts"
        )

        # SMTP settings.
        email_config = data.get("email", {})
        self._config.smtp_server = str(email_config.get("smtp_server", "smtp.gmail.com"))
        self._config.smtp_port = self._as_int(email_config.get("smtp_port", 465), "email.smtp_port")

        # Participants.
        participants_data = data.get("participants", [])
        if not isinstance(participants_data, list):
            raise ConfigError("'participants' must be a list of entries")
        self._config.participants = [
            self._build_person(entry, position)
            for position, entry in enumerate(participants_data, start=1)
        ]
        self._reject_duplicate_names(self._config.participants)

        # Restrictions (forbidden pairs).
        self._config.restrictions = self._parse_restrictions(
            data.get("restrictions", []), self._config.participants
        )

    @staticmethod
    def _as_int(value: Any, key: str) -> int:
        """Coerce a YAML value to int, failing at load time instead of at use time."""
        if isinstance(value, bool) or not isinstance(value, int | str):
            raise ConfigError(f"'{key}' must be a whole number, got a {type(value).__name__}")
        try:
            return int(value)
        except ValueError as e:
            raise ConfigError(f"'{key}' must be a whole number, got: {value!r}") from e

    @staticmethod
    def _build_person(entry: Any, position: int) -> Person:
        """Build a Person from a YAML entry, failing loudly on a missing name.

        The errors reference the entry's position rather than its contents: the
        entry holds an email address and these messages reach the log.
        """
        if not isinstance(entry, dict):
            raise ConfigError(f"Participant #{position} must be an entry with a 'name'")
        if "name" not in entry:
            raise ConfigError(f"Participant #{position} has no 'name'")
        return Person(name=entry["name"], email=entry.get("email", ""))

    @staticmethod
    def _reject_duplicate_names(participants: list[Person]) -> None:
        """Reject repeated names.

        Participants are identified by name, so a duplicate would silently
        overwrite the other one and drop them from the draw.
        """
        seen: set[str] = set()
        for person in participants:
            if person.name in seen:
                raise ConfigError(
                    f"Duplicate participant name: {person.name!r}. "
                    "Names identify participants, so they must be unique."
                )
            seen.add(person.name)

    @staticmethod
    def _parse_restrictions(raw: Any, participants: list[Person]) -> list[list[str]]:
        """Validate the forbidden pairs.

        A malformed pair used to be accepted and then turned into nonsense by
        `frozenset()` (a bare string became a set of its characters), leaving a
        restriction that could never match.
        """
        if not isinstance(raw, list):
            raise ConfigError("'restrictions' must be a list of pairs")

        known = {person.name for person in participants}
        restrictions: list[list[str]] = []

        for position, pair in enumerate(raw, start=1):
            if not isinstance(pair, list | tuple) or len(pair) != 2:
                raise ConfigError(
                    f"Restriction #{position} must be a pair of two participant names"
                )
            if not all(isinstance(name, str) and name for name in pair):
                raise ConfigError(
                    f"Restriction #{position} must be a pair of two participant names"
                )
            for name in pair:
                if name not in known:
                    raise ConfigError(
                        f"Restriction #{position} names {name!r}, who is not a participant"
                    )
            restrictions.append([pair[0], pair[1]])

        return restrictions

    @property
    def participants(self) -> list[Person]:
        """Return the list of participants."""
        return self._config.participants

    @property
    def restrictions(self) -> list[list[str]]:
        """Return the restrictions (forbidden pairs)."""
        return self._config.restrictions

    @property
    def max_attempts(self) -> int:
        """Return the maximum number of attempts."""
        return self._config.max_attempts

    @property
    def smtp_server(self) -> str:
        """Return the SMTP server."""
        return self._config.smtp_server

    @property
    def smtp_port(self) -> int:
        """Return the SMTP port."""
        return self._config.smtp_port

    @property
    def email_sender(self) -> str:
        """Return the sender email from the environment."""
        email = os.getenv("MAILSENDER")
        if not email:
            raise ConfigError("Environment variable MAILSENDER not set")
        return email

    @property
    def email_password(self) -> str:
        """Return the sender password from the environment."""
        password = os.getenv("PASSWORD")
        if not password:
            raise ConfigError("Environment variable PASSWORD not set")
        return password
