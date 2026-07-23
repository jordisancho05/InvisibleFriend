# Test Quality Rules — how to test in InvisibleFriend

> Used by the `planner` skill to write each GRAPH STEP's **Tests** block, and by `implementer` when
> running them. Reflects the conventions in `tests/` (pytest).

## TDD-first (mandatory)
The red→green cycle is defined once, in
`@.claude/skills/implementer/references/execution-rules.md` (canonical); it applies to every code
subtask. Build/test via `@.claude/skills/references/common-commands.md` (`pytest`). This file only
defines **how the tests themselves are written**.

## Style per layer
- **Pure domain** (`models.py`, `validators.py`) → plain `pytest` unit tests, no I/O. Build `Persona`
  objects with fake data, assert the boolean/exception. Restrictions are symmetric: test `A-B`
  **and** `B-A`. Use `@pytest.mark.parametrize` for the validation branches (empty name, invalid
  email, self-pairing). E.g. `tests/test_validators.py`.
- **Assignment service** (`services/secret_santa.py`) → the shuffle is random, so assert
  **invariants over many runs**, never one expected mapping:
  - every participant appears exactly once as giver and once as receiver;
  - nobody is assigned to themselves;
  - no pair violates the restrictions;
  - it is a **single cycle** — follow `n` hops from any start and you return to it having seen all `n`.
  Pin the failure path too: `<2` people and an unsatisfiable restriction set → `AssignmentError`.
  Seed `random.seed(...)` only when a test genuinely needs determinism. E.g.
  `tests/test_secret_santa.py`.
- **Email service** (`services/email_service.py`) → **never open a socket**. Patch
  `smtplib.SMTP_SSL` with `unittest.mock.patch` and assert on the mock (login called with the sender,
  `sendmail` called with the right recipient, the `with` block entered). For bulk sends prefer
  `simular=True` and assert the returned `(exitosos, fallidos)` — including that a participant
  without an email counts as failed and doesn't raise. An SMTP error must surface as `EmailError`.
  E.g. `tests/test_email_service.py`.
- **Templates** (`templates/email_template.py`) → pure string assertions: the rendered body contains
  the recipient's name and their assigned person. Copy stays Spanish.
- **Config** (`config.py`) → write a temp YAML with `tmp_path` and point `Config` at it; assert
  parsed values and defaults, and that a missing file / malformed YAML raises `ConfigError`. Secrets
  via `monkeypatch.setenv` / `delenv` (`MAILSENDER`, `PASSWORD`) → missing raises `ConfigError`.
  **Never** read the real `config/settings.yaml` or `.env` in a test. E.g. `tests/test_config.py`.
- **File I/O** (`utils/file_handler.py`) → `tmp_path`; assert the round-trip and the UTF-8 /
  `ensure_ascii=False` behavior (accented names survive). E.g. `tests/test_file_handler.py`.

## Conventions
- Files `tests/test_<module>.py`; functions `test_<behavior>`. Shared fixtures in `tests/conftest.py`.
- Test names / docstrings describe the **behavior**, not the function: "rechaza una pareja prohibida
  en ambos sentidos" / "returns None and logs when the file is missing". Match the language already
  used in the neighbouring test file.
- **Fake data only.** Alice/Bob/Charlie + `@example.com`. Never a participant's real name or email —
  tests are versioned, `config/settings.yaml` is not.
- **No network, no SMTP, no real config files** in any test. Patch `smtplib.SMTP_SSL`, use `tmp_path`
  for files, `monkeypatch` for env.
- User-facing text that gets asserted stays in **Spanish** (the email copy); code stays English.

## How to fill `Tests` in a GRAPH STEP
- **Why (TDD)**: the observable behavior the test blocks before implementing.
- **How**: `tests/<test_xxx.py>` → `test_<behavior>` + the chosen style (pure unit / invariants /
  patched SMTP / tmp_path / monkeypatch). If extending an existing test, name it.
