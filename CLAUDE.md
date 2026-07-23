# CLAUDE.md

Guidance for Claude Code (and other agents) working in this repo. `.github/copilot-instructions.md`
is kept in sync with this file.

## What this is
CLI app in **Python**. Reads the participants and the forbidden pairs from a YAML file, generates a
Secret Santa (Amigo Invisible) assignment as a single cycle, prints it, saves it to JSON and emails
each participant their assigned person over Gmail SMTP. Packaged app under `src/invisible_friend/`.

## Always Remember
- **Never commit secrets or personal data.** `MAILSENDER` / `PASSWORD` live in the root `.env` only;
  the participants' real names and emails live in `config/settings.yaml`; `output/` and `logs/` hold
  generated copies of both. All four are gitignored — keep them that way. Only the `*.example.*`
  templates are versioned, and they use fake names.
- **Sending email is opt-in.** The default run simulates (`simular=True` / `enviar=False`); only
  `--enviar` opens an SMTP connection. Never flip a default to send.
- **Code language split**: comments, logs and docstrings in **Spanish** (matching the existing code);
  the domain vocabulary (`Persona`, `generar_asignaciones`, `es_pareja_valida`) is Spanish too — don't
  translate it. The email copy is user-facing Spanish; don't translate those literals either.
- **Tests never touch the outside world**: no SMTP socket, no real `.env`, no real
  `config/settings.yaml`. Patch `smtplib.SMTP_SSL`, use `tmp_path` and `monkeypatch`, fake names only.
- **Don't commit or push** unless explicitly asked.

## Stack
- **Python ≥3.11** (developed on 3.14)
- `PyYAML` ≥6.0 — parse `config/settings.yaml`
- `python-dotenv` ≥1.0 — load the root `.env`
- stdlib `smtplib` + `ssl` — Gmail SMTP over SSL (port 465)
- Dev: `pytest`, `pytest-cov`, `pytest-mock`, `ruff`, `mypy`, `types-PyYAML` (the `dev` extra).

## Run & Test
```powershell
python -m venv .venv; .venv\Scripts\Activate.ps1
pip install -e ".[dev]"          # editable install + dev tools
python main.py                    # generate → print → save JSON → SIMULATE the emails
python main.py --enviar           # actually send
# equivalent: python -m invisible_friend | invisible-friend (console script)
pytest                            # test suite (no network, no SMTP)
ruff check . ; mypy src           # lint + types
```
Config lives in `.env` (secrets, root) and `config/settings.yaml` (participants + forbidden pairs);
copy them from `.env.example` and `config/settings.example.yaml`. Full commands:
`.claude/skills/references/common-commands.md`.

## Architecture (`src/invisible_friend/`)
- `config.py` — `Config`: loads the root `.env` via `find_dotenv(usecwd=True)`, parses the YAML into
  `ConfigData`, exposes `personas` / `restricciones` / `max_intentos` / `smtp_*` as properties and
  `email_sender` / `email_password` from env. Anything missing or malformed → `ConfigError`.
- `models.py` — `Persona` (validates name + mandatory well-formed email; hashed and compared **by name
  only**), `Asignacion` (rejects self-assignment), `ConfigData`.
- `exceptions.py` — `InvisibleFriendError` base + `ConfigError`, `EmailError`, `ValidationError`,
  `AssignmentError`.
- `validators.py` — `ParejaValidator`: restrictions as `set[frozenset[str]]` so `A-B` == `B-A`;
  `es_pareja_valida()`, `validar_ciclo()` (checks every edge including the wrap-around).
- `services/secret_santa.py` — `SecretSantaService.generar_asignaciones()`: shuffle, build the cycle
  `persona[i] → persona[(i+1) % n]`, retry up to `max_intentos` until the validator passes; raises
  `AssignmentError` with <2 people or when attempts run out.
- `services/email_service.py` — `EmailService`: builds the `EmailMessage`, sends over
  `smtplib.SMTP_SSL`, and `enviar_asignaciones_masivas()` returns `(exitosos, fallidos)`. A
  participant with no email is a logged warning + a failure count, never an exception.
- `templates/email_template.py` — `EmailTemplate`: subject and body (plain text + HTML), Spanish.
- `utils/logger.py` — `get_logger()`: singleton, UTF-8 console (INFO) + `logs/invisible_friend.log`
  (DEBUG). `utils/file_handler.py` — JSON save/load, UTF-8, `ensure_ascii=False`.
- `__main__.py` — `InvisibleFriendApp` (wires everything) + `parse_args()` / `main()`
  (`--enviar`, `--config`, `--output`, `--version`). `main.py` at the root is a thin launcher.
  `__init__.py` exposes `__version__` from installed metadata.

## Conventions
- Read configuration from the `Config` object, never scattered `os.getenv` or a second
  `yaml.safe_load`. New code logs via `get_logger(__name__)`, not `print` (the `print`s in
  `__main__.py` and `imprimir_asignaciones()` are the deliberate CLI output).
- Type-hint new public functions (`mypy` runs with `disallow_untyped_defs`). Raise the project's own
  exceptions, never a bare `Exception`; chain with `raise ... from e`.
- Layering points downward only: `models`/`validators` never import a service; no service imports
  `__main__`.
- **Domain invariants**: the assignment is a single cycle (no fixed points, no sub-cycles), everyone
  gives once and receives once, and restrictions are symmetric. Tests assert these invariants over
  many runs rather than one expected mapping — the shuffle is random.
- Version is single-sourced in `pyproject.toml` (SemVer); changes tracked in `CHANGELOG.md`.
