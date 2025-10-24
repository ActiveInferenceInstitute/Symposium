# Development Guide

## Overview

This guide provides instructions for developers contributing to the Symposium package. The package follows modern Python development practices with comprehensive testing, linting, and documentation.

## Development Setup

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- Git

### Initial Setup

```bash
# Clone repository
git clone https://github.com/ActiveInferenceInstitute/symposium.git
cd symposium

# Setup development environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install with development dependencies
uv pip install -e ".[dev]"

# Verify installation
python -c "from symposium.core.api import APIClient; print('✅ Import successful')"
```

### Configuration

#### Development Configuration

Copy and configure environment files:

```bash
# API keys for testing
cp .env.example .env
# Edit .env with your development API keys

# Optional: Create development config
cp config.example.json config.json
# Edit config.json for development settings
```

#### Testing Configuration

The package uses pytest with comprehensive fixtures:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/symposium --cov-report=html --cov-report=term

# Run specific test module
pytest tests/test_core/test_api.py -v

# Run integration tests
pytest tests/test_integration/ -v
```

## Code Organization

### Package Structure

```
src/symposium/
├── core/              # Core functionality
│   ├── api.py         # Unified API client
│   ├── config.py      # Configuration management
│   ├── data_loader.py # Data loading utilities
│   └── logging_utils.py # Logging setup
├── analysis/          # Analysis modules
│   ├── presenters.py  # Presenter analysis
│   └── participants.py # Participant analysis
├── generation/        # Content generation
│   ├── profiles.py    # Profile generation
│   └── projects.py    # Project generation
├── io/                # I/O operations
│   ├── readers.py     # File readers
│   └── writers.py     # Report writers
├── visualization/     # Visualization tools
│   ├── embeddings.py  # Dimension reduction
│   ├── networks.py    # Network analysis
│   └── distributions.py # Statistical plots
└── cli/               # Command-line interfaces
    ├── __init__.py    # Main CLI
    ├── analyze.py     # Analysis commands
    ├── generate.py    # Generation commands
    └── visualize.py   # Visualization commands
```

### Key Design Patterns

#### Factory Pattern (API Client)

```python
from symposium.core.api import APIClient

# Create provider instance
client = APIClient.create("perplexity", api_key="your_key")
response = client.get_response(prompt, system_prompt)
```

#### Strategy Pattern (API Providers)

```python
from symposium.core.api import BaseAPIProvider, PerplexityProvider, OpenRouterProvider

class CustomProvider(BaseAPIProvider):
    def get_response(self, prompt, system_prompt=None, **kwargs):
        # Custom implementation
        return self.custom_api_call(prompt)
```

#### Configuration Hierarchy

```python
from symposium.core.config import Config

config = Config()
value = config.get("api.provider")  # Dot notation access
config.set("data.max_rows", 20)     # Dot notation setting
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Implement Changes

Follow the existing code patterns:

- Add type hints to all functions
- Include comprehensive docstrings
- Handle errors gracefully
- Add logging for important operations
- Write tests for new functionality

### 3. Write Tests

#### Unit Tests

Create tests in `tests/test_module/`:

```python
# tests/test_analysis/test_presenters.py
import pytest
from symposium.analysis.presenters import PresenterAnalyzer

class TestPresenterAnalyzer:
    def test_analyze_presenter(self, mock_api_client, sample_presenter_data):
        # Test implementation
        pass
```

#### Integration Tests

Create end-to-end tests in `tests/test_integration/`:

```python
# tests/test_integration/test_workflows.py
def test_complete_workflow(self, temp_dir, mock_api_client):
    # Full workflow test
    pass
```

### 4. Run Tests and Linting

```bash
# Run tests with coverage
pytest --cov=src/symposium --cov-report=term

# Run linting
ruff check src/ tests/

# Format code
black src/ tests/

# Type checking
mypy src/symposium --ignore-missing-imports
```

### 5. Update Documentation

Update relevant documentation:

- `README.md` for new features
- `docs/user_guide.md` for usage examples
- `docs/api_guide.md` for API changes
- Add docstring examples to new functions

### 6. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add new analysis feature

- Add comprehensive presenter analysis
- Include token-aware processing
- Add unit tests with 95% coverage
- Update documentation"

# Push to branch
git push origin feature/your-feature-name
```

## Testing Guidelines

### Test Structure

```
tests/
├── conftest.py              # Global fixtures
├── test_core/               # Core module tests
│   ├── test_api.py
│   ├── test_config.py
│   └── test_data_loader.py
├── test_analysis/           # Analysis module tests
├── test_generation/         # Generation module tests
├── test_io/                 # I/O module tests
└── test_integration/        # End-to-end tests
```

### Fixtures

Use pytest fixtures for test data:

```python
# tests/conftest.py
@pytest.fixture
def sample_presenter_data():
    return {
        'name': 'Test Presenter',
        'topics': pd.DataFrame({'topic': ['AI'], 'count': [5]}),
        'works': pd.DataFrame({'title': ['Paper 1'], 'publication_year': [2023]})
    }
