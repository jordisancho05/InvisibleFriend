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
  error), then parses the YAML into a `ConfigData`. Exposes `personas`, `restricciones`,
  `max_intentos`, `smtp_server`, `smtp_port` as properties, plus `email_sender` / `email_password`
  read from env (`MAILSENDER` / `PASSWORD`) and raising `ConfigError` when missing. A missing or
  invalid YAML raises `ConfigError`.
- `models.py` — `Persona` (dataclass; validates non-empty name and a mandatory well-formed email in
  `__post_init__`, hashed/compared **by name only**), `Asignacion` (rejects self-assignment) and
  `ConfigData` (config container with defaults).
- `exceptions.py` — `InvisibleFriendError` base + `ConfigError`, `EmailError`, `ValidationError`,
  `AssignmentError`. Every failure raised by the package derives from the base.
- `validators.py` — `ParejaValidator`. Holds restrictions as a `set[frozenset[str]]` so lookups are
  **bidirectional** (`A-B` == `B-A`). `es_pareja_valida()` (false for the same person or a forbidden
  pair), `validar_ciclo()` (checks every `i → i+1` edge, wrapping around; raises `ValidationError`
  on an empty list), plus add/remove/list restrictions.
- `services/secret_santa.py` — `SecretSantaService`. `generar_asignaciones()` shuffles the list and
  builds the cycle `persona[i] → persona[(i+1) % n]`, retrying up to `max_intentos` until
  `validar_ciclo()` passes; raises `AssignmentError` with <2 people or when attempts run out. The
  cycle guarantees everyone gives once and receives once. Also
  `obtener_asignaciones_formateadas()` (`Persona` dict → name dict) and `imprimir_asignaciones()`.
- `services/email_service.py` — `EmailService`. `crear_email()` builds the `EmailMessage`,
  `enviar_email()` sends it over `smtplib.SMTP_SSL` with an `ssl.create_default_context()`,
  `enviar_asignacion()` renders the template, and `enviar_asignaciones_masivas()` loops over the
  assignments returning `(exitosos, fallidos)`. **`simular=True` skips the network entirely.** A
  participant without an email is logged as a warning and counted as failed, not raised.
- `templates/email_template.py` — `EmailTemplate`: `ASUNTO` plus `generar_email()` (plain text) and
  `generar_email_html()`. All the copy is **Spanish** and user-facing.
- `utils/logger.py` — `get_logger()`; process-wide singleton logger with a UTF-8 console handler
  (INFO) and a UTF-8 file handler (DEBUG) writing to `logs/invisible_friend.log`. Creates `logs/`
  on import.
- `utils/file_handler.py` — `FileHandler`: static `guardar_json()` / `cargar_json()` (UTF-8,
  `ensure_ascii=False`, creates parent dirs) and `guardar_asignaciones()`, which wraps the mapping
  as `{"asignaciones": ..., "total_personas": n}`. Failures become `InvisibleFriendError`.

## Entry point (`__main__.py`)
- `InvisibleFriendApp` wires `Config` → `ParejaValidator` → `SecretSantaService` → `EmailService` in
  `__init__`; `ejecutar_completo(enviar=False, output_path=...)` runs the 4 steps: generate → print →
  save to `output/asignaciones.json` → send (**simulated unless `enviar=True`**).
- `parse_args()` defines `--enviar` (default `False`), `--config` (default `config/settings.yaml`),
  `--output` (default `output/asignaciones.json`) and `--version`.
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
- Sending emails is **opt-in**: any new caller defaults to `simular=True` / `enviar=False`.
- Participant names and emails are **personal data**: they live in `config/settings.yaml` and the
  generated `output/` and `logs/`, all gitignored. They never go into code, tests, docs or fixtures.

## Stack and versioning
See `CLAUDE.md` (root) and `.github/copilot-instructions.md` (Stack section = canonical dependency
versions). Version follows SemVer, single-sourced in `pyproject.toml` and tracked in `CHANGELOG.md`.
