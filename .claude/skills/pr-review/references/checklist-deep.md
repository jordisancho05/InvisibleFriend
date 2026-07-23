# pr-review — Deep Checklist

> Used by the `pr-review` skill (step 3). Itemized review against `CLAUDE.md`. Apply **only** the
> sections matching the diff's scope. Each violation → a finding with `file:line` + the broken rule.

## Privacy & secrets (always)
- No real credential in the diff: `MAILSENDER`, `PASSWORD` or a Gmail app password in code, tests,
  docs or examples. They belong in the root `.env` only.
- **No real participant's name or email.** This is the failure mode specific to this project: names
  and addresses live in `config/settings.yaml` (gitignored). A diff that adds them to a test fixture,
  a docstring, a README example or a plan is a **blocker**.
- `.env`, `config/settings.yaml`, `output/` and `logs/` stay out of the commit; check the diff's file
  list, not just the contents. Only `.env.example` and `config/settings.example.yaml` are versioned,
  with fake data.
- `.gitignore` changes: verify nothing that must stay private became visible, and — the trap that bit
  this repo once — that no broad pattern (`[Ss]cripts`, `[Ll]ib`) silently hides a project folder.

## Domain invariants (`assignment`)
- The result is still a **single cycle**: `n` participants → `n` edges, everyone gives exactly once
  and receives exactly once, no fixed points, no sub-cycles. A change that permutes differently must
  prove this holds.
- Restrictions stay **symmetric** (`frozenset`): a rule that treats `A-B` differently from `B-A` is a
  bug, not a feature.
- A stricter rule can make the problem unsatisfiable — the `AssignmentError` path must stay reachable
  and tested, and the retry loop must remain bounded by `max_attempts`.
- Validation rules belong in `PairValidator`, not inlined into `SecretSantaService`.

## Config (`config`)
- New values are read through the `Config` object. An `os.getenv(...)` or a second `yaml.safe_load`
  outside `config.py` is a warning.
- Every new key the code reads is added to `config/settings.example.yaml` (or `.env.example`) **and**
  documented in the README. A key that exists only in the private file breaks the next clone.
- Missing required config fails loudly with `ConfigError`, never silently defaults to something that
  looks like it worked.

## Email (`email`)
- **Sending stays opt-in.** `simulate=True` / `send=False` remain the defaults; `--send` is the
  only path that opens a connection. A default flipped to send is a blocker.
- The wording lives in `templates/email_template.py`, not in the service. The service handles
  transport only.
- A participant without an email is a logged warning plus a failure count — it must not raise or
  abort the rest of the batch.
- SMTP failures surface as `EmailError`, never as a raw `smtplib` exception escaping the service.

## Languages
- Code is **English**: identifiers, docstrings, comments, log messages and console output. A diff
  that introduces a Spanish identifier or docstring (`Persona`, `generar_asignaciones`) is a warning.
- **Spanish is expected in exactly one place**: the participant email copy — the subject and bodies in
  `templates/email_template.py` and the plain-text fallback in `email_service.py`. Don't let anyone
  "translate those to English", and don't let Spanish copy leak into a log or a variable name.

## Layering & style
- Dependencies point downward only: `models` / `validators` never import a service; no service
  imports `__main__`. A new import that inverts this is a warning.
- New code logs via `get_logger(__name__)`, not `print`. The `print`s in `__main__.py` and
  `print_assignments()` are the deliberate CLI output.
- The project's own exceptions (`exceptions.py`) are raised, never a bare `Exception`, and are
  chained with `raise ... from e`.
- New public functions are type-hinted (`mypy` runs with `disallow_untyped_defs`).

## Tests
- **No network, no SMTP, no real config files.** `smtplib.SMTP_SSL` patched, `tmp_path` for files,
  `monkeypatch` for env and CWD. A test that reads the repo's own `.env` or `config/settings.yaml` is
  a blocker — it passes on your machine and fails everywhere else.
- Assignment tests assert **invariants over many runs**, never one hard-coded expected mapping: the
  shuffle is random and such a test is flaky by construction.
- Changed behavior comes with a test that would have failed before. Fixtures use fake names.
- pytest style: functions and fixtures, not `unittest.TestCase`.

## Packaging & versioning
- The version lives only in `pyproject.toml`; `__version__` reads it from the installed metadata.
  A hardcoded version string anywhere else is a warning (`config/settings.yaml`'s `app.version` is
  decorative and unused — don't start relying on it).
- A new runtime dependency goes in `[project.dependencies]`, a new tool in the `dev` extra, and the
  Stack section of `.github/copilot-instructions.md` is updated.
- `CHANGELOG.md` gains an entry under `## [Unreleased]` for anything user-visible.

## Hygiene
- `ruff check .` clean and `mypy src` clean on the touched files.
- Docs describing the changed behavior are updated in the same diff (`doc-sync.md` lists the set).
- No leftover debug `print`, commented-out code, or a stale reference to a file the diff deleted.
