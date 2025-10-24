# Perplexity Web Research Integration

## Overview

The Symposium package leverages Perplexity's Sonar model for comprehensive web-based research on symposium participants. This document outlines how deep research capabilities are maximized for participant background analysis.

## Research Methodology

### Web Search Scope

The system performs exhaustive multi-source searches across:

- **Academic Databases**: Google Scholar, ResearchGate, ORCID, institutional repositories
- **Professional Profiles**: LinkedIn, university faculty pages, research lab websites
- **Publication Sources**: arXiv, bioRxiv, conference proceedings, journal articles
- **Code Repositories**: GitHub, GitLab, Bitbucket
- **Social Media**: Twitter/X research presence, academic blogs
- **Institutional Pages**: University profiles, lab websites, project pages
- **Media**: Interviews, podcasts, conference videos

### Research Depth

For each participant, the system conducts **deep investigative research** covering:

1. **Academic Background**
   - Complete educational history with dates and institutions
   - Research areas and specific expertise domains
   - Current and historical academic positions
   - Awards, grants, honors, and achievements
   - Links to all academic profile pages

2. **Research Contributions**
   - Key publications with full citations and DOI links
   - Citation metrics (h-index, total citations)
   - Research methodologies and focus areas
   - Collaborative networks and frequent co-authors
   - Recent preprints and working papers

3. **Professional Experience**
   - Complete employment history with dates
   - Industry and consulting experience
   - Professional society memberships
   - Leadership roles in organizations
   - Patents and technical reports

4. **Active Inference Engagement**
   - Direct connections to Active Inference research
   - Adjacent field connections (free energy, Bayesian inference)
   - Methodological overlap with Active Inference
   - Potential applications and research gaps

5. **Academic Networks**
   - Key collaborators with profile links
   - Conference presentations and proceedings
   - Workshop organization and participation
   - Community engagement (tutorials, code, blogs)

6. **Online Presence**
   - Personal and research websites
   - All academic profile links (Scholar, ResearchGate, ORCID)
   - Professional profiles (LinkedIn)
   - Code repositories (GitHub)
   - Social media research presence

## Citation Requirements

### Comprehensive Source Attribution

Every factual claim in the research output includes:

- **Inline Citations**: Numbered references or source links
- **Clickable URLs**: Direct links to all online resources
- **DOI Links**: For all publications and papers
- **Profile Links**: Direct links to all professional profiles
- **References Section**: Complete bibliography with all URLs

### Output Format

Research reports use markdown with:
- Clickable hyperlinks throughout the text
- Immediate source attribution for findings
- Structured references section at the end
- Clear distinction between verified facts and inferences

## API Configuration

### Perplexity Sonar Model

```python
# Perplexity client configuration
perplexity_client = PerplexityProvider(
    api_key=PERPLEXITY_API_KEY,
    model="sonar",                # Optimized for web research
    temperature=0.7,              # Balanced creativity/accuracy
    max_tokens=4000              # Extended for comprehensive research
)
```

### Enhanced System Prompt

The research specialist system prompt emphasizes:

- **Elite research intelligence analyst** role
- **Real-time web search** capabilities
- **Multi-source cross-reference** validation
- **Exhaustive citation** requirements
- **Comprehensive database** coverage

### Research Prompt Structure

The participant research prompt includes:

1. **Clear Research Subject**: Name, affiliation, ORCID, background
2. **Research Methodology**: Explicit instructions for exhaustive searches
3. **Required Analysis Sections**: 7 comprehensive analysis areas
4. **Citation Requirements**: Every statement must be sourced
5. **Output Format**: Markdown with clickable links

## Integration in Workflow

### Dedicated Perplexity Usage

Background research **exclusively** uses Perplexity:

```python
# In run.py
if include_background:
    perplexity_client = APIClient.create('perplexity')
    print("   🔍 Using Perplexity Sonar for background research")

# In participants.py
if include_background_research and perplexity_client:
    logger.info(f"🔍 Using Perplexity Sonar for background research: {name}")
    original_client = self.api_client
    self.api_client = perplexity_client
    
    background = self.research_participant_background(participant_data)
    participant_results['background_research'] = background
    
    self.api_client = original_client
```

### API Client Separation

The system maintains separate API clients:

- **Perplexity (Sonar)**: Background research with web search
- **OpenRouter (Claude)**: Profile analysis and curriculum generation

This ensures optimal API usage:
- Perplexity's web search for factual research
- Claude's reasoning for analysis and personalization

## Quality Assurance

### Research Verification

The system ensures:

1. **Multi-Source Validation**: Cross-reference across databases
2. **Recent Activity**: Prioritize last 3-5 years
3. **Source Availability**: Note when information is limited
4. **Fact vs. Inference**: Clear distinction in output

### Output Quality

Each research report contains:

- **Clickable Links**: All URLs are hyperlinked
- **DOI References**: Direct links to publications
- **Profile Links**: Access to all online profiles
- **Comprehensive Coverage**: All available sources explored
- **References Section**: Complete bibliography

