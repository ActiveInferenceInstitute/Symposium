# Symposium: Active Inference Symposium Research Tools

[![Tests](https://github.com/ActiveInferenceInstitute/symposium/workflows/Tests/badge.svg)](https://github.com/ActiveInferenceInstitute/symposium/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Research analysis and project generation tools for the Active Inference Symposium

## Overview

Symposium is a comprehensive Python package designed to facilitate research analysis, participant profiling, and project proposal generation for the [Active Inference Symposium](https://symposium.activeinference.institute/). The package provides modular tools for:

- **Research Analysis**: Automated analysis of presenter publications and research profiles
- **Participant Profiling**: Comprehensive participant profiling based on registration data
- **Profile Generation**: Research profile and methods documentation
- **Project Proposals**: Structured proposal generation using catechism templates
- **Collaboration Matching**: Identifying synergies and collaboration opportunities

## Features

- 🔬 **Multi-Provider LLM Support**: Unified interface for Perplexity and OpenRouter APIs
- 📊 **Data Processing**: OpenAlex publication data analysis with token-aware handling
- 📝 **Structured Outputs**: Dual format reports (Markdown + JSON)
- 🎯 **Flexible Configuration**: Environment-based and file-based configuration
- 🧪 **Well-Tested**: Test suite at ~86% coverage (regression gate `--cov-fail-under=80`); live-LLM tests are opt-in via the `real_api` marker
- 🚀 **Modern Tooling**: Built with uv, pytest, and ruff

## Quick Start

### Installation

Install using [uv](https://docs.astral.sh/uv/) (recommended):

```bash
# Clone repository
git clone https://github.com/ActiveInferenceInstitute/symposium.git
cd symposium

# Install with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Interactive Interface

The easiest way to use Symposium is through the interactive interface. The
[`symposium.sh`](symposium.sh) launcher checks for uv, creates a virtual environment,
installs the package, and starts the interface:

```bash
./symposium.sh
```

To run the interface directly (requires the package to be installed):

```bash
python run.py
```

The interactive interface provides numbered options for:
1. **📊 List Available Data** - Explore research datasets
2. **🎯 Analyze 2025 Participants (Complete Analysis)** - Full participant analysis with background research and curricula
3. **📊 Generate Column Summaries & Word Clouds** - Statistical analysis of participant responses
4. **🔍 Background Research (Single Participant)** - Use Perplexity for individual researcher analysis
5. **📚 Personalized Curriculum (Single Participant)** - Generate learning curriculum for one participant
6. **🌐 Create Visualizations** - Generate network, embedding, and distribution plots from Markdown reports
7. **🔧 Configuration Management** - Setup API keys and settings
8. **🧪 Test System Components** - Validate system functionality
9. **🚪 Exit** - Close the interface

#### Advanced Features
- **🎯 Batch Generation**: CLI commands for complete pipelines (profiles → proposals → visualizations)
- **🌐 All Visualizations**: `symposium visualize all` creates embeddings, networks, and distributions in one command from a directory of Markdown reports
- **📊 CSV Word Clouds & Summaries**: Column summaries and per-question word clouds from the participant CSV via `run.py` option 3
- **🧮 Advanced Methods**: 7 dimension reduction methods (PCA, LSA, t-SNE, UMAP, Isomap, NMF, LDA)
- **🔧 Smart Configuration**: Automatic virtual environment detection and activation
- **📝 Comprehensive Logging**: Real-time progress tracking with file persistence
- **🛡️ Error Recovery**: Robust error handling with clear user guidance, including PaymentRequiredError detection for API payment issues

### Command Line Interface

Alternatively, use the CLI directly:

#### Visualization Commands

**From Markdown Files:**
```bash
# Create embedding visualizations (PCA, LSA, t-SNE)
symposium visualize embeddings --input-dir <dir> --output-dir <dir> --method pca

# Create network visualizations (similarity networks, community analysis)
symposium visualize networks --input-dir <dir> --output-dir <dir> --layout spring

# Create distribution plots (document length, TF-IDF distributions)
symposium visualize distributions --input-dir <dir> --output-dir <dir>

# Create all visualizations at once
symposium visualize all --input-dir <dir> --output-dir <dir> --method pca --layout spring
```

**Note on input:** the `visualize` subcommands read **Markdown** documents from a directory (`--input-dir`); they do **not** accept a CSV file. Participant CSV data (e.g. `data/inputs/aif_2025/Public_Participant_Information.csv`) feeds the `analyze`/`generate` flows, which produce the Markdown reports you then visualize. Point `--input-dir` at a directory tree of `.md` files — for per-participant labelling, group the reports under `people/<participant>/` subdirectories:

```bash
# Create embedding visualizations (PCA, LSA, t-SNE) from a directory of Markdown reports
symposium visualize embeddings --input-dir outputs/2025_symposium/people --output-dir outputs/visualizations --method pca

# Create network visualizations (similarity networks, community analysis)
symposium visualize networks --input-dir outputs/2025_symposium/people --output-dir outputs/visualizations --layout spring

# Create distribution plots (document length, TF-IDF distributions)
symposium visualize distributions --input-dir outputs/2025_symposium/people --output-dir outputs/visualizations

# Create all visualizations at once
symposium visualize all --input-dir outputs/2025_symposium/people --output-dir outputs/visualizations --method pca --layout spring
```

**Generated Visualizations:**
- **📊 PCA/LSA/t-SNE Embeddings**: 2D and 3D dimension reduction plots
- **☁️ Word Clouds**: Term frequency visualization
- **📈 Term Frequency**: Distribution of terms across documents
- **🌐 Similarity Networks**: Document similarity networks with community detection
- **📋 Community Analysis**: Network community structure visualization
- **📊 Document Length Distributions**: Statistical analysis of text lengths

### Configuration

Create a `.env` file with your API keys:

```bash
PERPLEXITY_API_KEY=your_perplexity_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
```

**API Models:**
- **Perplexity**: `sonar` (search-enhanced responses)
- **OpenRouter**: `anthropic/claude-3.5-sonnet` (advanced reasoning)

**Error Handling:**
- Payment errors (402) are detected immediately and processing stops with clear guidance
- Other errors allow graceful degradation and continue processing
- See [API Guide](docs/api_guide.md) for detailed error handling documentation

### Setup Validation

Run the setup script to validate your environment:

```bash
python setup.py
```

This will check:
- Python version and dependencies
- API key configuration
- Data directory structure
- Package installation
- API connectivity

> **Note:** `setup.py` is the legacy validation script; `launch.py` and `symposium.sh`
> perform their own in-process validation and no longer call it.

### Interactive Launcher

For the easiest experience, use the launcher script:

```bash
python launch.py
```

This provides:
- **Automatic virtual environment activation**
- **Comprehensive logging** to both console and file
- **Setup validation** (package import check)
- **Interactive text interface** with 9 numbered options
- **Guided workflow** for all symposium operations
- **Error handling** and user guidance
- **Real-time progress tracking**

#### Logging Features
- Console logging with timestamps and levels
- File logging to `symposium.log` and `setup.log`
- Detailed import and configuration tracking
- API connectivity monitoring
- Error tracking with stack traces

#### Virtual Environment Management
- Automatic detection and activation
- Graceful fallback if not in virtual environment
- Clear error messages and setup instructions
- Cross-platform compatibility

### Basic Usage

#### Analyze Presenter Research Profiles

```bash
symposium analyze presenters \
  --data-dir data/inputs/aif_2025/ \
  --output-dir outputs/profiles/ \
  --domain-file data/domains/active_inference.md
```

#### Generate Research Profiles and Methods

```bash
symposium generate profiles \
  --data-dir data/inputs/aif_2025/ \
  --output-dir outputs/profiles/ \
  --include-methods
```

#### Generate Project Proposals

```bash
symposium generate projects \
  --profiles-dir outputs/profiles/ \
  --output-dir outputs/projects/ \
  --domain-file data/domains/active_inference.md \
  --catechism KarmaGAP \
  --collaborators-file data/collaborators.md
```

**Note on inputs:** `--domain-file` and `--collaborators-file` point at files **you
provide** — the package does not ship domain or collaborator content. Create the
directory and file, e.g.:

```bash
mkdir -p data/domains
# data/domains/active_inference.md: domain context passed to the LLM prompts
# data/collaborators.md: optional list of potential collaborators
```

See [Creating Domain Context](docs/user_guide.md#custom-domain-knowledge) for the
expected format.

### Python API

```python
from symposium.core.api import APIClient, PaymentRequiredError
from symposium.core.config import Config
from symposium.analysis.presenters import PresenterAnalyzer
from pathlib import Path

# Initialize
config = Config()
api_client = APIClient.create("perplexity")

# Analyze presenters with error handling
try:
    analyzer = PresenterAnalyzer(api_client)
    results = analyzer.analyze_all_presenters(
        data_path=Path("data/inputs/aif_2025"),
        output_dir=Path("outputs/profiles")
    )
except PaymentRequiredError as e:
    print(f"Payment required: {e.message}")
    # User needs to add credits before continuing
```

## Documentation

- [Documentation Index](docs/README.md) — overview of every guide in `docs/`
- [Installation Guide](docs/installation.md) — environment setup with uv
- [User Guide](docs/user_guide.md) — end-to-end usage (analysis, generation, visualization)
- [API Guide](docs/api_guide.md) — LLM providers, configuration, error handling
- [API Usage](docs/api_usage.md) — provider roles (Perplexity vs OpenRouter) in the 2025 workflow
- [CSV Visualization Guide](docs/csv_visualization_guide.md) — word clouds, embeddings, networks, distributions
- [Perplexity Research](docs/perplexity_research.md) — web-research integration for participant backgrounds
- [Architecture Overview](docs/architecture.md) — system design and module dependencies
- [Development Guide](docs/development.md) — contributing, testing, and code standards
- [Migration Guide](docs/migration.md) — upgrading from v1.x
- [UV Setup](UV_SETUP.md) — uv-based setup and commands
- [AI Agents Overview](AGENTS.md) — all AI agents in the system

## Project Structure

```
symposium/
├── src/symposium/          # Main package
│   ├── core/              # Core functionality (API, config, logging)
│   ├── analysis/          # Analysis modules
│   ├── generation/        # Content generation
│   ├── io/                # Input/output operations
│   ├── visualization/     # Visualization tools
│   ├── cli/               # Command-line interfaces
│   └── calendar/          # Calendar export functionality
├── tests/                 # Test suite
├── data/                  # Data and templates
│   ├── inputs/           # Input data (OpenAlex, registrations)
│   ├── catechisms/       # Proposal templates (KarmaGAP, EUGrants, Synthetic)
│   ├── domains/          # Domain knowledge files (user-provided)
│   ├── prompts/          # System prompts
│   └── templates/        # Data structure templates
├── docs/                  # Documentation (see docs/README.md)
├── outputs/              # Generated reports and visualizations (example outputs tracked)
├── run.py                # Interactive interface
├── launch.py             # Launcher (venv check + interface)
├── setup.py              # Legacy environment validation script
└── symposium.sh          # uv-based install-and-run script
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=src/symposium --cov-report=html

# Run linting
ruff check src/ tests/

# Format code
ruff format src/ tests/
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_core/test_api.py

# With coverage
pytest --cov=src/symposium --cov-report=term --cov-report=html

# Live-LLM tests are opt-in (require API keys):
pytest -m real_api
```

## Migration from v1.x

The 2.0 release represents a comprehensive refactor. See [migration.md](docs/migration.md) for detailed migration instructions.

Key changes:
- Unified API client interface
- Modular package structure
- Configuration management
- CLI commands replace numbered scripts
- Data reorganization

## Contributing

We welcome contributions! Please see [contributing.md](docs/contributing.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this software in your research, please cite:

```bibtex
@software{symposium2025,
  title = {Symposium: Research Analysis Tools for Active Inference Symposium},
  author = {Active Inference Institute},
  year = {2025},
  url = {https://github.com/ActiveInferenceInstitute/symposium}
}
```

## Acknowledgments

- [Active Inference Institute](https://activeinference.institute/)
- [OpenAlex](https://openalex.org/) for publication data
- [Perplexity AI](https://www.perplexity.ai/) and [OpenRouter](https://openrouter.ai/) for LLM access

## Support

- [Submit Issues](https://github.com/ActiveInferenceInstitute/symposium/issues)
- [Discussions](https://github.com/ActiveInferenceInstitute/symposium/discussions)
- Email: [contact@activeinference.institute](mailto:contact@activeinference.institute)

## Roadmap

- [ ] Real-time analysis updates
- [ ] Interactive visualization dashboard
- [ ] Multi-symposium support
- [ ] Enhanced collaboration matching
- [ ] Impact tracking and analytics

---

**Prepared for the 2025 Active Inference Symposium**
