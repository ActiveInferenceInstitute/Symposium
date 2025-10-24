"""Project proposal generation module."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from symposium.core.api import BaseAPIProvider
from symposium.core.data_loader import DataLoader
from symposium.io.readers import ReportReader

logger = logging.getLogger(__name__)


class ProjectGenerator:
    """Generator for research project proposals."""

    def __init__(self, api_client: BaseAPIProvider, config: Optional[Dict[str, Any]] = None):
        """Initialize project generator.
        
        Args:
            api_client: API client for generating content
            config: Optional configuration dictionary
        """
        self.api_client = api_client
        self.config = config or {}
        self.data_loader = DataLoader()

    def load_catechism_template(self, catechism_type: str, catechisms_dir: Path) -> str:
        """Load catechism template.
        
        Args:
            catechism_type: Type of catechism (e.g., 'KarmaGAP', 'EUGrants')
            catechisms_dir: Directory containing catechism templates
            
        Returns:
            Catechism template text
        """
        # Map catechism types to filenames
        catechism_files = {
            'karmagap': 'KarmaGAPGrants.md',
            'eugrants': 'EUGrants.md',
            'synthetic': 'Synthetic_Catechism.md'
        }

        filename = catechism_files.get(catechism_type.lower())
        if not filename:
            raise ValueError(f"Unknown catechism type: {catechism_type}")

        filepath = catechisms_dir / filename
        return ReportReader.read_catechism(filepath)

    def load_collaborators_list(self, collaborators_file: Path) -> str:
        """Load list of potential collaborators.
        
        Args:
            collaborators_file: Path to collaborators file
            
        Returns:
            Collaborators text
        """
        return ReportReader.read_markdown(collaborators_file)

    def generate_project_prompt(
        self,
        participant_name: str,
        participant_profile: str,
        domain_context: str,
        catechism_template: str,
        collaborators: Optional[str] = None
    ) -> str:
        """Generate project proposal prompt.
        
        Args:
            participant_name: Name of participant
            participant_profile: Participant's research profile
            domain_context: Domain/field description
            catechism_template: Catechism template to follow
            collaborators: Optional list of potential collaborators
            
        Returns:
            Generated prompt string
        """
        prompt = f"""You are a top researcher and expert at writing successful, innovative research projects.

For participant '{participant_name}' with the following research profile:

{participant_profile}

Create a highly original, breakthrough research project in the field:

{domain_context}

The project must:
- Address important challenges not previously tackled in the literature
- Be technically sound with high feasibility
- Be detailed and well-structured
- Use Research Domain Field Shift technique (applying concepts from one domain to another)
"""

        if collaborators:
            prompt += f"""

Select the 5 most suitable collaborators from the following list and explicitly justify each choice:

{collaborators}
"""

        prompt += f"""

Structure your project proposal according to the following catechism format. Answer ALL questions in detail:

{catechism_template}

Before finalizing, analyze multiple potential project directions and select the most promising one."""

        return prompt

    def generate_project_proposal(
        self,
        participant_name: str,
        participant_profile: str,
        domain_context: str,
        catechism_type: str = "KarmaGAP",
        catechisms_dir: Optional[Path] = None,
        collaborators: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate a project proposal for a participant.
        
        Args:
            participant_name: Name of participant
            participant_profile: Participant's research profile
            domain_context: Domain/field description
            catechism_type: Type of catechism to use
            catechisms_dir: Directory containing catechism templates
            collaborators: Optional list of potential collaborators
            system_prompt: Optional system prompt override
            
        Returns:
            Generated project proposal
        """
        if system_prompt is None:
            system_prompt = (
                "You are a top-level research director specializing in project development "
                "and research planning. Focus on creating concrete, original, well-structured "
                "proposals that are both innovative and feasible."
            )

        # Load catechism template
        if catechisms_dir is None:
            catechisms_dir = Path.cwd() / "data" / "catechisms"
        
        catechism_template = self.load_catechism_template(catechism_type, catechisms_dir)

        # Generate prompt
        prompt = self.generate_project_prompt(
            participant_name,
            participant_profile,
            domain_context,
            catechism_template,
            collaborators
        )

        # Token limit check
        max_tokens = self.config.get('max_prompt_tokens', 12000)
        if self.data_loader.estimate_token_count(prompt) > max_tokens:
            logger.warning(f"Prompt exceeds token limit, truncating for {participant_name}")
            prompt = self.data_loader.truncate_to_tokens(prompt, max_tokens)

        response = self.api_client.get_response(prompt, system_prompt)
        logger.info(f"Generated project proposal for {participant_name}")
        
        return response

    def generate_all_projects(
        self,
        profiles_dir: Path,
        output_dir: Path,
        domain_context_file: Path,
        catechism_type: str = "KarmaGAP",
        catechisms_dir: Optional[Path] = None,
        collaborators_file: Optional[Path] = None
    ) -> Dict[str, str]:
        """Generate project proposals for all participants.
        
        Args:
            profiles_dir: Directory containing participant profiles
            output_dir: Output directory for proposals
            domain_context_file: File containing domain description
            catechism_type: Type of catechism to use
            catechisms_dir: Directory containing catechism templates
            collaborators_file: Optional file with collaborators list
            
        Returns:
            Dictionary mapping participant names to proposals
        """
        from symposium.io.writers import ReportWriter

        # Load domain context
        domain_context = ReportReader.read_markdown(domain_context_file)

        # Load collaborators if provided
        collaborators = None
        if collaborators_file and collaborators_file.exists():
            collaborators = self.load_collaborators_list(collaborators_file)

        # Load participant profiles
        participants = self.data_loader.load_participant_profiles(profiles_dir)
        results = {}

        for participant_name, participant_data in participants.items():
            try:
                logger.info(f"Generating project proposal for: {participant_name}")

                proposal = self.generate_project_proposal(
                    participant_name,
                    participant_data['profile'],
                    domain_context,
                    catechism_type,
                    catechisms_dir,
                    collaborators
                )

                results[participant_name] = proposal

                # Save proposal
                ReportWriter.save_project_proposal(
                    participant_name,
                    proposal,
                    output_dir,
                    catechism_type
                )

            except Exception as e:
                logger.error(f"Error generating proposal for {participant_name}: {e}")
                continue

        logger.info(f"Completed project generation for {len(results)} participants")
        return results

