# Symposium AI Agents

Comprehensive overview of all AI agents and intelligent systems in the Symposium package ecosystem.

## Overview

The Symposium package employs a sophisticated multi-agent architecture where specialized AI agents collaborate to provide comprehensive research analysis, participant profiling, content generation, and data visualization capabilities. Each agent has a specific role, capabilities, and integration points within the larger system.

## Agent Architecture

The agent ecosystem is organized into functional domains, each with specialized agents:

```
Symposium Agent Ecosystem
├── Core Infrastructure Agents (API, Config, Data, Logging)
├── Analysis Agents (Research, Education, Methodology)
├── Generation Agents (Profiles, Projects, Innovation)
├── I/O Agents (Data Ingestion, Report Generation, File Management)
├── Visualization Agents (Embeddings, Networks, Statistics)
├── CLI Agents (Orchestration, Coordination, User Interface)
├── Calendar Agents (Schedule Management, Event Processing)
├── Data Management Agents (Ingestion, Validation, Organization)
└── Test Agents (Quality Assurance, Validation, Coverage)
```

## Core Infrastructure Agents

**Location**: `src/symposium/core/AGENTS.md`

### API Gateway Agent
Unified interface manager for multiple LLM providers (Perplexity, OpenRouter).

**Key Capabilities**:
- Multi-provider API management with automatic switching
- Payment error detection (PaymentRequiredError for 402 errors)
- Token counting and optimization
- Rate limiting with exponential backoff retry logic
- Provider-specific error handling

**Integration**: Used by all analysis and generation agents

### Configuration Manager Agent
Hierarchical configuration management (defaults → JSON → environment → CLI).

**Key Capabilities**:
- Multi-level configuration hierarchy
- Secure API key management
- Path validation and management
- Cross-platform compatibility

### Data Processing Agent
Data loading, validation, and preprocessing specialist.

**Key Capabilities**:
- Multi-format support (CSV, JSON, Markdown)
- Token-aware truncation
- Content validation and error recovery
- OpenAlex data format handling

### Logging Infrastructure Agent
Centralized logging and monitoring system.

**Key Capabilities**:
- Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File and console output
- Error tracking and performance monitoring

### Error Recovery Agent
Robust error handling with PaymentRequiredError detection.

**Key Capabilities**:
- Payment error detection (402) - stops processing immediately
- Graceful degradation for other errors
- User-friendly error messages with provider-specific guidance
- Partial result preservation

## Analysis Agents

**Location**: `src/symposium/analysis/AGENTS.md`

### Research Analyst Agent
Expert research analyst specializing in academic profile analysis.

**System Prompt**: Expert research analyst focusing on contributions, impact, and future potential

**Key Capabilities**:
- Comprehensive research profile analysis
- Citation pattern and impact assessment
- Research evolution tracking
- Future trajectory prediction

**Input**: OpenAlex data, publication records, collaboration networks

**Output**: Structured research profiles, impact assessments, collaboration recommendations

### Educational Mentor Agent
Expert in educational program design and research mentoring.

**System Prompt**: Educational program design expert providing actionable learning plans

**Key Capabilities**:
- Participant expertise assessment
- Learning gap identification
- Skill development planning
- Collaboration matching

**Input**: Participant backgrounds, research interests, domain context

**Output**: Expertise assessments, development roadmaps, collaboration recommendations

### Methodologist Agent
Scientific method specialist for research method analysis.

**System Prompt**: Scientific methodologist providing technically accurate method descriptions

**Key Capabilities**:
- Research methodology identification
- Technical skill assessment
- Method evolution tracking
- Best practice recommendations

**Input**: Research publications, technical approaches, domain requirements

**Output**: Method documentation, technical capability assessments

### Analysis Workflow
1. Data Collection → 2. Context Analysis → 3. Profile Generation → 4. Method Analysis → 5. Impact Assessment → 6. Recommendation Engine

**Error Handling**:
- PaymentRequiredError stops processing immediately
- Other errors allow graceful degradation
- Partial results always preserved

## Generation Agents

**Location**: `src/symposium/generation/AGENTS.md`

### Research Profile Synthesizer Agent
Expert in research profile synthesis and academic content generation.

**System Prompt**: Expert research analyst focusing on contributions, impact, and future potential

**Key Capabilities**:
- Comprehensive research profile creation
- Method documentation synthesis
- Domain integration analysis
- Technical capability assessment

**Input**: Analyzed OpenAlex data, publication records, domain context

