# Execution Rules — how to implement in InvisibleFriend

> Canonical mechanics for writing code in this repo. The `implementer` skill applies them per plan
> subtask; `CLAUDE.md` makes the TDD cycle mandatory for **any** code change, plan or not.

## Inverse TDD (mandatory for every code change)
1. Write the tests that pin the expected behavior first (`pytest`).
2. Run them and **confirm they FAIL (red)** before implementing.
3. Implement until they **PASS (green)**.
4. Don't move on with red tests.
5. If a behavior can't be unit-tested (a real Gmail SMTP send, how the email renders in an inbox, a
   run against the real `config/settings.yaml`), say so **explicitly**: name what is uncovered and how
   it was verified instead (it belongs in the plan's `Uncovered / manual verification` section,
   verified via `python main.py` or one real send to your own address). Never claim it works without
   running it.
- Test style per layer: `@.claude/skills/planner/references/test-quality-rules.md`.

## Retry cap
- If a test is still red after **3 distinct implementation attempts** (different approaches, not
  re-runs), STOP: record the failure in the plan's `## Deviations` section (per
  `annotation-format.md`) and ask the user. Grinding past 3 attempts hides a wrong plan assumption.

## Run / test
- Commands via `@.claude/skills/references/common-commands.md` (`pytest`, `ruff check .`, `mypy src`,
  `pip install -e ".[dev]"`, `python main.py`). Tests must never open a socket or read the real config:
  patch `smtplib.SMTP_SSL` with `unittest.mock.patch`, use `simular=True` for bulk sends, `tmp_path`
  for files and `monkeypatch` for env vars.
- A step isn't green until `pytest` for it passes **and** `ruff check .` is clean on the touched files.

## Project rules
- Apply every **`CLAUDE.md` "Always Remember"** gotcha — it is always in context, so the list is not
  restated here (secrets and personal data out of git; English code / Spanish email copy; real sending
  is opt-in).
- Domain invariants that must survive any change (see
  `@.claude/skills/references/project-architecture.md` §Invariants): the assignment is a **single
  cycle**, restrictions are **symmetric**, `simular` / `enviar` default to not sending.
- Code-style additions not in `CLAUDE.md`:
  - **Type hints** on new public functions; the project targets `mypy` with `disallow_untyped_defs`.
  - New code logs via `get_logger(__name__)` from `utils/logger.py`, not `print`. The existing `print`
    calls in `main.py` and `imprimir_asignaciones()` are the deliberate CLI output — don't propagate
    the pattern into services.
  - Read configuration from the `Config` object, never `os.getenv` or a second `yaml.safe_load`
    scattered across modules.
  - Raise the project's own exceptions (`exceptions.py`), never a bare `Exception`; every new error
    type derives from `InvisibleFriendError`.
  - Keep the layering downward-only: `models`/`validators` never import a service; no service imports
    `main`.
- **Never edit `config/settings.yaml`, `.env`, `output/` or `logs/`** — real personal data. Change the
  `*.example.*` templates instead.

## Scope
- Implement **only** what the plan describes. If an ambiguity or uncovered requirement appears, **STOP
  and ask**; don't improvise outside the plan (the plan's `## Out of scope` is the boundary).
