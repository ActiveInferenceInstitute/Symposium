# User Guide

## Overview

This guide provides comprehensive instructions for using the Symposium v2.0 package for research analysis and project generation at the Active Inference Symposium.

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

### Quick Installation

```bash
# Clone repository
git clone https://github.com/ActiveInferenceInstitute/symposium.git
cd symposium

# Setup virtual environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install package
uv pip install -e ".[dev]"

# Configure API keys
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

#### Environment Variables

Create `.env` file with your API keys:

```bash
# Required: Choose one or both
PERPLEXITY_API_KEY=your_perplexity_key_here
OPENROUTER_API_KEY=your_openrouter_key_here

# Optional
API_PROVIDER=perplexity  # or "openrouter"
LOG_LEVEL=INFO
```

#### Configuration File

Optional `config.json` for advanced settings:

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

## Data Preparation

### Directory Structure

Organize your data in the `data/` directory:

```
data/
├── inputs/
│   ├── aif_2024/    # Historical symposium data
│   └── aif_2025/    # Current symposium data (create this)
├── catechisms/      # Proposal templates
├── domains/         # Domain knowledge files
└── prompts/         # System prompts
```

### Input Data Format

#### Presenter Data (OpenAlex CSV)

Each presenter should have a folder with two CSV files:

```
data/inputs/aif_2025/
├── Researcher_Name/
│   ├── openalex-group-by-*.csv  # Research topics and frequencies
│   └── works-*.csv              # Publications with citations
```

**Example CSV Structure:**
```csv
# openalex-group-by-*.csv
topic,count
Active Inference,15
Free Energy Principle,12
Bayesian Inference,8

# works-*.csv
title,publication_year,cited_by_count
Understanding Active Inference,2023,45
Free Energy in Practice,2022,32
```

#### Participant Registration

CSV file with participant information:

```csv
name,background,interests,experience
John Doe,PhD Computer Science,Active Inference,Intermediate
Jane Smith,Postdoc Neuroscience,Bayesian Methods,Expert
```

## CLI Usage

### Basic Commands

#### Analyze Presenters

```bash
symposium analyze presenters \
  --data-dir data/inputs/aif_2025/ \
  --output-dir outputs/profiles/ \
  --domain-file data/domains/active_inference.md \
  --max-rows 10
```

**Options:**
- `--data-dir`: Directory containing presenter folders
- `--output-dir`: Where to save analysis results
- `--domain-file`: Optional domain context file
- `--max-rows`: Max CSV rows per presenter (token management)
- `--api-provider`: Choose API (perplexity/openrouter)

#### Analyze Participants

```bash
symposium analyze participants \
  --registration-file data/participants.csv \
  --output-dir outputs/profiles/ \
  --domain-file data/domains/active_inference.md
```

#### Generate Research Profiles

```bash
symposium generate profiles \
  --data-dir data/inputs/aif_2025/ \
  --output-dir outputs/profiles/ \
  --include-methods \
  --domain-file data/domains/active_inference.md
```

**Options:**
- `--include-methods`: Generate research methods documentation

#### Generate Project Proposals

```bash
symposium generate projects \
  --profiles-dir outputs/profiles/ \
  --output-dir outputs/projects/ \
  --domain-file data/domains/active_inference.md \
  --catechism KarmaGAP \
  --collaborators-file data/collaborators.md
```

**Options:**
- `--catechism`: Template type (KarmaGAP, EUGrants, Synthetic)
- `--collaborators-file`: Optional collaborators list

#### Create Visualizations

```bash
# Embeddings and dimension reduction
symposium visualize embeddings \
  --input-dir outputs/profiles/ \
  --output-dir outputs/visualizations/ \
  --method pca \
  --n-components 2

# Similarity networks
symposium visualize networks \
  --input-dir outputs/profiles/ \
  --output-dir outputs/visualizations/ \
  --threshold 0.3

# Statistical distributions
symposium visualize distributions \
  --input-dir outputs/profiles/ \
  --output-dir outputs/visualizations/
```

## Python API

### Basic Usage

```python
from symposium.core.api import APIClient
from symposium.core.config import Config
from symposium.analysis.presenters import PresenterAnalyzer
from pathlib import Path

# Initialize configuration and API
config = Config()
api_client = APIClient.create(
    provider=config.get("api.provider"),
    api_key=config.get_api_key()
)

# Analyze presenters
analyzer = PresenterAnalyzer(api_client)
results = analyzer.analyze_all_presenters(
    data_path=Path("data/inputs/aif_2025"),
    output_dir=Path("outputs/profiles"),
    domain_context="Active Inference research context"
)
```

### Advanced Configuration

```python
from symposium.core.config import Config

# Load custom configuration
config = Config(config_file=Path("custom_config.json"))