```

### Mock External Dependencies

```python
# Mock API calls
with patch.object(analyzer.api_client, 'get_response', return_value="Mock response"):
    result = analyzer.analyze_presenter(data)

# Mock file I/O
with patch('builtins.open', mock_open(read_data="test content")):
    content = ReportReader.read_markdown(file_path)
```

## Code Standards

### Style Guidelines

- **Line Length**: 100 characters
- **Type Hints**: Required for all public functions
- **Docstrings**: Google-style for modules, NumPy-style for functions
- **Imports**: Group by type (stdlib, third-party, local)
- **Naming**: snake_case for functions/variables, PascalCase for classes

### Error Handling

```python
def process_data(data: Dict[str, Any]) -> str:
    """Process data with proper error handling.

    Args:
        data: Input data dictionary

    Returns:
        Processed result

    Raises:
        ValueError: If data is invalid
        APIError: If external API fails
    """
    try:
        # Validate input
        if not data:
            raise ValueError("Data cannot be empty")

        # Process data
        result = self._process_internal(data)

        # Log success
        logger.info(f"Successfully processed {len(data)} items")

        return result

    except Exception as e:
        logger.error(f"Error processing data: {e}")
        raise
```

### Logging

Use structured logging:

```python
import logging

logger = logging.getLogger(__name__)

# Different log levels
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
```

## Adding New Features

### 1. Analysis Module

To add a new analysis type:

1. Create analyzer class in `src/symposium/analysis/`
2. Implement analysis logic
3. Add CLI command in `src/symposium/cli/analyze.py`
4. Write comprehensive tests
5. Update documentation

```python
# src/symposium/analysis/new_analysis.py
class NewAnalyzer:
    """New analysis functionality."""

    def __init__(self, api_client, config=None):
        self.api_client = api_client
        self.config = config or {}

    def analyze(self, data, **kwargs) -> str:
        """Perform analysis.

        Args:
            data: Input data
            **kwargs: Additional parameters

        Returns:
            Analysis result
        """
        # Implementation
        pass
```

### 2. CLI Command

```python
# src/symposium/cli/analyze.py
def analyze_new(args):
    """Analyze with new method."""
    # Implementation

# Add to main CLI
def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Add new command
    new_parser = subparsers.add_parser('new', help='New analysis')
    new_parser.set_defaults(func=analyze_new)
```

### 3. Configuration

```python
# Add new config options
config_dict = {
    'new_analysis': {
        'enabled': True,
        'threshold': 0.5,
        'max_items': 100
    }
}
```

## Performance Considerations

### Token Management

Always consider token limits:

```python
from symposium.core.data_loader import DataLoader

# Estimate token count
tokens = DataLoader.estimate_token_count(text)

# Truncate if needed
if tokens > max_tokens:
    text = DataLoader.truncate_to_tokens(text, max_tokens)
```

### Batch Processing

For large datasets:

```python
def process_batch(items: List[Any], batch_size: int = 10) -> List[str]:
    """Process items in batches."""
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = [process_item(item) for item in batch]
        results.extend(batch_results)

        # Add delay to avoid rate limits
        time.sleep(1)

    return results
```

### Memory Management

```python
# Use generators for large datasets
def load_large_dataset(filepath: Path):
    """Load dataset as generator."""
    with open(filepath) as f:
        for line in f:
            yield process_line(line)

# Process without loading everything into memory
for item in load_large_dataset(data_file):
    process_item(item)
```

## API Development

### Versioning

The package follows semantic versioning (MAJOR.MINOR.PATCH):

- **Major**: Breaking changes
- **Minor**: New features (backwards compatible)
- **Patch**: Bug fixes

### Deprecation

When deprecating features:

```python
import warnings

def old_function():
    warnings.warn(
        "old_function is deprecated, use new_function instead",
        DeprecationWarning,
        stacklevel=2
    )
    return new_function()
```

### Backwards Compatibility

For breaking changes, provide migration path:

```python
# Old interface (deprecated)
def old_analyze(data, output_path):
    # Implementation

# New interface (recommended)
def analyze_presenter(data, output_dir, **kwargs):
    # Implementation

# Bridge function
def analyze(data, output_path=None, output_dir=None, **kwargs):
    if output_path:
        warnings.warn("output_path deprecated, use output_dir")
        output_dir = output_path
    return analyze_presenter(data, output_dir, **kwargs)
