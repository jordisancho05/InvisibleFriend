# 🎁 Invisible Friend - Scalable Secret Santa System

A professional, scalable application to generate and send **Secret Santa** (Amigo Invisible) assignments, with restriction validation, robust error handling, centralized logging and unit tests.

## 🌟 Features

✅ **Smart assignment generation** - Cyclic algorithm that forms a perfect cycle
✅ **Restriction validation** - Avoids configurable forbidden pairs
✅ **Email delivery** - Gmail SMTP integration
✅ **Explicit sending** - Simulates by default; only `--send` opens a real connection
✅ **Centralized configuration** - YAML + environment variables
✅ **Full type hints** - Checked with mypy
✅ **Extensive logging** - Event and error tracing
✅ **Unit tests** - 73 tests, 97% coverage
✅ **Robust error handling** - Specific exceptions
✅ **Scalable architecture** - Separation of concerns

---

## 📁 Project Structure

```
Pinvisiblefriend/
├── src/invisible_friend/        # Main package (src-layout)
│   ├── __init__.py              # __version__ (read from metadata)
│   ├── __main__.py              # CLI: InvisibleFriendApp + argparse
│   ├── config.py                # Configuration management (YAML + .env)
│   ├── models.py                # Dataclasses (Person, Assignment, ConfigData)
│   ├── exceptions.py            # Custom exceptions
│   ├── validators.py            # Pair validation
│   ├── services/
│   │   ├── secret_santa.py      # Assignment generation logic
│   │   └── email_service.py     # Email sending service
│   ├── utils/
│   │   ├── logger.py            # Centralized logging
│   │   └── file_handler.py      # JSON file I/O
│   └── templates/
│       └── email_template.py    # Email templates
├── config/
│   ├── settings.example.yaml    # Template of participants and restrictions
│   └── settings.yaml            # PRIVATE: your real participants
├── tests/                       # pytest suite (conftest + 8 modules)
├── scripts/
│   └── demo.py                  # Demo script
├── .env                         # PRIVATE: Gmail credentials
├── .env.example                 # Environment variables template
├── main.py                      # Root-level launcher
├── pyproject.toml               # Project configuration and dependencies
├── CHANGELOG.md                 # Change history (Keep a Changelog)
├── LICENSE                      # MIT license
├── NOTICE.md                    # Third-party attributions
└── README.md
```

> The `output/` and `logs/` directories are created automatically on the first
> run and are not versioned: they contain participants' personal data.

---

## 🚀 Quick Install

Requires **Python 3.11 or higher**.

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1

# 2. Install the project (editable) and the dev tools
pip install -e ".[dev]"

# 3. Configure credentials (PRIVATE)
cp .env.example .env
# Edit .env with your Gmail credentials

# 4. Configure people and restrictions (PRIVATE)
cp config/settings.example.yaml config/settings.yaml
# Edit config/settings.yaml with YOUR people and restrictions

