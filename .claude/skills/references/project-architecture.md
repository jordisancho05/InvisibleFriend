# InvisibleFriend — Architecture

> Detailed architecture. Day-to-day rules live in `CLAUDE.md` (repo root).

CLI app in Python. Reads the participants and the forbidden pairs from a YAML file, generates a valid
Secret Santa (Amigo Invisible) assignment as a single cycle, prints it, saves it to JSON and emails
each participant their assigned person over Gmail SMTP. Sending is **opt-in**: the default run
simulates.

## Package map (`src/invisible_friend/`)
- `__init__.py` — exposes `__version__`, read from the installed metadata via `importlib.metadata`
  so the version lives only in `pyproject.toml`.
- `config.py` — `Config` class. Loads the root `.env` via `find_dotenv(usecwd=True)` (searches
  upward from the CWD; existing env vars win and are never overwritten; a missing `.env` is not an
  error), then parses the YAML into a `ConfigData`. Exposes `participants`, `restrictions`,
  `max_attempts`, `smtp_server`, `smtp_port` as properties, plus `email_sender` / `email_password`
  read from env (`MAILSENDER` / `PASSWORD`) and raising `ConfigError` when missing. A missing or
  invalid YAML — or a participant entry without a `name` — raises `ConfigError`.
- `models.py` — `Person` (dataclass; validates non-empty name and a mandatory well-formed email in
  `__post_init__`, hashed/compared **by name only**), `Assignment` (`giver`/`receiver`, rejects
  self-assignment) and `ConfigData` (config container with defaults).
- `exceptions.py` — `InvisibleFriendError` base + `ConfigError`, `EmailError`, `ValidationError`,
  `AssignmentError`. Every failure raised by the package derives from the base.
- `validators.py` — `PairValidator`. Holds restrictions as a `set[frozenset[str]]` so lookups are
  **bidirectional** (`A-B` == `B-A`). `is_valid_pair()` (false for the same person or a forbidden
  pair), `validate_cycle()` (checks every `i → i+1` edge, wrapping around; raises `ValidationError`
  on an empty list), plus add/remove/list restrictions.
- `services/secret_santa.py` — `SecretSantaService`. `generate_assignments()` shuffles the list and
  builds the cycle `person[i] → person[(i+1) % n]`, retrying up to `max_attempts` until
  `validate_cycle()` passes; raises `AssignmentError` with <2 people or when attempts run out. The
  cycle guarantees everyone gives once and receives once. Also
  `get_formatted_assignments()` (`Person` dict → name dict) and `print_assignments()`.
- `services/email_service.py` — `EmailService`. `create_email()` builds the `EmailMessage`,
  `send_email()` sends it over `smtplib.SMTP_SSL` with an `ssl.create_default_context()`,
  `send_assignment()` renders the template, and `send_assignments()` loops over the
  assignments returning `(successful, failed)`. **`simulate=True` skips the network entirely.** A
  participant without an email is logged as a warning and counted as failed, not raised.
- `templates/email_template.py` — `EmailTemplate`: `SUBJECT` plus `render_body()` (plain text) and
  `render_html()`. All the copy is **Spanish** and user-facing (the only Spanish left in the code).
- `utils/logger.py` — `get_logger()`; process-wide singleton logger with a UTF-8 console handler
  (INFO) and a UTF-8 file handler (DEBUG) writing to `logs/invisible_friend.log`. Creates `logs/`
  on import.
- `utils/file_handler.py` — `FileHandler`: static `save_json()` / `load_json()` (UTF-8,
  `ensure_ascii=False`, creates parent dirs) and `save_assignments()`, which wraps the mapping
  as `{"assignments": ..., "total_participants": n}`. Failures become `InvisibleFriendError`.

## Entry point (`__main__.py`)
- `InvisibleFriendApp` wires `Config` → `PairValidator` → `SecretSantaService` → `EmailService` in
  `__init__`; `run(send=False, output_path=...)` runs the 4 steps: generate → print →
  save to `output/assignments.json` → send (**simulated unless `send=True`**).
- `parse_args()` defines `--send` (default `False`), `--config` (default `config/settings.yaml`),
  `--output` (default `output/assignments.json`) and `--version`.
- `main(argv=None)` returns `0`, or `1` after logging a controlled failure — it never lets a
  traceback reach the user.
- Three equivalent invocations: `python main.py` (thin launcher at the repo root),
  `python -m invisible_friend`, and the `invisible-friend` console script declared in
  `[project.scripts]`.

## Layering
`config` (YAML + env) → `models` + `validators` (pure domain, no I/O) → `services/secret_santa`
(assignment) → `templates` + `services/email_service` (delivery) → `__main__` (orchestration + CLI).
`utils/` (logger, file_handler) is cross-cutting and may be used from any layer. Dependencies point
**downward only**: nothing under `models`/`validators` imports a service, and no service imports
`__main__`.

## Invariants that must not regress
- The assignment is a **single cycle**, never fixed points or sub-cycles: `n` people → `n` edges,
  everyone gives once and receives once.
- Restrictions are **symmetric** (`frozenset`) — don't replace them with ordered pairs.
- Sending emails is **opt-in**: any new caller defaults to `simulate=True` / `send=False`.
- Participant names and emails are **personal data**: they live in `config/settings.yaml` and the
  generated `output/` and `logs/`, all gitignored. They never go into code, tests, docs or fixtures.

## Stack and versioning
See `CLAUDE.md` (root) and `.github/copilot-instructions.md` (Stack section = canonical dependency
versions). Version follows SemVer, single-sourced in `pyproject.toml` and tracked in `CHANGELOG.md`.