## Testing

### Test Coverage

Tests verify:

1. **Perplexity Client Usage**: Correct API client for background research
2. **max_tokens Parameter**: Extended length for comprehensive research
3. **Link Generation**: Output contains URLs and citations
4. **API Separation**: Perplexity used only for background research

### Test Example

```python
def test_analyze_all_participants_with_perplexity(
    mock_save, mock_api_client, sample_participant_csv, tmp_path
):
    # Create mock Perplexity with enhanced research
    mock_perplexity = Mock()
    mock_perplexity.get_response.return_value = """
    ## Academic Background
    - PhD from Test University [link](https://test.edu/profile)
    - Google Scholar: [link](https://scholar.google.com/test)
    
    ## References
    [1] https://test.edu/profile
    [2] https://scholar.google.com/test
    """
    
    results = analyzer.analyze_all_participants(
        sample_participant_csv,
        output_dir,
        include_background_research=True,
        perplexity_client=mock_perplexity
    )
    
    # Verify links are present
    for name, result in results.items():
        assert 'link' in result['background_research'] or 'http' in result['background_research']
    
    # Verify max_tokens parameter
    for call in mock_perplexity.get_response.call_args_list:
        assert call[1]['max_tokens'] >= 4000
```

## Usage Examples

### Command Line

```bash
# Run complete analysis with background research
./symposium.sh
# Select option 2: Analyze 2025 Participants
# Choose option 4: Complete Analysis (All Features)
```

### Programmatic Usage

```python
from symposium.core.api import APIClient
from symposium.analysis.participants import ParticipantAnalyzer
from pathlib import Path

# Create API clients
perplexity_client = APIClient.create('perplexity')
openrouter_client = APIClient.create('openrouter')

# Initialize analyzer with OpenRouter
analyzer = ParticipantAnalyzer(openrouter_client)

# Run analysis with Perplexity for background research
results = analyzer.analyze_all_participants(
    csv_path=Path("data/inputs/aif_2025/Public_Participant_Information.csv"),
    output_dir=Path("outputs/2025_symposium"),
    include_background_research=True,
    include_curriculum=True,
    perplexity_client=perplexity_client
)
```

## Output Examples

### Before Enhancement

```markdown
## ACADEMIC BACKGROUND
- Educational history and qualifications not specified
- Research areas include early childhood education
- Currently at University of Portsmouth
```

### After Enhancement

```markdown
## ACADEMIC BACKGROUND
- PhD in Education from [University of Portsmouth](https://port.ac.uk/profile/alexander-sabine)
- Research profile: [Google Scholar](https://scholar.google.com/citations?user=ABC123)
- Current position: Senior Lecturer, [School of Education](https://port.ac.uk/education)
- ORCID: [0000-0001-2345-6789](https://orcid.org/0000-0001-2345-6789)

## RESEARCH CONTRIBUTIONS
- Key Publication: "Quality early childhood education" ([DOI: 10.1234/example](https://doi.org/10.1234/example))
- Citation metrics: h-index 12, 450+ citations ([Google Scholar](https://scholar.google.com/citations?user=ABC123))
- Recent preprints on environmental pedagogies ([ResearchGate](https://researchgate.net/profile/Alexander-Sabine))

## ONLINE PRESENCE
- Personal Website: https://alexandersabine.com
- LinkedIn: https://linkedin.com/in/alexandersabine
- GitHub: https://github.com/asabine
- Twitter/X: https://twitter.com/asabine_edu

## References
[1] University of Portsmouth Profile: https://port.ac.uk/profile/alexander-sabine
[2] Google Scholar: https://scholar.google.com/citations?user=ABC123
[3] Key Publication DOI: https://doi.org/10.1234/example
[4] ResearchGate Profile: https://researchgate.net/profile/Alexander-Sabine
```

## Performance Considerations

### Token Management

- **max_tokens=4000**: Allows comprehensive research with extensive citations
- **Response Length**: Typically 2000-3500 tokens for thorough research
- **Cost Optimization**: Single comprehensive call vs. multiple smaller calls

### Rate Limiting

- **Exponential Backoff**: Built into API client
- **Retry Logic**: Handles transient failures
- **Sequential Processing**: One participant at a time to respect rate limits

## Future Enhancements

### Potential Improvements

1. **Citation Validation**: Verify all links are accessible
2. **Source Ranking**: Prioritize high-quality sources
3. **Temporal Analysis**: Track research trajectory over time
4. **Network Mapping**: Visualize collaboration networks
5. **Impact Assessment**: Calculate research impact metrics

## References

- [Perplexity API Documentation](https://docs.perplexity.ai/)
- [Sonar Model Capabilities](https://docs.perplexity.ai/docs/model-cards)
- [Best Practices for Web Research](https://docs.perplexity.ai/docs/getting-started)

