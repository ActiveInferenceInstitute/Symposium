"""Presenter research analysis module."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from symposium.core.api import BaseAPIProvider
from symposium.core.data_loader import DataLoader
from symposium.io.readers import ReportReader
import pandas as pd

logger = logging.getLogger(__name__)


class PresenterAnalyzer:
    """Analyzer for presenter research profiles."""

    def __init__(self, api_client: BaseAPIProvider, config: Optional[Dict[str, Any]] = None):
        """Initialize presenter analyzer.
        
        Args:
            api_client: API client for generating analysis
            config: Optional configuration dictionary
        """
        self.api_client = api_client
        self.config = config or {}
        self.data_loader = DataLoader()

    def load_presenter_data(
        self,
        data_path: Path,
        max_rows: Optional[int] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Load presenter data from directory.
        
        Args:
            data_path: Path to directory containing presenter folders
            max_rows: Maximum rows to load per file
            
        Returns:
            Dictionary of presenter data
        """
        return self.data_loader.load_presenter_data(data_path, max_rows)

    def generate_research_prompt(
        self,
        presenter_data: Dict[str, Any],
        domain_context: Optional[str] = None
    ) -> str:
        """Generate research analysis prompt for a presenter.
        
        Args:
            presenter_data: Presenter data dictionary
            domain_context: Optional domain context/description
            
        Returns:
            Generated prompt string
        """
        # Extract and format topics
        topics_df = presenter_data.get('topics', pd.DataFrame())
        if not topics_df.empty:
            topics_str = topics_df.to_string()
        else:
            topics_str = "No topic data available"

        # Extract and format recent works
        works_df = presenter_data.get('works', pd.DataFrame())
        if not works_df.empty:
            # Select relevant columns if they exist
            cols = [c for c in ['title', 'publication_year', 'cited_by_count'] if c in works_df.columns]
            if cols:
                recent_works = works_df[cols].head(10)
                works_str = recent_works.to_string()
            else:
                works_str = works_df.head(10).to_string()
        else:
            works_str = "No works data available"

        prompt = f"""Please analyze the research profile of {presenter_data['name']} based on the following data.

Research Topics and Frequencies:
{topics_str}

Recent Publications:
{works_str}

Please provide a comprehensive analysis including:

1. **RESEARCH FOCUS**
   - Main research areas and expertise
   - Key methodologies and approaches
   - Notable contributions to the field

2. **IMPACT AND INFLUENCE**
   - Citation patterns and research impact
   - Key collaborations and networks
   - Real-world applications

3. **RESEARCH EVOLUTION**
   - How research interests have developed over time
   - Emerging research directions
   - Trajectory and trends

4. **KEY CONTRIBUTIONS**
   - Most significant papers and findings
   - Theoretical or methodological innovations
   - Impact on the field

5. **FUTURE DIRECTIONS**
   - Potential research trajectories
   - Collaboration opportunities
   - Areas for future exploration"""

        if domain_context:
            prompt += f"""

**DOMAIN CONTEXT**:
{domain_context}

6. **DOMAIN RELEVANCE**
   - How this researcher's work relates to the domain context
   - Potential contributions to domain challenges
   - Synergies and opportunities"""

        return prompt

    def analyze_presenter(
        self,
        presenter_data: Dict[str, Any],
        domain_context: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Analyze a presenter's research profile.
        
        Args:
            presenter_data: Presenter data dictionary
            domain_context: Optional domain context
            system_prompt: Optional system prompt override
            
        Returns:
            Analysis text
        """
        if system_prompt is None:
            system_prompt = (
                "You are an expert research analyst specializing in academic profile analysis. "
                "Provide detailed, evidence-based analysis focusing on research contributions, "
                "impact, and future potential."
            )

        prompt = self.generate_research_prompt(presenter_data, domain_context)
        
        # Token limit check
        max_tokens = self.config.get('max_prompt_tokens', 12000)
        if self.data_loader.estimate_token_count(prompt) > max_tokens:
            logger.warning(f"Prompt exceeds token limit, truncating for {presenter_data['name']}")
            prompt = self.data_loader.truncate_to_tokens(prompt, max_tokens)

        response = self.api_client.get_response(prompt, system_prompt)
        logger.info(f"Generated analysis for {presenter_data['name']}")
        
        return response

    def analyze_all_presenters(
        self,
        data_path: Path,
        output_dir: Path,
        domain_context: Optional[str] = None,
        max_rows: Optional[int] = None
    ) -> Dict[str, str]:
        """Analyze all presenters in a directory.
        
        Args:
            data_path: Path to presenter data directory
            output_dir: Output directory for reports
            domain_context: Optional domain context
            max_rows: Maximum rows to load per file
            
        Returns:
            Dictionary mapping presenter names to analysis text
        """
        from symposium.io.writers import ReportWriter

        presenters = self.load_presenter_data(data_path, max_rows)
        results = {}

        for presenter_name, presenter_data in presenters.items():
            try:
                logger.info(f"Analyzing presenter: {presenter_name}")
                analysis = self.analyze_presenter(presenter_data, domain_context)
                results[presenter_name] = analysis

                # Save report
                ReportWriter.save_presenter_report(
                    presenter_name,
                    analysis,
                    output_dir,
                    "research_profile"
                )

            except Exception as e:
                logger.error(f"Error analyzing presenter {presenter_name}: {e}")
                continue

        logger.info(f"Completed analysis for {len(results)} presenters")
        return results

