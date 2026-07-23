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
        self._config.max_attempts = app_config.get("max_attempts", 100)

        # SMTP settings.
        email_config = data.get("email", {})
        self._config.smtp_server = email_config.get("smtp_server", "smtp.gmail.com")
        self._config.smtp_port = email_config.get("smtp_port", 465)

        # Participants.
        participants_data = data.get("participants", [])
        self._config.participants = [self._build_person(entry) for entry in participants_data]

        # Restrictions (forbidden pairs).
        self._config.restrictions = data.get("restrictions", [])

    @staticmethod
    def _build_person(entry: dict[str, Any]) -> Person:
        """Build a Person from a YAML entry, failing loudly on a missing name."""
        if "name" not in entry:
            raise ConfigError(f"Participant entry without a 'name': {entry}")
        return Person(name=entry["name"], email=entry.get("email", ""))

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