# Override specific settings
config.set("api.perplexity.temperature", 0.5)
config.set("data.max_rows_per_file", 20)

# Ensure all paths exist
config.ensure_paths()
```

### Custom Analysis

```python
from symposium.analysis.presenters import PresenterAnalyzer
from symposium.generation.projects import ProjectGenerator

# Custom presenter analysis
analyzer = PresenterAnalyzer(api_client, custom_config)
custom_prompt = "Analyze focusing on novel methodologies..."
analysis = analyzer.analyze_presenter(presenter_data, system_prompt=custom_prompt)

# Custom project generation
generator = ProjectGenerator(api_client, custom_config)
proposal = generator.generate_project_proposal(
    participant_name,
    profile,
    domain_context,
    catechism_type="EUGrants"
)
```

## Output Formats

### Reports Structure

The package generates dual-format reports:

```
outputs/
├── profiles/
│   └── Researcher_Name/
│       ├── Researcher_Name_research_profile.md
│       └── Researcher_Name_research_profile.json
└── projects/
    └── Participant_Name/
        ├── Participant_Name_project_proposal_KarmaGAP.md
        └── Participant_Name_project_proposal_KarmaGAP.json
```

### JSON Format

```json
{
  "timestamp": "2025-01-01T12:00:00",
  "metadata": {
    "presenter": "Researcher Name",
    "report_type": "research_profile"
  },
  "content": "Full analysis text..."
}
```

### Markdown Format

```markdown
# Research Profile: Researcher Name

Generated on: 2025-01-01 12:00:00

---

## Research Focus

Detailed analysis...

## Future Directions

Potential research trajectories...
```

## Workflows

### Complete Symposium Preparation

```bash
# 1. Analyze all presenters
symposium analyze presenters \
  --data-dir data/inputs/aif_2025/speakers/ \
  --output-dir outputs/presenters/ \
  --domain-file data/domains/active_inference.md

# 2. Analyze all participants
symposium analyze participants \
  --registration-file data/participants.csv \
  --output-dir outputs/participants/ \
  --domain-file data/domains/active_inference.md

# 3. Generate detailed profiles
symposium generate profiles \
  --data-dir data/inputs/aif_2025/ \
  --output-dir outputs/profiles/ \
  --include-methods

# 4. Generate project proposals
symposium generate projects \
  --profiles-dir outputs/profiles/ \
  --output-dir outputs/projects/ \
  --domain-file data/domains/active_inference.md \
  --catechism KarmaGAP \
  --collaborators-file data/collaborators.md

# 5. Create visualizations
symposium visualize embeddings \
  --input-dir outputs/profiles/ \
  --output-dir outputs/visualizations/ \
  --method pca
```

### Incremental Updates

```bash
# Analyze new presenters only
symposium analyze presenters \
  --data-dir data/inputs/aif_2025/new_presenters/ \
  --output-dir outputs/profiles/

# Update specific participant profiles
symposium generate profiles \
  --data-dir data/inputs/aif_2025/specific_researchers/ \
  --output-dir outputs/profiles/
```

## Troubleshooting

### Common Issues

#### "Module 'symposium' not found"

**Solution:**
```bash
# Ensure you're in virtual environment
source .venv/bin/activate

# Reinstall package
uv pip install -e .
```

#### "API key not found"

**Solution:**
```bash
# Check .env file exists and has correct keys
cat .env

# Test API connection
python -c "from symposium.core.api import APIClient; print('API setup OK')"
```

#### "No data found"

**Solution:**
```bash
# Check data directory structure
ls -la data/inputs/aif_2025/

