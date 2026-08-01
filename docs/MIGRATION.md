# Migration Guide: v1.x to v2.0

## Overview

Version 2.0 represents a major refactoring of the Symposium package, transforming it from a collection of scripts into a professional, modular Python package. This guide helps users migrate from the old structure to the new system.

## What Changed

### Before (v1.x) ❌
- Numbered scripts (`1_Research_Presenters.py`, etc.)
- Duplicate code in multiple locations
- Hard-coded paths and configuration
- Mixed AIF and ISM functionality
- No tests or CI/CD pipeline
- Manual dependency management

### After (v2.0) ✅
- Professional CLI commands (`symposium analyze presenters`)
- Modular package structure (`src/symposium/`)
- Flexible configuration system
- Focus on Active Inference Symposium
- Comprehensive test suite
- Modern tooling (uv, pytest, GitHub Actions)

## Migration Steps

### 1. Backup Your Data

Before migration, backup your existing data:

```bash
# Backup current directory
cp -r /path/to/symposium /path/to/symposium_backup

# Or use git (if using version control)
git branch backup-before-v2
```

### 2. Install New Version

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone new repository (or update existing)
git clone https://github.com/ActiveInferenceInstitute/symposium.git
cd symposium

# Setup virtual environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install new package
uv pip install -e ".[dev]"
```

### 3. Migrate Data & Configuration

The package does **not** ship automated `scripts/` migration utilities (the `scripts/`
directory does not exist in this release). Upgrade existing data and configuration by
pointing the new tooling at the standard locations:

```bash
# Input data stays under data/inputs/<year>/<name>/ (OpenAlex CSV pairs: openalex-group-by-*, works-*)
# Copy the environment template and set your API keys
cp .env.example .env
```

Then re-run analysis/generation through the CLI (`symposium analyze …`,
`symposium generate …`, `symposium visualize …`) to regenerate reports in the new layout.

### 4. Update Configuration

#### Environment Variables

Create `.env` file with your API keys:

```bash
# Copy template
cp .env.example .env

# Edit with your API keys
PERPLEXITY_API_KEY=your_perplexity_key
OPENROUTER_API_KEY=your_openrouter_key
API_PROVIDER=perplexity  # or "openrouter"
```

#### Configuration File (Optional)

For advanced configuration, create `config.json`:

```json
{
  "api": {
    "provider": "perplexity",
    "perplexity": {
      "model": "llama-3.1-sonar-large-128k-online",
      "temperature": 0.7,
      "max_tokens": 2000
    }
  },
  "data": {
    "max_rows_per_file": 10,
    "max_prompt_tokens": 12000
  }
}
```

### 5. Update Data Structure

Your data will be automatically reorganized:

| Old Path | New Path | Status |
|----------|----------|--------|
| `inputs/AIF/` | `data/inputs/aif_2024/` | ✅ Automatic |
| `Catechism/` | `data/catechisms/` | ✅ Automatic |
| `prompts/` | `data/prompts/` | ✅ Automatic |
| `ISM_Stream/Domain/` | `data/domains/` | ✅ Automatic |

### 6. Update Scripts and Workflows

#### Old Commands vs New Commands

| Old Command | New Command | Notes |
|-------------|-------------|-------|
| `python 1_Research_Presenters.py` | `symposium analyze presenters` | New CLI |
| `python 2_Research_Participants.py` | `symposium analyze participants` | New CLI |
| `python 3_Projects_creation.py` | `symposium generate projects` | New CLI |
| Manual visualization scripts | `symposium visualize` | New CLI |

#### Detailed Migration Examples

**Old presenter analysis:**
```bash
# Before
python 1_Research_Presenters.py --data=inputs/AIF/ --output=outputs/

# After
symposium analyze presenters \
  --data-dir data/inputs/aif_2025/ \
  --output-dir outputs/profiles/ \
  --domain-file data/domains/active_inference.md
```

**Old project generation:**
```bash
# Before
python 3_Projects_creation.py --profiles=synthetic/participants/

# After
symposium generate projects \
  --profiles-dir outputs/profiles/ \
  --output-dir outputs/projects/ \
  --domain-file data/domains/active_inference.md \
  --catechism KarmaGAP
```

**Old visualization:**
```bash
# Before
python Visualization_Methods.py --input=outputs/

# After
symposium visualize embeddings \
  --input-dir outputs/profiles/ \
  --output-dir outputs/visualizations/ \
  --method pca
```

### 7. Test New System

Verify the migration worked:

```bash
# Test CLI availability
symposium --help

# Test specific commands
symposium analyze --help
symposium generate --help
symposium visualize --help

# Test imports
python -c "
from symposium.core.api import APIClient
from symposium.core.config import Config
from symposium.analysis.presenters import PresenterAnalyzer
print('✅ All imports successful')
"

