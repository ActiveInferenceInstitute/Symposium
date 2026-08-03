# Symposium 2025 - UV Setup Guide

## Quick Start with UV

The Symposium package uses [uv](https://github.com/astral-sh/uv) for fast, reliable dependency management.

### 1. Install UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using Homebrew
brew install uv

# Or using pip
pip install uv
```

### 2. Run Symposium

```bash
# The simplest way - everything is automated
./symposium.sh
```

The script will:
- ✅ Check if uv is installed
- ✅ Create a virtual environment (`.venv`)
- ✅ Install all dependencies
- ✅ Check for `.env` file
- ✅ Launch the interactive interface

### 3. Manual Setup (Optional)

If you prefer manual control:

```bash
# Create virtual environment
uv venv

# Install package and dependencies
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate  # On Windows

uv pip install -e .

# Run the application
python run.py
```

## Environment Configuration

Create a `.env` file with your API keys:

```bash
# Copy the example
cp .env.example .env

# Edit with your keys
nano .env
```

Required keys:
```
PERPLEXITY_API_KEY=your_perplexity_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
```

## Running Tests

```bash
# Activate the virtual environment
source .venv/bin/activate

# Run all tests
pytest tests/test_2025_participants.py -v

# Run with coverage
pytest tests/test_2025_participants.py --cov=src/symposium --cov-report=html

# Run specific test class
pytest tests/test_2025_participants.py::TestDataLoading -v
```

## UV Commands Reference

### Package Management

```bash
# Install dependencies
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"

# Update dependencies
uv pip install --upgrade -e .

# List installed packages
uv pip list

# Show package info
uv pip show symposium
```

### Virtual Environment

```bash
# Create new venv
uv venv

# Create with specific Python version
uv venv --python 3.12

# Remove and recreate
uv venv --clear

# Show venv info
uv venv --help
```

### Running Commands

```bash
# Run Python in the venv
uv run python script.py

# Run pytest
uv run pytest

# Run with specific Python version
uv run --python 3.12 python script.py
```

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError`:

```bash
# Reinstall the package
uv pip install -e . --force-reinstall

# Or clear cache and reinstall
rm -rf .venv
uv venv
uv pip install -e .
```

### UV Not Found

```bash
# Check if uv is in PATH
which uv

# Add to PATH if needed (add to ~/.zshrc or ~/.bashrc)
export PATH="$HOME/.cargo/bin:$PATH"

# Reload shell
source ~/.zshrc  # or ~/.bashrc
```

### Permission Issues

```bash
# Make symposium.sh executable
chmod +x symposium.sh

# If still issues, run directly
bash symposium.sh
```

### API Key Issues

```bash
# Check if .env file exists
ls -la .env

# Verify keys are loaded
source .venv/bin/activate
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Perplexity:', bool(os.getenv('PERPLEXITY_API_KEY'))); print('OpenRouter:', bool(os.getenv('OPENROUTER_API_KEY')))"
```

## Why UV?

- **⚡ Fast**: 10-100x faster than pip
- **🔒 Reliable**: Deterministic dependency resolution
- **🎯 Simple**: Single tool for venv + package management
- **🔄 Compatible**: Works with pip, pyproject.toml, requirements.txt
- **🐍 Flexible**: Manages multiple Python versions

## Development Workflow

```bash
# 1. Setup (one time)
uv venv
uv pip install -e ".[dev]"

# 2. Activate environment
source .venv/bin/activate

# 3. Make changes to code

# 4. Run tests
pytest tests/test_2025_participants.py -v

# 5. Run the application
python run.py
# OR
./symposium.sh
```

## CI/CD with UV

The repository's CI workflow (`.github/workflows/ci.yml`, workflow name `Tests`) runs
on every push to `main` and on pull requests:

```yaml
name: Tests
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: |
          uv venv
          uv pip install -e ".[dev]"
      - name: Lint (ruff check)
        run: uv run ruff check src/ tests/
      - name: Format (ruff format --check)
        run: uv run ruff format --check src/ tests/
      - name: Test (pytest + coverage gate)
        run: uv run python -m pytest --no-header
```

## Comparison: UV vs Traditional Methods

| Task | Traditional | UV |
|------|------------|-----|
| Create venv | `python -m venv .venv` | `uv venv` |
| Activate | `source .venv/bin/activate` | Same |
| Install deps | `pip install -e .` | `uv pip install -e .` |
| Run script | `python script.py` | `uv run python script.py` |
| Speed | ~30 seconds | ~3 seconds |

## Directory Structure

```
symposium/
├── .venv/              # UV-managed virtual environment
├── symposium.sh        # Automated setup and launcher
├── run.py              # Main application (simplified, no auto-install)
├── pyproject.toml      # UV reads this for dependencies
├── .env                # API keys (create from .env.example)
├── src/
│   └── symposium/      # Package source code
├── tests/              # Test suite
├── data/               # Input data
└── outputs/            # Generated reports
```

## Additional Resources

- UV Documentation: https://github.com/astral-sh/uv
- Python Packaging Guide: https://packaging.python.org/
- Symposium Documentation: ./docs/

## Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Ensure UV is up to date: `uv self update`
3. Try recreating the venv: `rm -rf .venv && uv venv && uv pip install -e .`
4. Check the logs in `symposium.log`
5. Run system component tests: Option 8 in the menu

---

**Quick Command Reference:**

```bash
# Setup and run
./symposium.sh

# Development
uv venv && uv pip install -e ".[dev]"
source .venv/bin/activate
pytest tests/test_2025_participants.py -v

# Update UV
uv self update

# Clean install
rm -rf .venv && uv venv && uv pip install -e .
```