**Output**: Structured research profiles, method documentation, technical assessments

### Method Extraction Agent
Scientific method specialist for research method documentation.

**System Prompt**: Scientific methodologist providing detailed, technically accurate method descriptions

**Key Capabilities**:
- Research methodology identification
- Technical method documentation
- Equipment and tool specification
- Limitation and trend analysis

**Input**: Research publications, technical approaches, domain requirements

**Output**: Method documentation, technical specifications, application guidelines

### Project Proposal Generator Agent
Expert research director specializing in project development and proposal writing.

**System Prompt**: Top-level research director creating concrete, original, well-structured proposals

**Key Capabilities**:
- Innovative project proposal creation
- Research domain field shifting
- Collaboration identification
- Technical feasibility assessment

**Input**: Participant profiles, domain context, catechism templates, collaborator lists

**Output**: Complete project proposals, collaboration justifications, implementation roadmaps

### Innovation Catalyst Agent
Creative research director for breakthrough project development.

**System Prompt**: Top researcher creating highly original, breakthrough research projects

**Key Capabilities**:
- Field shift identification
- Novel research direction synthesis
- Cross-domain integration
- Breakthrough opportunity analysis

**Input**: Multiple researcher profiles, domain challenges, collaboration networks

**Output**: Breakthrough project concepts, field shift proposals, innovation assessments

### Generation Workflow
1. Profile Analysis → 2. Method Identification → 3. Content Synthesis → 4. Project Development → 5. Collaboration Matching → 6. Quality Assurance

**Template Integration**:
- KarmaGAP: Ethical research grant format
- EUGrants: European research funding format
- Synthetic: Cross-domain synthesis format

## I/O Agents

**Location**: `src/symposium/io/AGENTS.md`

### Data Ingestion Agent
Multi-format data ingestion and validation specialist.

**Key Capabilities**:
- Multi-format file reading (Markdown, JSON, CSV)
- Data structure validation
- Content integrity checking
- Format conversion

**Supported Formats**: Markdown, JSON, CSV, Template files

### Report Generation Agent
Structured report writing and formatting specialist.

**Key Capabilities**:
- Multi-format report generation (Markdown + JSON)
- Metadata integration
- Directory structure management
- Filename sanitization

**Output Structure**:
```
outputs/
├── presenters/PresenterName/
│   ├── profile.md & .json
│   └── methods.md & .json
├── participants/ParticipantName/
│   ├── learning_plan.md & .json
│   └── roadmap.md
└── proposals/ParticipantName/
    └── project_proposal_*.md & .json
```

### Template Management Agent
Template loading and processing specialist.

**Key Capabilities**:
- Template file discovery
- Format validation
- Variable substitution
- Template versioning

**Template Types**: Catechisms, System Prompts, Configuration Templates, Report Templates

### File System Agent
Cross-platform file system management and path resolution.

**Key Capabilities**:
- Dynamic path resolution
- Directory creation and validation
- Security path validation
- Cross-platform compatibility

### Data Validation Agent
Data integrity and format validation specialist.

**Key Capabilities**:
- Multi-format validation
- Structure compliance checking
- Content integrity verification
- Error detection and reporting

## Visualization Agents

**Location**: `src/symposium/visualization/AGENTS.md`

### Embedding Analysis Agent
Dimension reduction and embedding visualization specialist.

**Key Capabilities**:
- Multi-algorithm dimension reduction (PCA, LSA, t-SNE, UMAP, Isomap, NMF, LDA)
- 2D and 3D visualization
- Feature importance analysis
- Interactive plot generation

**Algorithms**: PCA, LSA, t-SNE, UMAP, Isomap, NMF, LDA

**Visualization Features**: 2D/3D plots, feature maps, interactive elements

### Network Analysis Agent
Similarity network creation and community detection specialist.

**Key Capabilities**:
- Similarity network construction
- Community detection algorithms
- Centrality analysis
- Network visualization with multiple layouts

**Network Types**: Term networks, Document networks, Co-occurrence networks

**Layout Algorithms**: Spring, Circular, Kamada-Kawai

### Statistical Visualization Agent
Statistical distribution and comparative analysis specialist.

**Key Capabilities**:
- Distribution analysis and plotting
- Comparative statistical visualization
- Trend identification
- Statistical testing integration

**Distribution Types**: Document length, TF-IDF scores, Category comparisons, Temporal trends

**Plot Types**: Histograms, Box plots, Violin plots, Scatter plots

