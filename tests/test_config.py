"""Tests for configuration loading (YAML + environment variables)."""

from pathlib import Path

import pytest

from invisible_friend.config import Config
from invisible_friend.exceptions import ConfigError

MINIMAL_YAML = """
app:
  max_attempts: 50

email:
  smtp_server: "smtp.example.com"
  smtp_port: 587

participants:
  - name: "Alice"
    email: "alice@example.com"
  - name: "Bob"
    email: "bob@example.com"

restrictions:
  - ["Alice", "Bob"]
"""


@pytest.fixture
def yaml_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A temp settings.yaml with the CWD isolated from the repo's real .env."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("MAILSENDER", raising=False)
    monkeypatch.delenv("PASSWORD", raising=False)
    path = tmp_path / "settings.yaml"
    path.write_text(MINIMAL_YAML, encoding="utf-8")
    return path


def test_loads_env_from_the_root(yaml_path: Path, tmp_path: Path) -> None:
    """Finds the .env at the project root."""
    (tmp_path / ".env").write_text("MAILSENDER=root@example.com\n", encoding="utf-8")

    config = Config(yaml_path)

    assert config.email_sender == "root@example.com"


def test_ignores_an_env_inside_config(yaml_path: Path, tmp_path: Path) -> None:
    """The .env lives only at the root: a leftover config/.env is not loaded."""
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / ".env").write_text("MAILSENDER=old@example.com\n", encoding="utf-8")

    config = Config(yaml_path)

    with pytest.raises(ConfigError, match="MAILSENDER"):
        _ = config.email_sender


def test_no_env_does_not_fail(yaml_path: Path) -> None:
    """A missing .env does not break loading: only the secret is absent."""
    config = Config(yaml_path)

    assert len(config.participants) == 2
    with pytest.raises(ConfigError):
        _ = config.email_sender


def test_parses_participants_and_restrictions(yaml_path: Path) -> None:
    """Reads the participant list and the forbidden pairs from the YAML."""
    config = Config(yaml_path)

    assert [p.name for p in config.participants] == ["Alice", "Bob"]
    assert config.restrictions == [["Alice", "Bob"]]


def test_reads_app_and_email_values(yaml_path: Path) -> None:
    """Takes max_attempts and the SMTP data from the YAML."""
    config = Config(yaml_path)

    assert config.max_attempts == 50
    assert config.smtp_server == "smtp.example.com"
    assert config.smtp_port == 587


def test_applies_defaults_when_sections_are_missing(yaml_path: Path, tmp_path: Path) -> None:
    """A YAML without app/email uses the default values."""
    path = tmp_path / "settings.yaml"
    path.write_text('participants:\n  - name: "Alice"\n    email: "alice@example.com"\n', "utf-8")

    config = Config(path)

    assert config.max_attempts == 100
    assert config.smtp_server == "smtp.gmail.com"
    assert config.smtp_port == 465


def test_participant_without_name_raises_config_error(yaml_path: Path) -> None:
    """A participant entry with no 'name' fails loudly, not with a raw KeyError."""
    yaml_path.write_text('participants:\n  - email: "alice@example.com"\n', encoding="utf-8")

    with pytest.raises(ConfigError, match="name"):
        Config(yaml_path)


def test_missing_file_raises_config_error(yaml_path: Path, tmp_path: Path) -> None:
    """A settings.yaml that does not exist fails explicitly."""
    with pytest.raises(ConfigError, match="not found"):
        Config(tmp_path / "does_not_exist.yaml")


def test_malformed_yaml_raises_config_error(yaml_path: Path) -> None:
    """A syntactically invalid YAML is translated into ConfigError."""
    yaml_path.write_text("participants: [\n  - broken", encoding="utf-8")

    with pytest.raises(ConfigError):
        Config(yaml_path)


def test_empty_yaml_raises_config_error(yaml_path: Path) -> None:
    """An empty configuration file is not usable."""
    yaml_path.write_text("", encoding="utf-8")

    with pytest.raises(ConfigError, match="[Ee]mpty"):
        Config(yaml_path)


def test_secrets_from_the_environment(yaml_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MAILSENDER and PASSWORD are read from the environment."""
    monkeypatch.setenv("MAILSENDER", "sender@example.com")
    monkeypatch.setenv("PASSWORD", "app-password")

    config = Config(yaml_path)

    assert config.email_sender == "sender@example.com"
    assert config.email_password == "app-password"


@pytest.mark.parametrize("variable", ["MAILSENDER", "PASSWORD"])
def test_missing_secret_raises_config_error(yaml_path: Path, variable: str) -> None:
    """A secret that is not set fails loudly, not silently."""
    config = Config(yaml_path)

    with pytest.raises(ConfigError, match=variable):
        _ = config.email_sender if variable == "MAILSENDER" else config.email_password
