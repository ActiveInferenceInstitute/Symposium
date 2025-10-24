"""Profile generation module."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from symposium.core.api import BaseAPIProvider
from symposium.core.data_loader import DataLoader

logger = logging.getLogger(__name__)


class ProfileGenerator:
    """Generator for research profiles and methods documentation."""

    def __init__(self, api_client: BaseAPIProvider, config: Optional[Dict[str, Any]] = None):
        """Initialize profile generator.
        
        Args:
            api_client: API client for generating content
            config: Optional configuration dictionary
        """
        self.api_client = api_client
        self.config = config or {}
        self.data_loader = DataLoader()

    def generate_research_methods_prompt(
        self,
        researcher_data: Dict[str, Any],
        domain_context: Optional[str] = None
    ) -> str:
        """Generate prompt for research methods extraction.
        
        Args:
            researcher_data: Researcher data dictionary
            domain_context: Optional domain context
            
        Returns:
            Generated prompt string
        """
        import pandas as pd
        
        topics_df = researcher_data.get('topics', pd.DataFrame())
        topics_str = topics_df.to_string() if not topics_df.empty else "No topic data available"

        works_df = researcher_data.get('works', pd.DataFrame())
        if not works_df.empty:
            cols = [c for c in ['title', 'publication_year', 'cited_by_count'] if c in works_df.columns]
            recent_works = works_df[cols].head(10) if cols else works_df.head(10)
            works_str = recent_works.to_string()
        else:
            works_str = "No works data available"

        prompt = f"""Please identify and document the research methods used by {researcher_data['name']}.

Research Topics:
{topics_str}

Recent Publications:
{works_str}"""

        if domain_context:
            prompt += f"""

Domain Context:
{domain_context}
"""

        prompt += """

For each method identified, please provide:

1. **METHOD NAME**
   - Clear, descriptive title of the experimental technique or theoretical method

2. **DETAILED DESCRIPTION**
   - How the method works, including underlying principles or mechanisms
   - Equipment, software, or analytical tools involved
   - Scales of observation (e.g., molecular, macroscopic) or systems it applies to

3. **RESULTS AND OUTCOMES**
   - Types of materials, scales, or data produced
   - Primary metrics or insights expected
   - Examples of phenomena or parameters investigated

4. **EMERGING TRENDS**
   - Whether the method is evolving with newer variations
   - Complementary technologies that enhance performance
   - Alignment with current trends (e.g., sustainability, data-driven modeling)

5. **LIMITATIONS**
   - Inherent constraints or trade-offs (precision, sensitivity, scalability)
   - External factors affecting reliability
   - Impact on result interpretation or method feasibility

Please be specific and technical in your analysis."""

        return prompt

    def generate_research_methods(
        self,
        researcher_data: Dict[str, Any],
        domain_context: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate research methods documentation for a researcher.
        
        Args:
            researcher_data: Researcher data dictionary
            domain_context: Optional domain context
            system_prompt: Optional system prompt override
            
        Returns:
            Generated methods documentation
        """
        if system_prompt is None:
            system_prompt = (
                "You are a scientific methodologist specializing in research method analysis. "
                "Provide detailed, technically accurate descriptions of research methods, "
                "including their applications, limitations, and emerging developments."
            )

        prompt = self.generate_research_methods_prompt(researcher_data, domain_context)
        
        response = self.api_client.get_response(prompt, system_prompt)
        logger.info(f"Generated research methods for {researcher_data['name']}")
        
        return response

    def generate_all_profiles(
        self,
        data_path: Path,
        output_dir: Path,
        domain_context: Optional[str] = None,
        include_methods: bool = True
    ) -> Dict[str, Dict[str, str]]:
        """Generate profiles for all researchers in a directory.
        
        Args:
            data_path: Path to researcher data directory
            output_dir: Output directory for reports
            domain_context: Optional domain context
            include_methods: Whether to generate methods documentation
            
        Returns:
            Dictionary mapping researcher names to their profiles
        """
        from symposium.analysis.presenters import PresenterAnalyzer
        from symposium.io.writers import ReportWriter

        # Use presenter analyzer for research profiles
        analyzer = PresenterAnalyzer(self.api_client, self.config)
        presenters = self.data_loader.load_presenter_data(
            data_path,
            max_rows=self.config.get('max_rows_per_file', 10)
        )

        results = {}

        for researcher_name, researcher_data in presenters.items():
            try:
                logger.info(f"Generating profile for: {researcher_name}")
                results[researcher_name] = {}

                # Generate research profile
                profile = analyzer.analyze_presenter(researcher_data, domain_context)
                results[researcher_name]['profile'] = profile

                ReportWriter.save_presenter_report(
                    researcher_name,
                    profile,
                    output_dir,
                    "research_profile"
                )

                # Generate methods documentation if requested
                if include_methods:
                    methods = self.generate_research_methods(researcher_data, domain_context)
                    results[researcher_name]['methods'] = methods

                    ReportWriter.save_presenter_report(
                        researcher_name,
                        methods,
                        output_dir,
                        "research_methods"
                    )

            except Exception as e:
                logger.error(f"Error generating profile for {researcher_name}: {e}")
                continue

        logger.info(f"Completed profile generation for {len(results)} researchers")
        return results

