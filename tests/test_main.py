"""Tests for the CLI entry point.

The critical thing here is that real delivery is **opt-in**: the default run
must never touch the network.
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

import pytest

from invisible_friend.__main__ import InvisibleFriendApp, main, parse_args
from invisible_friend.utils.logger import PACKAGE_LOGGER

MINIMAL_YAML = """
participants:
  - name: "Alice"
    email: "alice@example.com"
  - name: "Bob"
    email: "bob@example.com"
  - name: "Charlie"
    email: "charlie@example.com"
"""


@pytest.fixture
def project_without_secrets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A fresh checkout: a settings.yaml but no .env and no secrets in the environment."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("MAILSENDER", raising=False)
    monkeypatch.delenv("PASSWORD", raising=False)
    path = tmp_path / "settings.yaml"
    path.write_text(MINIMAL_YAML, encoding="utf-8")
    return path


def test_a_simulated_run_needs_no_credentials(project_without_secrets: Path) -> None:
    """The default run never opens a socket, so it must not demand a .env.

    Requiring credentials for a dry run pushes people into putting real ones in
    place just to try the app.
    """
    output = project_without_secrets.parent / "out.json"

    code = main(["--config", str(project_without_secrets), "--output", str(output)])

    assert code == 0
    assert output.exists()


def test_a_real_send_without_credentials_fails(project_without_secrets: Path) -> None:
    """--send does need the secrets, and says so instead of crashing."""
    code = main(
        [
            "--send",
            "--config",
            str(project_without_secrets),
            "--output",
            str(project_without_secrets.parent / "out.json"),
        ]
    )

    assert code == 1


@pytest.fixture
def environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Fake project: its own settings.yaml and dummy secrets."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MAILSENDER", "sender@example.com")
    monkeypatch.setenv("PASSWORD", "app-password")
    path = tmp_path / "settings.yaml"
    path.write_text(MINIMAL_YAML, encoding="utf-8")
    return path


def test_default_simulates(environment: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """With no flags, the emails are simulated: simulate=True."""
    calls: list[bool] = []

    def fake_send(
        self: object,
        assignments: dict[str, str],
        emails: dict[str, str],
        simulate: bool = False,
    ) -> tuple[int, int]:
        calls.append(simulate)
        return (0, 0)

    monkeypatch.setattr(
        "invisible_friend.services.email_service.EmailService.send_assignments",
        fake_send,
    )

    app = InvisibleFriendApp(environment)
    app.run()

    assert calls == [True]


def test_send_flag_enables_delivery(environment: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """With send=True a real delivery is requested: simulate=False."""
    calls: list[bool] = []

    def fake_send(
        self: object,
        assignments: dict[str, str],
        emails: dict[str, str],
        simulate: bool = False,
    ) -> tuple[int, int]:
        calls.append(simulate)
        return (3, 0)

    monkeypatch.setattr(
        "invisible_friend.services.email_service.EmailService.send_assignments",
        fake_send,
    )

    app = InvisibleFriendApp(environment)
    app.run(send=True)

    assert calls == [False]


def test_parse_args_defaults_to_not_sending() -> None:
    """The default of --send is False: it must be requested explicitly."""
    args = parse_args([])

    assert args.send is False
    assert args.debug is False
    assert args.config == Path("config/settings.yaml")
    assert args.output == Path("output/assignments.json")


def test_debug_flag_turns_on_debug_logging(
    environment: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """--debug is what puts the assignment detail in the log file."""
    monkeypatch.setattr(
        "invisible_friend.services.email_service.EmailService.send_assignments",
        lambda self, assignments, emails, simulate=False: (0, 0),
    )

    main(["--debug", "--config", str(environment), "--output", str(environment.parent / "o.json")])

    assert logging.getLogger(PACKAGE_LOGGER).level == logging.DEBUG


def test_without_debug_the_log_stays_at_info(
    environment: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The normal run records INFO, which never names a receiver."""
    monkeypatch.setattr(
        "invisible_friend.services.email_service.EmailService.send_assignments",
        lambda self, assignments, emails, simulate=False: (0, 0),
    )

    main(["--config", str(environment), "--output", str(environment.parent / "o.json")])

    assert logging.getLogger(PACKAGE_LOGGER).level == logging.INFO


def test_running_as_a_module_still_logs_the_flow(tmp_path: Path) -> None:
    """`python -m invisible_friend` executes this file under the name "__main__".

    A logger called "__main__" is not a child of the package logger, so its
    records reach no handler and the whole flow disappears from the log. Only a
    real subprocess can catch that, since importing the module names it
    `invisible_friend.__main__` and hides the problem.
    """
    config = tmp_path / "settings.yaml"
    config.write_text(MINIMAL_YAML, encoding="utf-8")
    environment = {k: v for k, v in os.environ.items() if k not in ("MAILSENDER", "PASSWORD")}

    result = subprocess.run(  # noqa: S603 - fixed argv: this interpreter and tmp_path paths
        [
            sys.executable,
            "-m",
            "invisible_friend",
            "--config",
            str(config),
            "--output",
            str(tmp_path / "out.json"),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=environment,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    log = (tmp_path / "logs" / "invisible_friend.log").read_text(encoding="utf-8")
    assert "STARTING FULL SECRET SANTA FLOW" in log
    assert "Initializing Invisible Friend application" in log


def test_parse_args_accepts_the_flags() -> None:
    """--send, --config and --output are parsed as expected."""
    args = parse_args(["--send", "--config", "other.yaml", "--output", "out.json"])

    assert args.send is True
    assert args.config == Path("other.yaml")
    assert args.output == Path("out.json")


def test_old_spanish_flag_no_longer_exists(environment: Path) -> None:
    """The former Spanish send flag is gone: argparse rejects it."""
    with pytest.raises(SystemExit):
        parse_args(["--enviar"])


def test_main_uses_the_given_config_path(
    environment: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """--config wins: the app is built with that YAML."""
    monkeypatch.setattr(
        "invisible_friend.services.email_service.EmailService.send_assignments",
        lambda self, assignments, emails, simulate=False: (0, 0),
    )

    code = main(["--config", str(environment), "--output", str(environment.parent / "out.json")])

    assert code == 0
    assert (environment.parent / "out.json").exists()


def test_main_returns_1_when_config_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A missing YAML exits with code 1, with no raw traceback."""
    monkeypatch.chdir(tmp_path)

    assert main(["--config", str(tmp_path / "does_not_exist.yaml")]) == 1


def test_saves_the_assignments_to_the_output(
    environment: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The assignments JSON is written to the requested path."""
    monkeypatch.setattr(
        "invisible_friend.services.email_service.EmailService.send_assignments",
        lambda self, assignments, emails, simulate=False: (0, 0),
    )
    destination = environment.parent / "result.json"

    app = InvisibleFriendApp(environment)
    app.run(output_path=destination)

    assert destination.exists()
