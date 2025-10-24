# CLI Module

Command-line interface for the Symposium package.

## Overview

This module provides the command-line interface for all Symposium operations, including analysis, generation, and visualization commands.

## Components

### Main CLI Router
Central command dispatcher that routes to appropriate subcommands:
- Argument parsing and validation
- Subcommand routing
- Configuration loading
- Error handling and user feedback

### Analysis Commands
Research analysis and profiling commands:
- `analyze presenters` - Analyze presenter research profiles
- `analyze participants` - Analyze participant profiles

### Generation Commands
Content generation and synthesis commands:
- `generate profiles` - Generate research profiles
- `generate projects` - Generate project proposals

### Visualization Commands
Data visualization and plotting commands:
- `visualize embeddings` - Create embedding plots
- `visualize networks` - Create similarity networks
- `visualize distributions` - Create statistical plots

## Usage

### Basic Commands
```bash
# Show help
symposium --help

# Analyze presenters
symposium analyze presenters --data-dir data/inputs/aif_2024/ --output-dir outputs/presenters/

# Generate profiles
symposium generate profiles --data-dir data/inputs/aif_2024/ --output-dir outputs/profiles/

# Create visualizations
symposium visualize networks --input-dir outputs/profiles/ --output-dir outputs/visualizations/
```

### Advanced Usage
```bash
# Analyze with domain context
symposium analyze presenters \
  --data-dir data/inputs/aif_2024/ \
  --output-dir outputs/presenters/ \
  --domain-file data/domains/active_inference.md \
  --max-rows 10 \
  --api-provider perplexity

# Generate projects with specific template
symposium generate projects \
  --profiles-dir outputs/profiles/ \
  --output-dir outputs/proposals/ \
  --domain-file data/domains/active_inference.md \
  --catechism KarmaGAP \
  --catechisms-dir data/catechisms/

# Create detailed visualizations
symposium visualize embeddings \
  --input-dir outputs/profiles/ \
  --output-dir outputs/visualizations/ \
  --method pca \
  --n-components 3
```

## Command Structure

### Analysis Commands
```bash
symposium analyze presenters [OPTIONS]
symposium analyze participants [OPTIONS]
```

**Options**:
- `--data-dir`: Directory containing researcher data
- `--registration-file`: CSV file with participant data
- `--output-dir`: Output directory for reports
- `--domain-file`: Domain context file
- `--max-rows`: Maximum rows per CSV file
- `--api-provider`: API provider (perplexity, openrouter)

### Generation Commands
```bash
symposium generate profiles [OPTIONS]
symposium generate projects [OPTIONS]
```

**Options**:
- `--data-dir`: Directory containing researcher data
- `--profiles-dir`: Directory containing participant profiles
- `--output-dir`: Output directory for generated content
- `--domain-file`: Domain context file
- `--include-methods`: Generate methods documentation
- `--catechism`: Catechism type (KarmaGAP, EUGrants, Synthetic)
- `--catechisms-dir`: Directory containing catechism templates
- `--collaborators-file`: File with potential collaborators

### Visualization Commands
```bash
symposium visualize embeddings [OPTIONS]
symposium visualize networks [OPTIONS]
symposium visualize distributions [OPTIONS]
```

**Options**:
- `--input-dir`: Directory containing markdown files
- `--output-dir`: Output directory for plots
- `--method`: Dimension reduction method (pca, lsa, tsne)
- `--n-components`: Number of components (2, 3)
- `--threshold`: Similarity threshold for networks
- `--layout`: Network layout (spring, circular, kamada_kawai)

## Configuration

The CLI automatically loads configuration from:
1. Environment variables
2. Configuration JSON file
3. Built-in defaults

## Error Handling

- Comprehensive error messages
- Graceful degradation
- Configuration validation
- File existence checking
- API connectivity testing

## Integration

This module integrates with:
- `symposium.analysis` - Analysis functionality
- `symposium.generation` - Generation functionality
- `symposium.visualization` - Visualization functionality
- `symposium.core` - Configuration and API clients
