# Common Workflows — InvisibleFriend

> Loaded by `planner` (domain-analysis Step 3) and `implementer` when a change matches one of these
> recipes. Each recipe lists the files to touch in order and the test that pins it.

## Add a YAML config key
1. `config/settings.example.yaml` → add the key with a **fake/neutral** value and a comment.
2. `config.py` → read it in `_parse_config()` with a sane default (`section.get('key', default)`),
   store it in `ConfigData` (`models.py`) and expose it as a `@property`.
3. Consumers read it from the `Config` object — never re-open the YAML or call `os.getenv` elsewhere.
4. `README.md` → document the key in the configuration section.
5. Test: `tests/test_config.py` → build a temp YAML with `tmp_path`, assert the default when absent
   and the parsed value when present; a malformed YAML raises `ConfigError`.
- Gotcha: don't touch `config/settings.yaml` (real data, gitignored). Work on the example file.

## Add a secret / environment variable
1. `.env.example` → add the name with a placeholder value.
2. `config.py` → expose it as a `@property` reading `os.getenv(...)` and raising `ConfigError` when
   missing (the pattern of `email_sender` / `email_password`). Never a bare `os.getenv` in a service.
3. Test: `tests/test_config.py` → `monkeypatch.setenv` for the happy path, `monkeypatch.delenv` +
   `pytest.raises(ConfigError)` for the missing one.
- Gotcha: the secret goes in `.env` **only** — never in the YAML, in a test, or in a doc example.

## Change the assignment algorithm / add a restriction rule
1. `validators.py` → the rule belongs in `ParejaValidator` (`es_pareja_valida` for a pairwise rule,
   `validar_ciclo` for a whole-cycle rule). Keep restrictions **symmetric** (`frozenset`).
2. `services/secret_santa.py` → only touch it if the *search strategy* changes (shuffle + retry up to
   `max_intentos`); the rule itself stays in the validator.
3. Test: `tests/test_validators.py` for the rule (pure unit, both directions `A-B` / `B-A`), and
   `tests/test_secret_santa.py` for the invariants over many runs (still a single cycle, no fixed
   point, no forbidden pair). Never assert one concrete mapping — the shuffle is random.
- Gotcha: a stricter rule can make the problem unsatisfiable; assert the `AssignmentError` path too.

## Change the email content / template
1. `templates/email_template.py` → `ASUNTO`, `generar_email()` (plain text) and/or
   `generar_email_html()`. Copy stays in **Spanish**.
2. `services/email_service.py` → only if the *sending* changes (headers, MIME parts, HTML alternative);
   the wording never lives in the service.
3. Test: `tests/test_email_service.py` (or a new `tests/test_email_template.py`) → assert the rendered
   body contains the recipient's name and their assigned person, with **fake names**.
- Gotcha: `enviar_asignacion(usar_template=True)` currently sends the plain-text body;
  `generar_email_html()` is not wired into any send path.

## Add a CLI flag
1. `src/invisible_friend/__main__.py` → add the argument in `parse_args()` (next to `--enviar`,
   `--config`, `--output`, `--version`) and thread it through `main()` into
   `InvisibleFriendApp.ejecutar_completo(...)`. The root `main.py` is a thin launcher and needs no
   change.
2. Document it in the README's flag table.
3. Test: `tests/test_main.py` → assert `parse_args([...])` yields the expected value **and** that the
   flag changes the branch taken, monkeypatching the collaborators; no SMTP, no real config file.
- Gotcha: real sending must stay explicit and opt-in. `enviar` / `simular` default to not sending —
  never flip that, and never add a flag whose *absence* sends.

## Bump the version (SemVer)
1. Decide the bump: **patch** (fix), **minor** (backward-compatible feat), **major** (breaking).
2. `pyproject.toml` → `version = "X.Y.Z"` (single source of truth).
3. `CHANGELOG.md` → move the `## [Unreleased]` entries under a new `## [X.Y.Z] - <date>` heading and
   update the link refs at the bottom.
4. `git tag vX.Y.Z` + `git push --follow-tags` — **only when the user asks**.
- Gotcha: `config/settings.yaml` also carries an `app.version` field; it is decorative and unused by
  the code. Don't treat it as a second source of truth.
