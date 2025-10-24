# I/O Module

Input/Output operations and file management for the Symposium package.

## Overview

This module handles all file reading, writing, and data persistence operations across the Symposium ecosystem.

## Components

### ReportReader
File reading utilities for various formats:
- Markdown content reading
- JSON data loading
- CSV data import
- Template and configuration loading

### ReportWriter
Structured report writing and persistence:
- Markdown report generation
- JSON metadata storage
- Directory structure management
- Filename sanitization

## Usage

```python
from symposium.io import ReportReader, ReportWriter

# Reading files
content = ReportReader.read_markdown("data/domains/aif.md")
data = ReportReader.read_json("config/analysis.json")
df = ReportReader.read_csv("data/participants.csv")

# Writing reports
ReportWriter.save_markdown_report(
    content, output_path, title, metadata
)
ReportWriter.save_presenter_report(
    presenter_name, analysis, output_dir, report_type
)
```

## File Formats

### Markdown Files
- Research profiles and analysis
- Project proposals
- Documentation and guides
- Domain context files

### JSON Files
- Configuration and settings
- Metadata and results
- Structured data export
- API responses

### CSV Files
- Participant registration data
- Research metrics
- OpenAlex data exports
- Statistical data

## Directory Structure

### Input Directories
- `data/inputs/` - Research data and profiles
- `data/catechisms/` - Project proposal templates
- `data/domains/` - Domain knowledge files
- `data/prompts/` - System prompt templates

### Output Directories
- `outputs/presenters/` - Presenter analysis results
- `outputs/participants/` - Participant profiles
- `outputs/proposals/` - Project proposals
- `outputs/visualizations/` - Generated plots and charts

## Report Types

### Presenter Reports
- Research profiles
- Method documentation
- Impact assessments
- Collaboration recommendations

### Participant Reports
- Learning plans
- Development roadmaps
- Expertise assessments
- Project suggestions

### Project Reports
- Proposal documents
- Implementation plans
- Collaboration matrices
- Impact analysis

## Integration

This module integrates with:
- `symposium.analysis` - Writing analysis results
- `symposium.generation` - Saving generated content
- `symposium.cli` - File path resolution
- `symposium.core` - Configuration and logging
