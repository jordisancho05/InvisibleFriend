# InvisibleFriend — Project Structure

> Structure reference. The authoritative guide (stack, run, conventions, gotchas) lives in `CLAUDE.md`
> (root). Detailed architecture lives in `project-architecture.md`.

## Directory tree
```text
Pinvisiblefriend/
├── pyproject.toml            # Metadata + version (SemVer) + deps + tool config (ruff, mypy, pytest)
├── main.py                   # Thin launcher: `python main.py [--send] [--config P] [--output P]`
├── CHANGELOG.md              # Keep a Changelog format
├── README.md                 # User-facing docs (Spanish)
├── CLAUDE.md                 # Agent guide; mirrored by .github/copilot-instructions.md
├── LICENSE / NOTICE.md       # MIT + third-party attributions
├── .env                      # SECRETS (MAILSENDER / PASSWORD) — gitignored
├── .env.example              # Template for .env
├── config/
│   ├── settings.yaml         # PERSONAL DATA: participants + forbidden pairs — gitignored
│   └── settings.example.yaml # Template with fake names
├── src/
│   └── invisible_friend/
│       ├── __init__.py       # __version__ from installed metadata
│       ├── __main__.py       # InvisibleFriendApp + parse_args() + main()
│       ├── config.py         # Config: root .env + YAML → ConfigData
│       ├── models.py         # Person / Assignment / ConfigData dataclasses
│       ├── exceptions.py     # InvisibleFriendError + 4 subclasses
│       ├── validators.py     # PairValidator (symmetric frozenset restrictions)
│       ├── services/
│       │   ├── secret_santa.py   # SecretSantaService: cyclic assignment + retries
│       │   └── email_service.py  # EmailService: SMTP_SSL send + simulate mode
│       ├── templates/
│       │   └── email_template.py # EmailTemplate: Spanish body (text + HTML)
│       └── utils/
│           ├── logger.py         # get_logger(): singleton, console INFO + file DEBUG
│           └── file_handler.py   # FileHandler: JSON save/load
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Shared fixtures (fake participants, services)
│   ├── test_config.py
│   ├── test_email_service.py
│   ├── test_email_template.py
│   ├── test_file_handler.py
│   ├── test_main.py          # Pins that the default run never sends email
│   ├── test_models.py
│   ├── test_secret_santa.py
│   ├── test_validators.py
│   └── test_version.py
├── scripts/
│   └── demo.py               # Demonstration script (not production code)
├── output/                   # GENERATED: assignments.json — gitignored
├── logs/                     # GENERATED: invisible_friend.log — gitignored
├── .plan/                    # Plans (planner→implementer)
│   └── <usecase>/<type>/<slug>.md   # usecase: assignment|email|config|general; type: feat|fix|refactor
├── .github/
│   └── copilot-instructions.md
├── .venv/                    # Virtual environment — gitignored
└── .claude/skills/{caveman,planner,implementer,pr-review,references}/
```

## Notes
- **Two names, one project**: the source package is `invisible_friend` (underscore, under `src/`);
  the distribution is `invisible-friend` (hyphen, in `pyproject.toml`). Don't mix them in imports.
- `output/` and `logs/` are created at runtime (`file_handler.py` and `logger.py` respectively) and
  are gitignored — they contain participants' real names.
- `config/settings.yaml` and `.env` are gitignored; only the `*.example.*` files are versioned. When
  a config key changes, update the example file too.
- The suite covers every module (73 tests, ~97%); shared fixtures live in `tests/conftest.py` and use
  fake participants only.
- Three equivalent entry points: `python main.py`, `python -m invisible_friend` and the
  `invisible-friend` console script. All default to **simulating** the email send.
- The venv is `.venv/` (gitignored). Don't reintroduce broad ignore patterns like `[Ss]cripts` — they
  would silently hide `scripts/`.
