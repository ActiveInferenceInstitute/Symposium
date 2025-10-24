# Installation Guide

## Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager

## Installing uv

### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/ActiveInferenceInstitute/symposium.git
cd symposium
```

### 2. Create Virtual Environment with uv

```bash
uv venv
```

### 3. Activate Virtual Environment

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```powershell
.venv\Scripts\activate
```

### 4. Install Package

**For users:**
```bash
uv pip install -e .
```

**For developers:**
```bash
uv pip install -e ".[dev]"
```

### 5. Configure API Keys

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
PERPLEXITY_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
API_PROVIDER=perplexity
```

### 6. Verify Installation

```bash
# Check CLI is available
symposium --help

# Run tests (developers only)
pytest

# Check imports work
python -c "from symposium.core.api import APIClient; print('✅ Import successful')"
```

## Quick Test

Create a test script `test_install.py`:

```python
from symposium.core.api import APIClient
from symposium.core.config import Config

# Initialize configuration
config = Config()
print(f"✅ Config loaded: API provider = {config.get('api.provider')}")

# Test API client creation (without calling API)
try:
    # This will fail if no API key, which is expected
    client = APIClient.create("perplexity", api_key="test")
    print("✅ API client created successfully")
except Exception as e:
    print(f"✅ API client creation works (key validation: {type(e).__name__})")

print("\n🎉 Installation successful!")
```

Run it:
```bash
python test_install.py
```

## Troubleshooting

### Issue: "Module 'symposium' not found"

**Solution:** Make sure you're in the virtual environment and have installed the package:
```bash
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e .
```

### Issue: "API key not found"

**Solution:** Create and configure `.env` file:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Issue: "uv: command not found"

**Solution:** Install uv following the instructions above, then restart your terminal.

### Issue: Python version mismatch

**Solution:** The package requires Python 3.10+. Check your version:
```bash
python3 --version
```

If needed, use uv to install the correct Python version:
```bash
uv python install 3.10
uv python pin 3.10
```

## Development Setup

For contributors and developers:

```bash
# Clone and enter directory
git clone https://github.com/ActiveInferenceInstitute/symposium.git
cd symposium

# Setup with uv
uv venv
source .venv/bin/activate

# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src/ tests/
black --check src/ tests/

# Format code
black src/ tests/

# Run type checking
mypy src/symposium --ignore-missing-imports
```

## Updating

To update to the latest version:

```bash
cd symposium
git pull origin main
uv pip install -e ".[dev]"
```

## Uninstallation

```bash
# Remove virtual environment
rm -rf .venv

# Or uninstall package only
uv pip uninstall symposium
```

## Next Steps

After installation, see:
- [User Guide](user_guide.md) for usage instructions
- [API Guide](api_guide.md) for API configuration
- [Development Guide](development.md) for contributing

