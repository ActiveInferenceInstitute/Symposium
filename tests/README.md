# Test Suite

Comprehensive testing infrastructure for the Symposium package.

## Overview

This test suite provides complete coverage of all Symposium functionality, ensuring reliability, correctness, and maintainability of the entire system.

## Test Structure

### Core Tests (`test_core/`)
Tests for fundamental infrastructure components:
- **API Tests**: LLM provider integration testing
- **Configuration Tests**: Settings and environment management
- **Data Loading Tests**: File I/O and data processing validation

### Analysis Tests (`test_analysis/`)
Tests for research analysis functionality:
- **Presenter Tests**: Research profile analysis validation
- **Participant Tests**: Learning and development analysis testing

### Generation Tests (`test_generation/`)
Tests for content generation capabilities:
- **Profile Tests**: Research profile generation validation
- **Project Tests**: Project proposal generation testing

### Integration Tests (`test_integration/`)
End-to-end workflow testing:
- **Workflow Tests**: Complete pipeline validation
- **Real API Tests**: Live system integration testing

### I/O Tests (`test_io/`)
Input/output operation testing:
- **Reader Tests**: File reading functionality
- **Writer Tests**: Report generation validation

### Visualization Tests (`test_visualization/`)
Visualization and plotting testing:
- **Embedding Tests**: Dimension reduction validation
- **Network Tests**: Similarity network testing
- **Distribution Tests**: Statistical plotting validation

## Test Categories

### Unit Tests
Individual component testing:
- Function-level validation
- Mock-based isolation testing
- Edge case coverage
- Error condition testing

### Integration Tests
Component interaction testing:
- API integration validation
- Data flow verification
- Configuration interaction testing
- Cross-module functionality

### Real API Tests
Live system integration testing:
- Actual LLM API interaction
- Real data processing
- Performance validation
- Error recovery testing

## Test Data

### Mock Data
- Simulated research profiles
- Test configuration files
- Sample participant data
- Mock API responses

### Real Data
- Actual research datasets
- Live API connections
- Production configuration
- Real-world scenarios

## Running Tests

### All Tests
```bash
# Run complete test suite
pytest tests/

# With coverage report
pytest tests/ --cov=src/symposium --cov-report=html

# Verbose output
pytest tests/ -v
```

### Specific Test Categories
```bash
# Core functionality only
pytest tests/test_core/ -v

# Analysis module only
pytest tests/test_analysis/ -v

# Real API integration (requires API keys)
pytest tests/test_integration/test_workflows.py::TestRealAPIWorkflows -v
```

### Performance Testing
```bash
# Quick tests only
pytest tests/test_core/ -q

# Skip slow integration tests
pytest tests/ --ignore=tests/test_integration/test_workflows.py
```

## Test Configuration

### Environment Setup
```bash
# Install test dependencies
uv pip install -e ".[dev]"

# Set test environment variables
export TEST_API_KEY="test_key"
export TEST_PROVIDER="perplexity"
```

### Test Data Management
- Test fixtures in `conftest.py`
- Mock data in `tests/fixtures/`
- Temporary directories for I/O tests
- Cleanup after test completion

## Quality Metrics

### Coverage Goals
- **Overall Coverage**: > 90%
- **Core Modules**: > 95%
- **Critical Paths**: 100%
- **Error Paths**: 100%

### Test Reliability
- **Pass Rate**: > 99%
- **Flaky Tests**: < 1%
- **False Positives**: 0%
- **False Negatives**: < 1%

## Continuous Integration

### GitHub Actions
- Automated testing on push/PR
- Multiple Python versions (3.9, 3.10, 3.11)
- Cross-platform testing (Linux, macOS, Windows)
- Coverage reporting and badges

### Quality Gates
- All tests must pass
- Minimum coverage thresholds
- No critical security issues
- Performance benchmarks met

## Integration

This test suite validates:
- `symposium.core` - API, configuration, data loading
- `symposium.analysis` - Research analysis functionality
- `symposium.generation` - Content generation capabilities
- `symposium.io` - File I/O operations
- `symposium.cli` - Command-line interface
- `symposium.visualization` - Data visualization tools
