# Contributing to Symposium

Thank you for your interest in contributing to the Symposium package! This document provides guidelines for contributing code, documentation, and improvements.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)
- Git

### Setup

```bash
# Clone repository
git clone https://github.com/ActiveInferenceInstitute/symposium.git
cd symposium

# Create virtual environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install development dependencies
uv pip install -e ".[dev]"

# Setup pre-commit hooks (optional)
pre-commit install
```

## Code Standards

### Python Style

- **PEP 8**: Follow Python style guidelines
- **Type Hints**: Use typing module for all functions
- **Docstrings**: Google-style docstrings for all public functions
- **Line Length**: 100 characters maximum
- **Imports**: Group standard library, third-party, local imports

### Code Formatting

```bash
# Format code
black src/ tests/

# Check linting
ruff check src/ tests/

# Type checking
mypy src/
```

### Documentation

- **README.md**: Required in every module (overview, usage, integration)
- **AGENTS.md**: Required in every module (AI agents and their roles)
- **Docstrings**: Complete parameter and return documentation
- **Comments**: Complex logic explained, TODO/FIXME tracked

## Testing

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_core/test_api.py

# With coverage
pytest --cov=src/symposium --cov-report=html
```

### Test Standards

- **Unit Tests**: All functions have corresponding tests
- **Integration Tests**: End-to-end workflow validation
- **Coverage**: > 90% overall, > 95% critical paths
- **Real API Tests**: Optional, skip if API keys not available

### Writing Tests

- Place tests in `tests/` mirroring source structure
- Use descriptive test names: `test_function_name_scenario`
- Use fixtures from `conftest.py` for common setup
- Mock external dependencies (APIs, file I/O)

## Development Workflow

### Branch Strategy

1. Create a feature branch from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make changes following code standards
3. Write/update tests
4. Run tests and linting
5. Update documentation
6. Commit with clear messages

### Commit Messages

Use clear, descriptive commit messages:

```
feat: Add new visualization method for CSV data
fix: Correct token counting in API client
docs: Update user guide with new CLI commands
test: Add integration tests for participant analysis
```

### Pull Request Process

1. **Before Submitting**:
   - Ensure all tests pass
   - Run linting and formatting
   - Update documentation
   - Check coverage hasn't decreased

2. **PR Description**:
   - What changes were made
   - Why the changes were needed
   - How to test the changes
   - Any breaking changes

3. **Review Process**:
   - At least one approval required
   - All CI checks must pass
   - Address review comments

## Module Structure

### Adding a New Module

1. Create module directory in `src/symposium/`
2. Add `__init__.py` with proper exports
3. Create `README.md` with overview and usage
4. Create `AGENTS.md` describing AI agent roles
5. Add tests in `tests/test_<module>/`
6. Update main `README.md` if needed

### Module Components

Each module should have:
- **`__init__.py`**: Exports public API
- **`README.md`**: Module documentation
- **`AGENTS.md`**: AI agent documentation
- **Source files**: One class per file, related functions grouped

## Specific Guidelines

### API Integration

- Use `APIClient` from `symposium.core.api`
- Implement retry logic with exponential backoff
- Handle token limits gracefully
- Provide clear error messages

### Data Processing

- Validate input data
- Handle missing values gracefully
- Use type hints for data structures
- Document data formats

### Error Handling

- Use specific exception types
- Provide helpful error messages
- Log errors appropriately
- Handle edge cases

### Performance

- Use efficient algorithms
- Optimize for large datasets
- Consider memory usage
- Profile if needed

## Areas for Contribution

### High Priority

- **Test Coverage**: Increase coverage, especially for visualization and CLI modules
- **Documentation**: Expand user guides and API documentation
- **Error Handling**: Improve error messages and recovery
- **Performance**: Optimize data processing and API calls

### Features

- **New Visualizations**: Additional plot types and methods
- **API Providers**: Support for additional LLM providers
- **Data Formats**: Support for additional input formats
- **CLI Enhancements**: New commands and options

### Maintenance

- **Code Quality**: Refactoring and improvements
- **Dependencies**: Keep dependencies up to date
- **Bug Fixes**: Fix reported issues
- **Testing**: Improve test coverage and reliability

## Questions?

- **Issues**: [GitHub Issues](https://github.com/ActiveInferenceInstitute/symposium/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ActiveInferenceInstitute/symposium/discussions)
- **Email**: [contact@activeinference.institute](mailto:contact@activeinference.institute)

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on technical merit
- Welcome newcomers

Thank you for contributing to Symposium!