# 5. Verify everything loads
python scripts/demo.py
```

> The project uses **src-layout**, so it must be installed (`pip install -e .`)
> for `import invisible_friend` to work. The tests don't need it:
> `pythonpath` is configured in `pyproject.toml`.

### 🔑 Environment variables (`.env`)

| Variable | Description |
|----------|-------------|
| `MAILSENDER` | Gmail account the emails are sent from |
| `PASSWORD` | **App password** for that account, not the regular password |

They are generated at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
(requires two-step verification enabled).

### ⚙️ Configuration (`config/settings.yaml`)

| Key | Description | Default |
|-----|-------------|---------|
| `app.max_attempts` | Maximum attempts to find a valid cycle | `100` |
| `email.smtp_server` | SMTP server | `smtp.gmail.com` |
| `email.smtp_port` | SMTP port (SSL) | `465` |
| `participants` | List of `{name, email}` participants | — |
| `restrictions` | Pairs `[A, B]` that must not touch | `[]` |

Restrictions are **bidirectional**: `["Alice", "Bob"]` prevents both Alice
giving to Bob and the other way around.

### 🔐 Privacy Structure

```
Git Repository
├── .env.example                ✅ Include in Git (template)
├── .env                        ❌ DO NOT include (private, in .gitignore)
├── config/
│   ├── settings.example.yaml   ✅ Include in Git (template)
│   └── settings.yaml           ❌ DO NOT include (private, in .gitignore)
├── output/                     ❌ DO NOT include (real assignments)
├── logs/                       ❌ DO NOT include (emails in the logs)
├── .gitignore
└── ...
```

**Private files (NOT versioned):**
- `.env` - Contains your Gmail credentials
- `config/settings.yaml` - Contains real names and emails
- `output/` - The generated assignments (they spoil the draw)
- `logs/` - The logs record the participants' emails

**Public templates (versioned):**
- `.env.example` - Structure without real values
- `config/settings.example.yaml` - Structure without sensitive data

### ⚠️ Data Validation

- **Name**: Required, non-empty string
- **Email**: Required, must be a valid email (e.g. person@example.com)
- **Restrictions**: Pairs of names that CANNOT be Secret Santas (mutual)

---

## 💻 Usage

### Basic run (safe mode: simulates the emails)
```bash
python main.py
```

Generates the assignments, prints them to the console, saves them to
`output/assignments.json` and **simulates** sending without opening any connection.

### With real email sending
```bash
python main.py --send
```

### Available options
```bash
python main.py --help
```

| Flag | Description | Default |
|------|-------------|---------|
| `--send` | Actually sends the emails | disabled (simulates) |
| `--config PATH` | Path to the participants YAML | `config/settings.yaml` |
| `--output PATH` | Where to save the assignments JSON | `output/assignments.json` |
| `--version` | Show the version | — |

### Equivalent ways to run it
```bash
python main.py --send             # root-level launcher
python -m invisible_friend --send # as a module
invisible-friend --send           # console script (after pip install)
```

### Programmatic usage
```python
from pathlib import Path
from invisible_friend.__main__ import InvisibleFriendApp

app = InvisibleFriendApp(Path("config/settings.yaml"))
assignments = app.generate_assignments()
app.show_assignments(assignments)
app.save_assignments(assignments)
app.send_emails(assignments, simulate=True)
```

---

## 🧪 Unit Tests

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=invisible_friend --cov-report=term-missing

# Specific tests
pytest tests/test_validators.py -v
```

No test opens a socket or reads your `.env` or your `config/settings.yaml`: SMTP
is patched and the data is fake.

### Linting and types
```bash
ruff check .        # lint
ruff format .       # formatting
mypy src            # type checking
```

---

## 🏗️ Component Architecture

| Module | Responsibility |
|--------|----------------|
| **Config** | Load YAML, environment variables, validate configuration |
| **PairValidator** | Validate allowed/forbidden pairs bidirectionally |
| **SecretSantaService** | Generate valid assignment cycles |
| **EmailService** | Create and send emails via SMTP |
| **EmailTemplate** | Email body in plain text and HTML |
| **FileHandler** | Save/load data as JSON |
| **LoggerConfig** | Centralized logging system (console + file) |
| **InvisibleFriendApp** | Orchestrates the full flow from the CLI |

---

## 📊 Logging

Logs available at:
- **Console**: INFO level and above
- **File**: `logs/invisible_friend.log`

---

## 🛡️ Error Handling

Specific exceptions for each case:

```python
from invisible_friend.exceptions import (
    ConfigError,  # Configuration errors
    ValidationError,  # Validation errors
    AssignmentError,  # Assignment errors
    EmailError,  # Email sending errors
)
```

They all inherit from `InvisibleFriendError`, so you can catch them all at once.

---

## ✨ Advanced Features

- ✅ Guaranteed cycle (each person gives once and receives once)
- ✅ Bidirectional restriction validation
- ✅ Automatic retries to generate valid assignments
- ✅ Customizable email templates
- ✅ Risk-free send simulation (default behavior)
- ✅ Full type hints (checked with mypy)
- ✅ Unit test coverage
- ✅ Centralized configuration management

---

## 📝 License

This project is licensed under the **MIT** license - see the [LICENSE](LICENSE) file for details.

### Attributions

This project uses the following libraries under the MIT license:

- **PyYAML** - YAML parser: https://pyyaml.org/
- **python-dotenv** - Environment variable loading: https://github.com/theskumar/python-dotenv

For more information about attributions, see [NOTICE.md](NOTICE.md)

---
