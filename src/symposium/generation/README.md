# Generation Module

Content generation and synthesis functionality for the Symposium package.

## Overview

This module handles the generation of research profiles, project proposals, and related content using AI agents and structured templates.

## Components

### ProfileGenerator
Generates comprehensive research profiles and method documentation:
- Research profile synthesis from academic data
- Method extraction and documentation
- Domain integration analysis
- Technical capability assessment

### ProjectGenerator
Creates structured project proposals using catechism templates:
- Research project proposal generation
- Collaboration matching and justification
- Domain-specific project development
- Template-based structured output

## Usage

```python
from symposium.generation import ProfileGenerator, ProjectGenerator

# Generate research profiles
generator = ProfileGenerator(api_client, config)
results = generator.generate_all_profiles(data_path, output_dir, include_methods=True)

# Generate project proposals
generator = ProjectGenerator(api_client, config)
results = generator.generate_all_projects(
    profiles_dir, output_dir, domain_file,
    catechism_type="KarmaGAP"
)
```

## Templates

### Catechism Templates
- **KarmaGAP**: Karma GAP Grants proposal format
- **EUGrants**: European Union grant proposal format
- **Synthetic**: Synthetic research catechism format

### System Prompts
- Research method analysis prompts
- Project proposal generation prompts
- Profile synthesis prompts

## Data Requirements

### Profile Generation
- Researcher data with topics and publications
- Domain context files
- Optional method documentation requirements

### Project Generation
- Participant profiles from analysis module
- Domain context and requirements
- Catechism templates
- Optional collaborator lists

## Output Formats

### Research Profiles
- Comprehensive researcher profiles
- Method documentation
- Technical capability assessments
- Domain integration analysis

### Project Proposals
- Structured project proposals
- Collaboration recommendations
- Implementation roadmaps
- Justification and impact analysis

## Integration

This module integrates with:
- `symposium.analysis` - Analyzed profiles and data
- `symposium.core` - API clients and configuration
- `symposium.io` - File reading and template loading
- `data/catechisms/` - Template storage
- `data/prompts/` - System prompt storage
