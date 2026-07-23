# Common Commands — InvisibleFriend

> Python project. Commands assume Windows + PowerShell (adjust the venv activate path on other OSes).

## Environment
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"                   # editable install + dev tools (pytest, ruff, mypy, ...)
```

## Configure (both files are gitignored — they hold real data)
```powershell
Copy-Item .env.example .env                             # then fill MAILSENDER / PASSWORD
Copy-Item config\settings.example.yaml config\settings.yaml   # then fill participants + restrictions
```
- `PASSWORD` must be a Gmail **app password**, not the account password.

## Run
```powershell
python main.py                             # generate → print → save JSON → SIMULATE the emails
python main.py --enviar                    # actually send over SMTP
python main.py --config otro.yaml --output salida.json
python main.py --help                      # all flags
# equivalent entry points:
python -m invisible_friend
invisible-friend                           # console script (after pip install -e .)
```
- The default run **does not send email**: `--enviar` is the only path that opens an SMTP connection.
- Output lands in `output/asignaciones.json`; logs in `logs/invisible_friend.log`.

## Test
```powershell
pytest                                     # whole suite
pytest tests/test_secret_santa.py          # one file
pytest tests/test_validators.py::test_nadie_puede_ser_su_propio_amigo_invisible   # one test
pytest -k email                            # by keyword
pytest -q                                  # quiet
pytest --cov=invisible_friend --cov-report=term-missing   # coverage (opt-in, not in addopts)
```
- **No SMTP in tests**: `smtplib.SMTP_SSL` is mocked (`unittest.mock.patch`) and bulk sends use
  `simular=True`. A test that opens a socket is a bug.
- Randomness: `SecretSantaService` shuffles, so assert **invariants** (it's a cycle, no forbidden
  pair, everyone appears once) or seed `random` — never a fixed expected mapping.

## Lint / format / types
```powershell
ruff check .                               # lint
ruff check . --fix                         # autofix
ruff format .                              # format
mypy src                                   # static types
```

## Version bump (SemVer)
```powershell
# edit the version in pyproject.toml, then:
git tag v1.1.0
git push --follow-tags
```
- Version is single-sourced in `pyproject.toml`; the `CHANGELOG.md` entry follows.
