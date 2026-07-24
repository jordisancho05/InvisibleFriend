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
python main.py --send                      # actually send over SMTP
python main.py --debug                     # also record the draw itself in the log file
python main.py --config other.yaml --output out.json
python main.py --help                      # all flags
# equivalent entry points:
python -m invisible_friend
invisible-friend                           # console script (after pip install -e .)
```
- The default run **does not send email**: `--send` is the only path that opens an SMTP connection,
  and the only one that reads `MAILSENDER` / `PASSWORD`. A dry run needs no `.env`.
- Output lands in `output/assignments.json`; logs in `logs/invisible_friend.log` (rotating).
- **The log never records who was drawn for whom unless you pass `--debug`.** A normal run logs at
  most `Email sent to <name>`. Use `--debug` to review a past draw, and remember the file keeps it.

## Test
```powershell
pytest                                     # whole suite
pytest tests/test_secret_santa.py          # one file
pytest tests/test_validators.py::test_nobody_can_be_their_own_secret_friend   # one test
pytest -k email                            # by keyword
pytest -q                                  # quiet
pytest --cov=invisible_friend --cov-report=term-missing   # coverage (opt-in, not in addopts)
```
- **No SMTP in tests**: `smtplib.SMTP_SSL` is mocked (`unittest.mock.patch`) and bulk sends use
  `simulate=True`. A test that opens a socket is a bug.
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