```

## Documentation

### Docstring Standards

```python
def analyze_data(data: pd.DataFrame, threshold: float = 0.5) -> Dict[str, Any]:
    """Analyze data with configurable threshold.

    This function performs comprehensive analysis of the input data,
    applying statistical methods and generating insights.

    Args:
        data: Input DataFrame containing research data
        threshold: Similarity threshold for analysis (0.0 to 1.0)

    Returns:
        Dictionary containing analysis results with keys:
        - 'summary': Statistical summary
        - 'insights': Generated insights
        - 'recommendations': Actionable recommendations

    Raises:
        ValueError: If threshold is outside valid range
        TypeError: If data is not a DataFrame

    Examples:
        >>> data = pd.DataFrame({'col1': [1, 2, 3]})
        >>> result = analyze_data(data, threshold=0.7)
        >>> print(result['summary'])
        Statistical summary...
    """
    # Implementation
```

### API Documentation

For public APIs, ensure:

- Complete parameter documentation
- Return type specification
- Exception documentation
- Usage examples
- Type hints

## Contributing Workflow

### 1. Issue Tracking

- Check existing issues before creating new ones
- Use clear, descriptive titles
- Include reproduction steps for bugs
- Reference related issues/PRs

### 2. Pull Request Process

1. **Create branch**: `git checkout -b feature/your-feature`
2. **Implement**: Follow coding standards
3. **Test**: Add comprehensive tests
4. **Document**: Update documentation
5. **Review**: Request review from maintainers
6. **Merge**: Squash commits if needed

### 3. Code Review Checklist

- [ ] Type hints on all public functions
- [ ] Comprehensive docstrings
- [ ] Unit tests with good coverage
- [ ] Error handling and logging
- [ ] Follows existing patterns
- [ ] Documentation updated
- [ ] No linting errors
- [ ] Tests pass

## Continuous Integration

### GitHub Actions

The package uses GitHub Actions for:

- **Tests**: Multi-OS, multi-Python testing with coverage
- **Linting**: Code quality checks (ruff, black, mypy)
- **Documentation**: Build and validate docs

### Pre-commit Hooks

Install pre-commit for automatic checks:

```bash
pip install pre-commit
pre-commit install

# Manual run
pre-commit run --all-files
```

## Troubleshooting

### Common Development Issues

#### Import Errors

```bash
# Ensure you're in virtual environment
source .venv/bin/activate

# Reinstall package in development mode
uv pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Test Failures

```bash
# Run specific failing test
pytest tests/test_core/test_api.py::TestAPIClient::test_create_provider -v

# Debug with pdb
pytest --pdb tests/test_core/test_api.py::TestAPIClient::test_create_provider
```

#### Linting Issues

```bash
# Fix formatting
black src/ tests/

# Fix linting issues
ruff check src/ tests/ --fix

# Check types
mypy src/symposium
```

## Release Process

### 1. Version Update

Update version in `pyproject.toml`:

```toml
[project]
version = "2.1.0"  # Update version
```

### 2. Update Changelog

Add entry to CHANGELOG.md:

```markdown
## [2.1.0] - 2025-01-15

### Added
- New analysis feature
- Enhanced visualization options

### Changed
- Improved API client performance
- Updated configuration options

### Fixed
- Bug in data loading
- Memory leak in processing
```

### 3. Tag Release

```bash
git add .
git commit -m "Release v2.1.0"
git tag v2.1.0
git push origin main --tags
```

### 4. Build and Publish

```bash
# Build package
uv build

# Publish to PyPI (if maintainer)
uv publish
```

## Support

### Getting Help

1. **Documentation**: Check docs/ directory
2. **Issues**: Search existing GitHub issues
3. **Discussions**: Use GitHub discussions for questions
4. **Code Review**: Request review for PRs

### Reporting Bugs

Include in bug reports:
- Python version (`python --version`)
- Package version (`pip show symposium`)
- Error traceback
- Steps to reproduce
- Expected vs actual behavior

### Feature Requests

1. Create GitHub issue with "enhancement" label
2. Describe the feature and use case
3. Provide examples of how it would work
4. Consider implementation approach

## License and Attribution

This package is licensed under MIT License. When contributing:

- Ensure code follows license requirements
- Add attribution for external code
- Maintain copyright headers where appropriate
- Respect intellectual property

## Community Guidelines

- Be respectful and inclusive
- Use welcoming and inclusive language
- Be collaborative
- Focus on what is best for the community
- Show empathy towards other community members

---

**Happy coding!** 🎉

For questions or issues, please see the [main README](../README.md) or create a GitHub issue.

