# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-07-24

Security and robustness pass over the whole codebase. Nothing in the public API breaks.

### Added
- **`--debug` flag.** The draw (`Assignment: Alice -> Bob`) is now logged at DEBUG only, so a normal
  run never writes who was drawn for whom into `logs/invisible_friend.log`. Pass `--debug` to record
  it when you actually want to review a past draw.
- The log file **rotates** (`RotatingFileHandler`) instead of growing without bound.
- `configure_logging(debug=False)` in `utils/logger.py`, called first thing by `main()`.
- Config validation at load time, all raising `ConfigError`: duplicate participant names, malformed
  restriction pairs, restrictions naming someone who is not a participant, and non-numeric
  `max_attempts` / `smtp_port`.
- Ruff rulesets `S` (bandit), `G` (logging format), `RET` and `C4`; mypy `disallow_any_generics` and
  `strict_equality`.

### Changed
- **A simulated run no longer needs credentials.** `MAILSENDER` / `PASSWORD` are read only on the
  `--send` path, so `python main.py` works on a fresh clone with no `.env`.
- **One SMTP session for the whole batch.** `login()` used to run once per recipient, which gets the
  sender's account flagged partway through a delivery.
- The delivery log names only the recipient (`Email sent to Alice`), never their receiver.
- The draw is shuffled with `random.SystemRandom` instead of the default Mersenne Twister.
- `Person` validates emails against a regex and rejects addresses containing a line break (an SMTP
  header-injection attempt) at construction time rather than at send time.
- `Person` is now `@dataclass(eq=False)`, making the hand-written name-based `__eq__` / `__hash__`
  explicit instead of relying on dataclass not overwriting them.
- `render_body()` no longer leaks the source file's indentation into the message participants read.
- Config errors reference a participant's **position** instead of dumping the YAML entry, which
  contained their email address.
- Logging calls use lazy `%s` formatting throughout.

### Fixed
- **Duplicate participant names silently dropped someone from the draw.** Identity is the name, so a
  repeated name overwrote the earlier entry: four participants produced three assignments, with no
  error. Now rejected at config load.
- **`get_logger()` ignored its argument.** A process-wide singleton cached the first logger and
  returned it to every caller, so every module's records were attributed to whichever module happened
  to log first. Each module now gets its own logger.
- **A malformed restriction was silently ignored.** A bare string became a `frozenset` of its
  characters, so the rule never matched anyone.
- Importing the package no longer creates `logs/` as a side effect.

### Removed
- `EmailTemplate.render_html()` — dead code, wired into no send path.
- The `use_template` parameter of `send_assignment()` and its plain-text fallback body — the template
  is the only path.
- The double-wrapping of `EmailError` in `send_assignment()`, which logged every failure twice.

### Also in this release (work landed since 1.0.0)

#### Added
- **CI**: `.github/workflows/ci.yml` runs on every pull request to `master` (and on push to `master`):
  a lint/type-check job (`ruff check`, `ruff format --check`, `mypy src`) plus a test job across
  Python 3.11/3.12/3.13 (`pytest` with coverage). No secrets needed — the suite mocks SMTP and uses
  temp config.
- **Command-line interface**: `--send` (send for real; the default still only simulates),
  `--config PATH`, `--output PATH` and `--version`. Three equivalent entry points:
  `python main.py`, `python -m invisible_friend` and the `invisible-friend` console script.
- `src/invisible_friend/__main__.py` hosting `InvisibleFriendApp`, `parse_args()` and `main()`;
  the root `main.py` is now a thin launcher.
- `__version__` exposed from `invisible_friend`, read from the installed metadata so the version
  lives only in `pyproject.toml`.
- Test coverage for the four previously untested modules — `config.py`, `models.py`,
  `utils/file_handler.py` and `templates/email_template.py` — plus `tests/conftest.py` with the
  shared fixtures and `tests/test_main.py` pinning that the default run never sends email.
  The suite goes from 23 to 75 tests, ~97% coverage.
- `scripts/demo.py` (the former root-level `examples.py`).

#### Changed
- **Codebase translated to English.** Every identifier, docstring, comment, log message and console
  string is now English (`Persona`→`Person`, `ParejaValidator`→`PairValidator`,
  `generar_asignaciones`→`generate_assignments`, `ejecutar_completo`→`run`, `nombre`→`name`, …).
  **Spanish is kept only in the copy the participants receive** — the email subject and bodies in
  `templates/email_template.py` and the plain-text fallback in `email_service.py`. Breaking for
  anyone using the API or the config:
  - CLI flag `--enviar` → `--send`.
  - YAML keys `personas`/`nombre`/`restricciones` → `participants`/`name`/`restrictions`
    (`config/settings.yaml` must be migrated; the example file already is).
  - Default output file `output/asignaciones.json` → `output/assignments.json`; the saved JSON keys
    `asignaciones`/`total_personas` → `assignments`/`total_participants`.
- **Best-practice fixes folded in**: generic type parameters completed (`set[frozenset[str]]`,
  `list[Person]`, `dict[str, str]`), and a participant entry without a `name` now raises `ConfigError`
  instead of a raw `KeyError`.
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

#### Fixed
- `.gitignore` no longer swallows the `scripts/` directory: the virtualenv pattern block contained
  `[Ss]cripts`, which matched any folder named `scripts` at any depth. `.claude/` and `.github/`
  are versioned now, and the stale `config/.env` and `invisiblefriend/` entries are gone.
- Removed a leaked API-token fixture from `.claude/skills/pr-review/evals/evals.json`.

#### Removed
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

[Unreleased]: https://github.com/jordisancho05/InvisibleFriend/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/jordisancho05/InvisibleFriend/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/jordisancho05/InvisibleFriend/releases/tag/v1.0.0