### Word Cloud Generator Agent
Text summarization and keyword visualization specialist.

**Key Capabilities**:
- Word frequency analysis
- Visual keyword representation
- Customizable styling
- Multi-format export

**Features**: Frequency weighting, Color schemes, Layout optimization, Export formats

### PCA Analysis Agent
Comprehensive PCA analysis and visualization specialist.

**Key Capabilities**:
- Scree plots (variance explained per component)
- Loading plots (feature contributions)
- Biplots (scores + loadings)
- Loadings heatmaps
- Component correlation matrices
- 3D component visualizations
- Structured CSV data exports

## CLI Agents

**Location**: `src/symposium/cli/AGENTS.md`

### Command Orchestrator Agent
Central command dispatcher and workflow coordinator.

**Key Capabilities**:
- Multi-command coordination
- Argument parsing and validation
- Configuration management
- Error handling and recovery

**Command Structure**: `symposium [GLOBAL_OPTIONS] <COMMAND> [COMMAND_OPTIONS]`

### Analysis Coordinator Agent
Research analysis workflow management and execution.

**Key Capabilities**:
- Presenter analysis workflow
- Participant analysis workflow
- Data validation and preprocessing
- Result aggregation and reporting

**Commands**: `analyze presenters`, `analyze participants`

### Generation Coordinator Agent
Content generation workflow management and orchestration.

**Key Capabilities**:
- Profile generation workflow
- Project proposal generation
- Template management
- Collaboration matching

**Commands**: `generate profiles`, `generate projects`

### Visualization Coordinator Agent
Data visualization and plotting workflow management.

**Key Capabilities**:
- Embedding visualization workflow
- Network analysis visualization
- Statistical distribution plotting
- Multi-format output generation

**Commands**: `visualize embeddings`, `visualize networks`, `visualize distributions`, `visualize all`

### Error Handling Agent
Comprehensive error management and user communication.

**Key Capabilities**:
- Multi-level error detection
- User-friendly error messaging
- Recovery strategy implementation
- PaymentRequiredError handling

**Error Categories**: Configuration, Data, API (including PaymentRequiredError), Processing, Output

## Calendar Agents

**Location**: `src/symposium/calendar/AGENTS.md`

### Schedule Management Agent
Calendar export and schedule management specialist.

**Key Capabilities**:
- Symposium schedule parsing and organization
- Multi-format calendar export (ICS, JSON, CSV)
- Event validation and conflict detection
- Timezone coordination and conversion

**Output**: ICS calendar files, structured schedule data, validation reports

### Event Processing Agent
Individual event processing and formatting specialist.

**Key Capabilities**:
- Event data parsing and validation
- Speaker and organizer information extraction
- Location and venue processing
- Description and abstract formatting

### Calendar Integration Agent
Calendar format conversion and validation specialist.

**Key Capabilities**:
- ICS format generation and validation
- Calendar application compatibility testing
- Format conversion between calendar standards
- Error detection and correction

### Timezone Coordination Agent
Multi-timezone event scheduling and coordination specialist.

**Key Capabilities**:
- Timezone conversion and validation
- Event timing optimization
- Conflict detection across timezones
- Daylight saving time handling

## Data Management Agents

**Location**: `data/AGENTS.md`

### Data Ingestion Agent
Multi-format data collection and standardization specialist.

**Key Capabilities**:
- Academic data collection (OpenAlex, Google Scholar)
- Participant registration processing
- Domain knowledge integration
- Template management

**Data Sources**: Academic databases, Registration systems, Knowledge bases, User contributions

### Data Validation Agent
Data quality assurance and integrity verification specialist.

**Key Capabilities**:
- Format validation and compliance
- Completeness checking
- Consistency verification
- Error detection and reporting

**Validation Categories**: Structural, Content, Consistency, Quality

### Template Management Agent
Catechism template and system prompt management specialist.

**Key Capabilities**:
- Template discovery and loading
- Format validation and compliance
- Version management
- Customization support

**Template Types**: KarmaGAP, EUGrants, Synthetic, System Prompts

### Domain Knowledge Agent
Domain-specific knowledge base management and integration specialist.

**Key Capabilities**:
- Knowledge base construction
- Context integration
- Field-specific terminology
- Research trend analysis

**Knowledge Sources**: Academic literature, Conference proceedings, Expert knowledge, Trend analysis

### Configuration Data Agent
System configuration and settings management specialist.

**Key Capabilities**:
- Hierarchical configuration management
- Environment variable integration
- JSON configuration file handling
- Security and validation