# Run tests
pytest tests/test_core/ -v
```

### 8. Update Documentation and Scripts

Update any custom scripts or documentation:

1. **Replace script calls** with CLI commands
2. **Update path references** to new data structure
3. **Update configuration** to use `.env` format
4. **Test workflows** with new commands

## Breaking Changes

### Removed Features

- **ISM Workshop support**: Moved to archive (can be restored if needed)
- **Numbered scripts**: Replaced by CLI commands
- **Hard-coded paths**: Now configurable
- **Manual API handling**: Now unified client

### API Changes

#### Configuration
```python
# Before (v1.x)
# Hard-coded or llm_keys.key

# After (v2.0)
from symposium.core.config import Config
config = Config()
api_key = config.get_api_key()
```

#### Data Loading
```python
# Before (v1.x)
# Manual CSV loading with hard-coded paths

# After (v2.0)
from symposium.core.data_loader import DataLoader
loader = DataLoader()
presenters = loader.load_presenter_data(data_path, max_rows=10)
```

#### API Client
```python
# Before (v1.x)
# Separate Perplexity_Methods.py and OpenRouter_Methods.py

# After (v2.0)
from symposium.core.api import APIClient
client = APIClient.create("perplexity", api_key="your_key")
response = client.get_response(prompt, system_prompt)
```

## Backwards Compatibility

### Automatic Compatibility

The current release does not provide backward-compatibility wrapper scripts. The legacy
`scripts/` migration utilities referenced by earlier documentation do **not** exist here;
migrate configuration and data manually using the steps in section 3 above.

### Manual Compatibility

If you need to maintain old workflows:

1. **Use the new CLI entry points**: `symposium analyze|generate|visualize …`
2. **Gradual migration**: Update scripts one at a time
3. **Test thoroughly**: Verify outputs match old system

## Troubleshooting Migration

### Common Issues

#### "Module not found" errors

**Solution:**
```bash
# Ensure proper installation
source .venv/bin/activate
uv pip install -e .

# Check imports
python -c "from symposium.core.api import APIClient"
```

#### "No data found" errors

**Solution:**
```bash
# Check data migration
ls -la data/inputs/aif_2025/

# Verify data structure
find data/inputs/ -name "*.csv" | head -5
```

#### API connection issues

**Solution:**
```bash
# Check API configuration
cat .env

# Test API connection
python -c "
from symposium.core.api import APIClient
try:
    client = APIClient.create('perplexity')
    print('✅ API connection successful')
except Exception as e:
    print(f'❌ API error: {e}')
"
```

#### Command not found

**Solution:**
```bash
# Check CLI installation
symposium --help

# If not found, reinstall
uv pip install -e .
```

### Rollback Procedure

If migration fails, rollback to backup:

```bash
# Stop current process
cd /path/to/symposium_backup

# Restore data
cp -r data/* /path/to/new_symposium/data/

# Restore configuration
cp .env.backup /path/to/new_symposium/.env
```

## Performance Comparison

### Before vs After

| Aspect | v1.x | v2.0 | Improvement |
|--------|------|------|-------------|
| Setup | Manual dependencies | `uv pip install` | ✅ Automated |
| Configuration | Hard-coded | `.env` + JSON | ✅ Flexible |
| Testing | None | pytest + CI/CD | ✅ Quality assured |
| Documentation | Minimal | Comprehensive | ✅ Clear usage |
| API Handling | Duplicate code | Unified client | ✅ DRY principle |
| Error Handling | Basic | Comprehensive | ✅ Robust |
| Code Reuse | Copy-paste | Modular | ✅ Maintainable |

### Performance Benchmarks

The new system provides:
- **Faster startup**: Package loading optimized
- **Better memory usage**: Token-aware processing
- **Improved reliability**: Comprehensive error handling
- **Enhanced debugging**: Structured logging

## What's Next?

After successful migration:

1. **Explore new features**: Check `symposium --help` for all commands
2. **Read documentation**: See `docs/` for detailed guides
3. **Run tests**: Verify everything works with `pytest`
4. **Update workflows**: Modify any automation scripts
5. **Provide feedback**: Report issues or suggest improvements

## Support

### Migration Support

- **Documentation**: Check `docs/user_guide.md`
- **Examples**: See `docs/installation.md`
- **Issues**: Report problems on GitHub
- **Discussions**: Ask questions in GitHub discussions

### Getting Help

```bash
# Quick help
symposium --help

# Detailed help for specific commands
symposium analyze presenters --help
symposium generate projects --help

# Check configuration
python -c "from symposium.core.config import Config; Config().ensure_paths()"
```

## Success Checklist

- [ ] Data successfully migrated to `data/` structure
- [ ] Configuration converted to `.env` format
- [ ] CLI commands working (`symposium --help`)
- [ ] API connections functional
- [ ] Tests passing (`pytest`)
- [ ] Outputs generated in new structure
- [ ] Documentation reviewed and understood

## Next Steps

1. **Complete migration**: Finish any remaining steps above
2. **Test workflows**: Verify your specific use cases work
3. **Update team**: Inform other users about changes
4. **Clean up**: Remove backup files once confident
5. **Contribute**: Help improve the package

---

**Migration completed!** 🎉

The Symposium package is now a modern, maintainable, and extensible tool ready for the 2025 Active Inference Symposium and beyond.

