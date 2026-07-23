# GitHub Copilot Instructions — InvisibleFriend

> This file is kept in sync with `CLAUDE.md` (repo root). See it for the full picture.

CLI app in **Python**. Reads the participants and the forbidden pairs from a YAML file, generates a
Secret Santa (Amigo Invisible) assignment as a single cycle, prints it, saves it to JSON and emails
each participant their assigned person over Gmail SMTP. Packaged app under `src/invisible_friend/`.

## Always Remember
- **Never commit secrets or personal data.** `MAILSENDER` / `PASSWORD` live in the root `.env`; the
  participants' real names and emails live in `config/settings.yaml`; `output/` and `logs/` hold
  generated copies. All gitignored — only the `*.example.*` templates (fake names) are versioned.
- **Sending email is opt-in**: the default run simulates; only `--send` opens an SMTP connection.
- **Language split**: code is **English** (identifiers, docstrings, comments, logs, console, CLI).
  **Spanish is used ONLY for the participant email copy** — the subject and bodies in
  `templates/email_template.py` and the plain-text fallback in `email_service.py`. Don't translate
  those, and don't add Spanish anywhere else.
- **Tests never touch the outside world**: no SMTP socket, no real `.env` / `settings.yaml`. Patch
  `smtplib.SMTP_SSL`, use `tmp_path` / `monkeypatch`, fake names only. Email-copy assertions stay
  Spanish.
- **Don't commit or push** unless explicitly asked.

## Stack
- **Python ≥3.11** (developed on 3.14)
- `PyYAML` ≥6.0 — parse `config/settings.yaml`
- `python-dotenv` ≥1.0 — load the root `.env`
- stdlib `smtplib` + `ssl` — Gmail SMTP over SSL (port 465)
- Dev: `pytest`, `pytest-cov`, `pytest-mock`, `ruff`, `mypy`, `types-PyYAML` (the `dev` extra).

## Run & Test
```powershell
pip install -e ".[dev]"          # editable install + dev tools
python main.py                    # generate → print → save JSON → SIMULATE the emails
python main.py --send             # actually send
# equivalent: python -m invisible_friend | invisible-friend (console script)
pytest                            # test suite (no network, no SMTP)
ruff check . ; mypy src           # lint + types
```

## Architecture (`src/invisible_friend/`)
- `config.py` — `Config`: root `.env` + YAML → `ConfigData`; missing/malformed (and a participant
  without a `name`) → `ConfigError`.
- `models.py` — `Person` (mandatory valid email; equality/hash **by name**), `Assignment`
  (`giver`/`receiver`, no self-assignment), `ConfigData`.
- `exceptions.py` — `InvisibleFriendError` + `ConfigError` / `EmailError` / `ValidationError` /
  `AssignmentError`.
- `validators.py` — `PairValidator`: symmetric restrictions (`frozenset`), `is_valid_pair()`,
  `validate_cycle()` (includes the wrap-around edge).
- `services/secret_santa.py` — shuffle + build the cycle `person[i] → person[(i+1) % n]`, retry to
  `max_attempts`; `AssignmentError` with <2 participants or on exhaustion.
- `services/email_service.py` — `SMTP_SSL` send; `send_assignments()` → `(successful, failed)`; a
  participant with no email is a warning + a failure, not an exception. Fallback body copy is Spanish.
- `templates/email_template.py` — `SUBJECT` + `render_body()` / `render_html()` (Spanish copy).
- `utils/` — `get_logger()` (console INFO + `logs/` DEBUG) and `FileHandler`
  (`save_json` / `load_json` / `save_assignments`, UTF-8).
- `__main__.py` — `InvisibleFriendApp` + `parse_args()` / `main()` (`--send`, `--config`, `--output`,
  `--version`); root `main.py` is a thin launcher; `__init__.py` exposes `__version__`.

## Conventions
- Read config from the `Config` object, not scattered `os.getenv`. New code logs via
  `get_logger(__name__)`, not `print`. Type-hint new public functions (`disallow_untyped_defs`).
- Raise the project's own exceptions, chained with `raise ... from e`. Layering points downward only.
- **Domain invariants**: single cycle, no fixed points, everyone gives and receives once, symmetric
  restrictions. The shuffle is random — assert invariants over many runs, never one fixed mapping.