# Verify CSV files exist and are readable
head data/inputs/aif_2025/*/works-*.csv
```

#### Token limit exceeded

**Solution:**
```bash
# Reduce rows per file
symposium analyze presenters --max-rows 5 --data-dir data/inputs/aif_2025/

# Or increase token limit in config
echo '{"data": {"max_prompt_tokens": 15000}}' > config.json
```

### Performance Tips

1. **Batch Processing**: Process large datasets in chunks
2. **Token Management**: Use `--max-rows` to limit input size
3. **Caching**: Results are cached in output directories
4. **Parallel Processing**: API calls are rate-limited automatically

### Rate Limiting

The package handles API rate limits automatically:
- **Perplexity**: Manual retry with exponential backoff
- **OpenRouter**: Automatic retry with backoff (built-in)

If you hit rate limits frequently:
```bash
# Add delays between requests
import time
time.sleep(2)  # 2-second delay

# Or use smaller batches
symposium analyze presenters --max-rows 3
```

## Best Practices

### Data Organization

1. **Consistent Naming**: Use clear, consistent folder names
2. **Data Validation**: Check CSV structure before processing
3. **Backup**: Keep backups of original data
4. **Version Control**: Track data changes in git (use .gitignore for outputs)

### Configuration

1. **Environment Variables**: Keep API keys in .env, not config files
2. **Path Validation**: Use absolute paths for reliability
3. **Testing**: Test configuration with small datasets first

### Analysis Quality

1. **Domain Context**: Provide relevant domain knowledge files
2. **Iterative Refinement**: Review and refine generated content
3. **Validation**: Cross-check generated analyses with original data

## Support

### Getting Help

1. **Check Documentation**: Read the relevant guide section
2. **Test Commands**: Use `--help` to see available options
3. **Error Messages**: Read error logs carefully
4. **Community**: Check GitHub issues and discussions

### Reporting Issues

```bash
# Include this information in bug reports:
python --version
uv --version
symposium --help
cat .env  # (without API keys)
ls -la data/inputs/aif_2025/
```

## Advanced Features

### Custom Catechisms

Add new proposal templates in `data/catechisms/`:

```markdown
# Custom Catechism Template

## Section 1: Problem Definition
1. What is the core problem?
2. Why is it important?

## Section 2: Solution Approach
1. What is your proposed solution?
2. How does it address the problem?
```

Then use:
```bash
symposium generate projects --catechism Custom
```

### Custom Domain Knowledge

Create domain-specific context files in `data/domains/`:

```markdown
# Active Inference Domain Context

## Core Principles
- Free Energy Principle
- Active Inference
- Predictive Processing

## Current Challenges
- Scalability issues
- Biological plausibility
- Real-world applications

## Research Opportunities
- Novel applications in AI
- Integration with neuroscience
- Clinical applications
```

### Integration with Other Tools

```python
# Export results for further analysis
import json
from pathlib import Path

# Load generated profiles
profile_dir = Path("outputs/profiles")
for participant_dir in profile_dir.iterdir():
    if participant_dir.is_dir():
        json_file = participant_dir / f"{participant_dir.name}_research_profile.json"
        if json_file.exists():
            with open(json_file) as f:
                data = json.load(f)
                # Process data as needed
```

## Examples

### Example 1: Quick Presenter Analysis

```bash
# Analyze a single presenter
mkdir -p data/inputs/aif_2025/test_presenter
# Add CSV files to test_presenter directory

symposium analyze presenters \
  --data-dir data/inputs/aif_2025/test_presenter/ \
  --output-dir outputs/test/
```

### Example 2: Full Symposium Setup

```bash
# 1. Setup data directories
mkdir -p data/inputs/aif_2025/{speakers,participants}
mkdir -p data/{catechisms,domains}

# 2. Add domain context
cat > data/domains/active_inference.md << 'EOF'
# Active Inference Research Domain

Core concepts, challenges, and opportunities...
EOF

# 3. Run complete analysis
symposium analyze presenters --data-dir data/inputs/aif_2025/speakers/ --output-dir outputs/
symposium analyze participants --registration-file data/participants.csv --output-dir outputs/
symposium generate profiles --data-dir data/inputs/aif_2025/ --output-dir outputs/ --include-methods
symposium generate projects --profiles-dir outputs/profiles/ --output-dir outputs/ --domain-file data/domains/active_inference.md --catechism KarmaGAP
```

### Example 3: Visualization Pipeline

```bash
# Generate visualizations from analysis results
symposium visualize embeddings \
  --input-dir outputs/profiles/ \
  --output-dir outputs/visualizations/ \
  --method pca \
  --n-components 2

symposium visualize networks \
  --input-dir outputs/profiles/ \
  --output-dir outputs/visualizations/ \
  --threshold 0.3

symposium visualize distributions \
  --input-dir outputs/profiles/ \
  --output-dir outputs/visualizations/
```

## API Reference

For detailed API documentation, see [API Guide](api_guide.md).

### Quick API Reference

```python
# Core classes
from symposium.core.api import APIClient
from symposium.core.config import Config
from symposium.analysis.presenters import PresenterAnalyzer
from symposium.generation.projects import ProjectGenerator

# Configuration
config = Config()
config.get("api.provider")  # Get setting
config.set("data.max_rows", 20)  # Set setting

# API client
client = APIClient.create("perplexity", api_key="your_key")
response = client.get_response("Analyze this research...")

# Analysis
analyzer = PresenterAnalyzer(client)
results = analyzer.analyze_all_presenters(data_path, output_dir)

# Generation
generator = ProjectGenerator(client)
proposal = generator.generate_project_proposal(name, profile, domain, catechism)
```

---

**Next Steps:**
- Review [API Guide](api_guide.md) for detailed API usage
- Check [Architecture](architecture.md) for system design
- See [Installation](installation.md) for setup details
- Visit [Development Guide](development.md) for contributing