**Configuration Hierarchy**: Built-in defaults → JSON files → Environment variables → Command-line arguments

### Data Organization Agent
File system organization and directory structure management specialist.

**Key Capabilities**:
- Hierarchical directory management
- Naming convention enforcement
- Cross-platform compatibility
- Backup and recovery

## Test Agents

**Location**: `tests/AGENTS.md`

### Test Orchestrator Agent
Comprehensive test suite management and execution coordinator.

**Key Capabilities**:
- Multi-level test coordination
- Coverage analysis and reporting
- Test result aggregation
- Quality metric calculation

**Test Categories**: Unit tests, Integration tests, Real API tests, Performance tests

### Mock Data Agent
Test data generation and mock object management specialist.

**Key Capabilities**:
- Realistic test data generation
- Mock API response creation
- Fixture management
- Data validation

**Mock Types**: API responses, Research data, Configuration, File system

### Validation Agent
Test result validation and quality assurance specialist.

**Key Capabilities**:
- Test result verification
- Expected vs actual comparison
- Error pattern analysis
- Regression detection

### Coverage Analysis Agent
Code coverage analysis and reporting specialist.

**Key Capabilities**:
- Line coverage tracking
- Branch coverage analysis
- Function coverage reporting
- Coverage gap identification

**Coverage Goals**: > 90% overall, > 95% critical paths

### Performance Testing Agent
System performance monitoring and benchmarking specialist.

**Key Capabilities**:
- Execution time measurement
- Memory usage tracking
- CPU utilization monitoring
- Bottleneck identification

### Integration Testing Agent
End-to-end workflow validation and system integration specialist.

**Key Capabilities**:
- Complete workflow testing
- Cross-module validation
- Real API integration testing
- Error recovery testing

### Error Simulation Agent
Error condition testing and robustness validation specialist.

**Key Capabilities**:
- Error scenario simulation
- Edge case testing
- Failure mode analysis
- Recovery mechanism validation

**Error Types**: API errors (including PaymentRequiredError), Data errors, Configuration errors, Resource errors

## Agent Integration and Workflows

### Complete Analysis Workflow

1. **Data Ingestion Agent** → Loads participant/researcher data
2. **Data Validation Agent** → Validates data integrity
3. **Configuration Manager Agent** → Loads API keys and settings
4. **API Gateway Agent** → Establishes LLM provider connections
5. **Research Analyst Agent** → Analyzes research profiles
6. **Educational Mentor Agent** → Creates learning plans
7. **Methodologist Agent** → Documents research methods
8. **Report Generation Agent** → Saves results (Markdown + JSON)
9. **Error Recovery Agent** → Handles any errors (stops on PaymentRequiredError)

### Content Generation Workflow

1. **Data Processing Agent** → Loads analyzed profiles
2. **Template Management Agent** → Loads catechism templates
3. **Domain Knowledge Agent** → Integrates domain context
4. **Research Profile Synthesizer Agent** → Creates comprehensive profiles
5. **Method Extraction Agent** → Documents methods
6. **Project Proposal Generator Agent** → Generates proposals
7. **Innovation Catalyst Agent** → Identifies breakthrough opportunities
8. **Report Generation Agent** → Saves generated content

### Visualization Workflow

1. **Data Ingestion Agent** → Loads markdown or CSV data
2. **Data Processing Agent** → Prepares data for visualization
3. **Embedding Analysis Agent** → Performs dimension reduction
4. **Network Analysis Agent** → Creates similarity networks
5. **Statistical Visualization Agent** → Generates distribution plots
6. **Word Cloud Generator Agent** → Creates keyword visualizations
7. **PCA Analysis Agent** → Comprehensive PCA analysis
8. **Export Management Agent** → Saves visualizations

## Error Handling Architecture

### Payment Error Handling (PaymentRequiredError)

**Detection**: API Gateway Agent detects 402 errors immediately

**Response**:
- Processing stops immediately (no retries)
- Clear error message displayed
- Provider-specific credit addition links provided
- Partial results saved for completed work

**Integration**: All agents using API Gateway Agent inherit this behavior

### Graceful Degradation

**Non-Payment Errors**:
- Individual participant/researcher errors logged
- Processing continues with remaining items
- Partial results preserved
- System stability maintained

**Error Categories**:
- **Payment Errors (402)**: Fatal - stop processing
- **Rate Limit Errors (429)**: Retry with exponential backoff
- **Network Errors**: Retry with exponential backoff
- **Data Errors**: Log and continue
- **Configuration Errors**: User guidance provided

