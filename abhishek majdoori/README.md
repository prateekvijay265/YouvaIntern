# Handshake Project Watcher

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready Windows desktop application that monitors your Handshake AI Projects page and
immediately notifies you when a new project becomes available.

> **⚠️ Important:** This application is a **read-only monitor**. It will **never** automatically
> accept projects, click buttons, submit forms, or perform any actions on your behalf. It only
> observes and notifies.

---

## Table of Contents

- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Development](#development)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- 🔍 **Passive Monitoring** — Polls the Handshake AI Projects page at a configurable interval.
- 🔔 **Instant Windows Notifications** — Uses native Windows toast notifications via `win10toast` / `plyer`.
- 🗂️ **Project Deduplication** — Tracks seen projects to avoid duplicate alerts.
- 💾 **Persistent State** — Survives restarts; known projects are saved to disk.
- 📋 **System Tray Integration** — Runs quietly in the system tray.
- 📝 **Structured Logging** — Rotating file logs + console output with configurable verbosity.
- ⚙️ **Environment-based Config** — All secrets and tunable parameters live in `.env`.
- 🧪 **Fully Tested** — Pytest suite with coverage reporting.
- 🛡️ **Type Safe** — Strict mypy checking throughout.
- 🔧 **Pre-commit Hooks** — Automatic formatting and linting on every commit.

---

## Architecture Overview

```
User's Browser Session
        │
        │  (cookies / session token provided by user)
        ▼
┌─────────────────────┐
│   Watcher Service   │  ← Polls Handshake at a set interval
│  (background loop)  │
└────────┬────────────┘
         │ new project detected
         ▼
┌─────────────────────┐
│  Notification Engine│  ← Windows Toast / Tray alert
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   State Store       │  ← JSON file; tracks seen project IDs
└─────────────────────┘
```

The application is intentionally split into thin, testable layers:

| Layer | Responsibility |
|---|---|
| `config` | Load and validate all settings from `.env` |
| `browser` | Headless browser session management (Playwright) |
| `scraper` | Parse the projects page; extract project metadata |
| `watcher` | Orchestrate polling loop; diff against known state |
| `notifier` | Send Windows desktop notifications |
| `state` | Persist / load seen-project IDs to/from disk |
| `tray` | System-tray icon and menu |
| `cli` | Entry-point; argument parsing |

---

## Project Structure

```
handshake-project-watcher/
├── src/
│   └── handshake_watcher/
│       ├── __init__.py
│       ├── browser/
│       │   ├── __init__.py
│       │   └── session.py          # Playwright browser session management
│       ├── scraper/
│       │   ├── __init__.py
│       │   └── projects.py         # HTML parsing → ProjectListing dataclasses
│       ├── watcher/
│       │   ├── __init__.py
│       │   └── service.py          # Polling loop orchestration
│       ├── notifier/
│       │   ├── __init__.py
│       │   └── windows.py          # Windows toast / plyer notifications
│       ├── state/
│       │   ├── __init__.py
│       │   └── store.py            # JSON-backed persistent state
│       ├── tray/
│       │   ├── __init__.py
│       │   └── icon.py             # System-tray icon via pystray
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py         # pydantic-settings config model
│       ├── cli/
│       │   ├── __init__.py
│       │   └── main.py             # argparse entry-point
│       └── logging_config.py       # Logging setup helper
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Shared fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_scraper.py
│   │   ├── test_state.py
│   │   ├── test_notifier.py
│   │   └── test_config.py
│   └── integration/
│       ├── __init__.py
│       └── test_watcher.py
├── scripts/
│   └── install_playwright.py       # One-shot browser install helper
├── assets/
│   └── icon.png                    # System-tray icon
├── logs/                           # Runtime log directory (git-ignored)
├── .env.example                    # Template for user's .env file
├── .gitignore
├── .pre-commit-config.yaml
├── LICENSE
├── README.md
├── pyproject.toml
└── requirements.txt
```

---

## Requirements

- **Windows 10/11** (toast notifications require Windows)
- **Python 3.11+**
- **Google Chrome** or **Chromium** (used by Playwright)
- A valid Handshake account with an active browser session

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-org/handshake-project-watcher.git
cd handshake-project-watcher
```

### 2. Create a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -e ".[dev]"
```

### 4. Install Playwright browsers

```bash
python scripts/install_playwright.py
# or simply:
playwright install chromium
```

### 5. Configure your environment

```bash
copy .env.example .env
# Then edit .env with your Handshake credentials / session details
```

---

## Configuration

All configuration is managed via the `.env` file. See `.env.example` for full documentation
of every available option.

| Variable | Default | Description |
|---|---|---|
| `HANDSHAKE_BASE_URL` | *(required)* | Base URL of your Handshake instance |
| `HANDSHAKE_PROJECTS_PATH` | `/projects` | Path appended to base URL |
| `POLL_INTERVAL_SECONDS` | `60` | How often to check for new projects |
| `NOTIFICATION_DURATION_SECONDS` | `10` | How long each toast stays visible |
| `STATE_FILE_PATH` | `state/seen_projects.json` | Where to store seen-project IDs |
| `LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `LOG_FILE_PATH` | `logs/watcher.log` | Path to rotating log file |
| `LOG_MAX_BYTES` | `10485760` | Max log file size before rotation (10 MB) |
| `LOG_BACKUP_COUNT` | `5` | Number of rotated log files to keep |
| `BROWSER_HEADLESS` | `true` | Run browser in headless mode |
| `BROWSER_TIMEOUT_MS` | `30000` | Page-load timeout in milliseconds |

---

## Usage

```bash
# Start the watcher with default settings
handshake-watcher start

# Run with verbose debug logging
handshake-watcher start --log-level DEBUG

# Show current configuration (without secrets)
handshake-watcher config show

# Clear the seen-projects state (will re-notify for all current projects)
handshake-watcher state clear

# Show version
handshake-watcher --version
```

---

## Development

### Set up pre-commit hooks

```bash
pip install pre-commit
pre-commit install
```

### Run linters manually

```bash
ruff check .          # Linting
black --check .        # Formatting check
mypy src/              # Type checking
```

### Auto-fix formatting

```bash
black .
ruff check --fix .
isort .
```

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=handshake_watcher --cov-report=term-missing

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Make your changes and ensure all tests pass.
4. Run pre-commit hooks: `pre-commit run --all-files`.
5. Open a pull request.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
