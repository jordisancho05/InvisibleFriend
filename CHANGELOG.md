# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Command-line interface**: `--enviar` (send for real; the default still only simulates),
  `--config PATH`, `--output PATH` and `--version`. Three equivalent entry points:
  `python main.py`, `python -m invisible_friend` and the `invisible-friend` console script.
- `src/invisible_friend/__main__.py` hosting `InvisibleFriendApp`, `parse_args()` and `main()`;
  the root `main.py` is now a thin launcher.
- `__version__` exposed from `invisible_friend`, read from the installed metadata so the version
  lives only in `pyproject.toml`.
- Test coverage for the four previously untested modules — `config.py`, `models.py`,
  `utils/file_handler.py` and `templates/email_template.py` — plus `tests/conftest.py` with the
  shared fixtures and `tests/test_main.py` pinning that the default run never sends email.
  The suite goes from 23 to 73 tests, 97% coverage.
- `scripts/demo.py` (the former root-level `examples.py`).

### Changed
- **Configuration layout**: secrets moved from `config/.env` to `.env` at the repository root
  (with `.env.example` alongside it); `config/` now holds only `settings.yaml` and its example.
  `Config` locates the file with `find_dotenv(usecwd=True)` instead of probing two hardcoded
  paths, so the app also works when launched from a subdirectory.
- **Toolchain unified on ruff + mypy**, replacing black + flake8 + isort + pylint. The whole
  codebase was reformatted by `ruff format`. Minimum Python raised to **3.11** (was 3.9).
- Test suite migrated from `unittest.TestCase` classes to idiomatic pytest (fixtures,
  `parametrize`, `tmp_path`, `monkeypatch`). The assignment tests now assert the real domain
  invariants — single cycle, no fixed points, no forbidden pair, everyone gives and receives once —
  over many runs, instead of a single weaker check.
- Exceptions raised inside an `except` block are chained with `raise ... from e`, so the original
  error is no longer lost in the traceback.
- Agent documentation (`CLAUDE.md`, `.github/copilot-instructions.md`, `.claude/skills/`) rewritten
  for this project; it had been copied from another repository and described a different app.

### Fixed
- `.gitignore` no longer swallows the `scripts/` directory: the virtualenv pattern block contained
  `[Ss]cripts`, which matched any folder named `scripts` at any depth. `.claude/` and `.github/`
  are versioned now, and the stale `config/.env` and `invisiblefriend/` entries are gone.
- Removed a leaked API-token fixture from `.claude/skills/pr-review/evals/evals.json`.

### Removed
- The legacy `invisiblefriend.py` script, a pre-package monolith carrying real participant names
  and emails hardcoded in the source.
- black, flake8, pylint and ipython from the `dev` extra.

## [1.0.0] - 2026-07-16

First stable release.

### Added
- `src/`-layout package `invisible_friend` with a layered design: `config` → `models` /
  `validators` → `services/secret_santa` → `templates` / `services/email_service`.
- Cyclic assignment algorithm: shuffle and build `persona[i] → persona[(i+1) % n]`, retrying up to
  `max_attempts` until no forbidden pair is violated. Guarantees that everyone gives exactly once
  and receives exactly once.
- Configurable forbidden pairs, stored as symmetric `frozenset`s so `A-B` and `B-A` are the same
  restriction.
- Email delivery over Gmail SMTP (`SMTP_SSL`, port 465) with a Spanish template in plain text and
  HTML, plus a simulation mode that reports what *would* be sent without opening a connection.
- YAML configuration (`config/settings.yaml`) for participants, restrictions and SMTP settings,
  with the credentials read from environment variables.
- Project exception hierarchy rooted at `InvisibleFriendError`, centralized UTF-8 logging to the
  console and `logs/`, and JSON persistence of the assignments to `output/`.
- pytest suite covering the validators, the assignment service and the email service.
- `pyproject.toml` with the runtime dependencies, a `dev` extra and SemVer versioning.

[Unreleased]: https://github.com/jordisancho05/InvisibleFriend/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/jordisancho05/InvisibleFriend/releases/tag/v1.0.0