## Agent Communication Patterns

### Direct Integration
- Analysis agents → API Gateway Agent
- Generation agents → API Gateway Agent
- All agents → Logging Infrastructure Agent
- All agents → Configuration Manager Agent

### Data Flow
- Data Management Agents → Analysis Agents
- Analysis Agents → Generation Agents
- Generation Agents → I/O Agents
- I/O Agents → Visualization Agents

### Error Propagation
- API Gateway Agent → Error Recovery Agent
- Error Recovery Agent → All consuming agents
- PaymentRequiredError → Stops all processing
- Other errors → Graceful degradation

## Performance Standards

### API Agents
- **Response Time**: < 2 seconds average
- **Error Rate**: < 1% of operations
- **Token Efficiency**: > 95% context utilization

### Data Processing Agents
- **Read Speed**: < 100ms for typical files
- **Write Speed**: < 200ms for typical reports
- **Validation Accuracy**: 100% format compliance

### Visualization Agents
- **Generation Time**: < 30 seconds for typical datasets
- **Memory Usage**: < 1GB for large datasets
- **Image Quality**: > 300 DPI resolution

### Test Agents
- **Test Execution**: < 5 minutes for full suite
- **Coverage Reporting**: < 1 minute generation
- **Error Detection**: 99% accuracy

## Quality Metrics

### Overall System
- **API Response Success Rate**: > 99%
- **Data Processing Integrity**: 100%
- **Error Recovery Success**: 95%
- **Test Coverage**: > 90% overall, > 95% critical paths

### Agent-Specific Metrics
- **Analysis Depth**: Comprehensive and accurate
- **Generation Quality**: Professional and structured
- **Visualization Clarity**: 95% information readability
- **Error Handling**: 100% critical error paths covered

## Module-Specific Documentation

For detailed information about agents in each module, see:

- **Core Agents**: [src/symposium/core/AGENTS.md](src/symposium/core/AGENTS.md)
- **Analysis Agents**: [src/symposium/analysis/AGENTS.md](src/symposium/analysis/AGENTS.md)
- **Generation Agents**: [src/symposium/generation/AGENTS.md](src/symposium/generation/AGENTS.md)
- **I/O Agents**: [src/symposium/io/AGENTS.md](src/symposium/io/AGENTS.md)
- **Visualization Agents**: [src/symposium/visualization/AGENTS.md](src/symposium/visualization/AGENTS.md)
- **CLI Agents**: [src/symposium/cli/AGENTS.md](src/symposium/cli/AGENTS.md)
- **Calendar Agents**: [src/symposium/calendar/AGENTS.md](src/symposium/calendar/AGENTS.md)
- **Data Management Agents**: [data/AGENTS.md](data/AGENTS.md)
- **Test Agents**: [tests/AGENTS.md](tests/AGENTS.md)

## Agent Development Guidelines

### Creating New Agents

1. **Define Role**: Clear, specific role and responsibilities
2. **Specify Capabilities**: Detailed capability list
3. **Document Integration**: How it integrates with other agents
4. **Error Handling**: PaymentRequiredError and graceful degradation
5. **Performance Standards**: Response time, resource usage
6. **Quality Metrics**: Success criteria and validation

### Agent Communication

- Use API Gateway Agent for all LLM interactions
- Use Logging Infrastructure Agent for all logging
- Use Configuration Manager Agent for all configuration
- Use Error Recovery Agent for error handling patterns
- Follow PaymentRequiredError protocol for payment errors

### Testing Agents

- Unit tests for individual agent capabilities
- Integration tests for agent interactions
- Real API tests for live system validation
- Error simulation for PaymentRequiredError scenarios
- Performance tests for response time validation

## Active Inference Focus

All agents are designed with Active Inference principles in mind:

- **Academic Rigor**: Evidence-based analysis and recommendations
- **Domain Expertise**: Active Inference specific knowledge integration
- **Method Accuracy**: Correct research method identification
- **Collaboration Focus**: Meaningful partnership suggestions
- **Research Ethics**: Responsible AI and research practices

## Future Enhancements

- Real-time agent communication protocols
- Agent learning and adaptation capabilities
- Multi-agent collaboration optimization
- Enhanced error recovery strategies
- Performance monitoring and auto-scaling

---

**Last Updated**: 2025-11-07  
**Version**: 2.0  
**Maintained by**: Active Inference Institute

