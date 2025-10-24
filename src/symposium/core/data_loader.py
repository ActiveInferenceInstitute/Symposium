"""Data loading utilities for CSV, JSON, and other formats."""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd

logger = logging.getLogger(__name__)


class DataLoader:
    """Utility class for loading various data formats."""

    @staticmethod
    def load_csv(filepath: Path, **kwargs) -> pd.DataFrame:
        """Load CSV file with error handling.
        
        Args:
            filepath: Path to CSV file
            **kwargs: Additional parameters for pd.read_csv
            
        Returns:
            DataFrame with CSV data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: For other loading errors
        """
        try:
            if not filepath.exists():
                raise FileNotFoundError(f"CSV file not found: {filepath}")
            
            df = pd.read_csv(filepath, **kwargs)
            logger.debug(f"Loaded CSV file: {filepath} ({len(df)} rows)")
            return df
        
        except Exception as e:
            logger.error(f"Error loading CSV file {filepath}: {e}")
            raise

    @staticmethod
    def load_json(filepath: Path) -> Dict[str, Any]:
        """Load JSON file with error handling.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Dictionary with JSON data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: For other loading errors
        """
        try:
            if not filepath.exists():
                raise FileNotFoundError(f"JSON file not found: {filepath}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.debug(f"Loaded JSON file: {filepath}")
            return data
        
        except Exception as e:
            logger.error(f"Error loading JSON file {filepath}: {e}")
            raise

    @staticmethod
    def load_markdown(filepath: Path) -> str:
        """Load markdown/text file with error handling.
        
        Args:
            filepath: Path to markdown file
            
        Returns:
            File contents as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: For other loading errors
        """
        try:
            if not filepath.exists():
                raise FileNotFoundError(f"Markdown file not found: {filepath}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.debug(f"Loaded markdown file: {filepath} ({len(content)} chars)")
            return content
        
        except Exception as e:
            logger.error(f"Error loading markdown file {filepath}: {e}")
            raise

    @staticmethod
    def load_presenter_data(
        base_path: Path,
        max_rows: Optional[int] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Load presenter data from directory structure.
        
        Expected structure:
        base_path/
          Presenter_Name/
            openalex-group-by-*.csv
            works-*.csv
        
        Args:
            base_path: Base directory containing presenter folders
            max_rows: Maximum rows to load from each CSV (for token management)
            
        Returns:
            Dictionary mapping presenter names to their data
        """
        presenters = {}
        
        if not base_path.exists():
            logger.error(f"Base path does not exist: {base_path}")
            return presenters
        
        for presenter_folder in base_path.iterdir():
            if not presenter_folder.is_dir():
                continue
            
            try:
                # Find CSV files
                group_by_files = list(presenter_folder.glob('openalex-group-by-*.csv'))
                works_files = list(presenter_folder.glob('works-*.csv'))
                
                if not group_by_files or not works_files:
                    logger.warning(f"Missing required files in folder: {presenter_folder.name}")
                    continue
                
                # Load data
                topics_df = DataLoader.load_csv(group_by_files[0])
                works_df = DataLoader.load_csv(works_files[0])
                
                # Truncate if needed
                if max_rows:
                    topics_df = topics_df.head(max_rows)
                    # For works, prioritize recent and highly cited
                    if 'cited_by_count' in works_df.columns and 'publication_year' in works_df.columns:
                        works_df = works_df.sort_values(
                            ['publication_year', 'cited_by_count'],
                            ascending=[False, False]
                        ).head(max_rows)
                    else:
                        works_df = works_df.head(max_rows)
                
                presenters[presenter_folder.name] = {
                    'name': presenter_folder.name,
                    'topics': topics_df,
                    'works': works_df,
                    'folder_path': presenter_folder
                }
                
                logger.info(f"Loaded data for {presenter_folder.name}")
            
            except Exception as e:
                logger.error(f"Error processing folder {presenter_folder.name}: {e}")
                continue
        
        if not presenters:
            logger.warning("No presenter data was loaded")
        else:
            logger.info(f"Loaded data for {len(presenters)} presenters")
        
        return presenters

    @staticmethod
    def load_participant_profiles(base_path: Path) -> Dict[str, Dict[str, Any]]:
        """Load participant profiles from directory structure.
        
        Expected structure:
        base_path/
          Participant_Name/
            *_research_profile.json
            *_research_profile.md
        
        Args:
            base_path: Base directory containing participant folders
            
        Returns:
            Dictionary mapping participant names to their profiles
        """
        participants = {}
        
        if not base_path.exists():
            logger.error(f"Base path does not exist: {base_path}")
            return participants
        
        for participant_dir in base_path.iterdir():
            if not participant_dir.is_dir():
                continue
            
            try:
                # Find profile JSON file
                json_files = list(participant_dir.glob('*_research_profile.json'))
                
                if not json_files:
                    logger.debug(f"No profile JSON found for {participant_dir.name}")
                    continue
                
                profile_data = DataLoader.load_json(json_files[0])
                
                participants[participant_dir.name] = {
                    'name': profile_data.get('metadata', {}).get('presenter', participant_dir.name),
                    'profile': profile_data.get('content', ''),
                    'metadata': profile_data.get('metadata', {}),
                    'folder_path': participant_dir
                }
                
                logger.debug(f"Loaded profile for {participant_dir.name}")
            
            except Exception as e:
                logger.error(f"Error loading profile for {participant_dir.name}: {e}")
                continue
        
        if not participants:
            logger.warning("No participant profiles were loaded")
        else:
            logger.info(f"Loaded profiles for {len(participants)} participants")
        
        return participants

    @staticmethod
    def truncate_dataframe(df: pd.DataFrame, max_rows: int) -> pd.DataFrame:
        """Truncate dataframe to maximum number of rows.
        
        Args:
            df: DataFrame to truncate
            max_rows: Maximum number of rows
            
        Returns:
            Truncated DataFrame
        """
        if len(df) > max_rows:
            return df.head(max_rows).copy()
        return df

    @staticmethod
    def estimate_token_count(text: str) -> int:
        """Rough estimation of token count (words / 0.75).
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        return int(len(text.split()) / 0.75)

    @staticmethod
    def truncate_to_tokens(text: str, max_tokens: int) -> str:
        """Truncate text to approximate maximum token count.

        Args:
            text: Text to truncate
            max_tokens: Maximum token count

        Returns:
            Truncated text
        """
        current_tokens = DataLoader.estimate_token_count(text)

        if current_tokens <= max_tokens:
            return text

        # Estimate words needed
        words_needed = int(max_tokens * 0.75)
        words = text.split()

        return ' '.join(words[:words_needed])

    @staticmethod
    def load_participant_data(csv_path: Path) -> Dict[str, Dict[str, Any]]:
        """Load participant data from Public_Participant_Information.csv format.

        Args:
            csv_path: Path to the participant CSV file

        Returns:
            Dictionary mapping participant names to their complete data
        """
        try:
            # Load the CSV with proper column mapping
            df = DataLoader.load_csv(csv_path)

            # Define the expected columns based on the CSV structure
            column_mapping = {
                'Can we share this information publicly?': 'share_publicly',
                'What is your name?': 'name',
                'What is your email?': 'email',
                'What are your affiliations?': 'affiliations',
                'What is your ORCID?': 'orcid',
                'What is your background & prior works? Feel free to provide as much information & links as you like.': 'background',
                'What would be useful for you in the Symposium (pragmatic value)?': 'pragmatic_value',
                'What would be interesting or informative for you to learn from the Symposium (epistemic value)?': 'epistemic_value',
                'How are you applying Active Inference? What domain, stage?': 'active_inference_application',
                'What are the biggest hurdles or challenges facing Active Inference research and application?': 'challenges',
                'What would help you learn and apply Active Inference? E.g. resource, tool, or community development.': 'learning_needs',
                'How did you hear about the Symposium?': 'heard_about',
                'How could Active Inference applications make impact in 2026? (Think big!)': 'future_impact',
                'Any other comments or questions?': 'comments'
            }

            # Rename columns for easier access
            df = df.rename(columns=column_mapping)

            participants = {}

            for idx, row in df.iterrows():
                try:
                    # Skip rows without names
                    if pd.isna(row.get('name', '')) or str(row.get('name', '')).strip() == '':
                        continue

                    participant_data = {
                        'name': str(row.get('name', f'Participant_{idx}')).strip(),
                        'email': str(row.get('email', '')).strip() if not pd.isna(row.get('email', '')) else '',
                        'affiliations': str(row.get('affiliations', '')).strip() if not pd.isna(row.get('affiliations', '')) else '',
                        'orcid': str(row.get('orcid', '')).strip() if not pd.isna(row.get('orcid', '')) else '',
                        'background': str(row.get('background', '')).strip() if not pd.isna(row.get('background', '')) else '',
                        'pragmatic_value': str(row.get('pragmatic_value', '')).strip() if not pd.isna(row.get('pragmatic_value', '')) else '',
                        'epistemic_value': str(row.get('epistemic_value', '')).strip() if not pd.isna(row.get('epistemic_value', '')) else '',
                        'active_inference_application': str(row.get('active_inference_application', '')).strip() if not pd.isna(row.get('active_inference_application', '')) else '',
                        'challenges': str(row.get('challenges', '')).strip() if not pd.isna(row.get('challenges', '')) else '',
                        'learning_needs': str(row.get('learning_needs', '')).strip() if not pd.isna(row.get('learning_needs', '')) else '',
                        'heard_about': str(row.get('heard_about', '')).strip() if not pd.isna(row.get('heard_about', '')) else '',
                        'future_impact': str(row.get('future_impact', '')).strip() if not pd.isna(row.get('future_impact', '')) else '',
                        'comments': str(row.get('comments', '')).strip() if not pd.isna(row.get('comments', '')) else '',
                        'share_publicly': str(row.get('share_publicly', 'No')).strip() if not pd.isna(row.get('share_publicly', '')) else 'No',
                        'row_index': idx
                    }

                    # Only include participants who agreed to share publicly (unless overridden)
                    if participant_data['share_publicly'].lower() in ['yes', 'y', 'true', '1']:
                        participants[participant_data['name']] = participant_data
                        logger.info(f"Loaded participant data for: {participant_data['name']}")
                    else:
                        logger.debug(f"Skipping participant {participant_data['name']} - did not agree to share publicly")

                except Exception as e:
                    logger.error(f"Error processing participant at row {idx}: {e}")
                    continue

            logger.info(f"Loaded data for {len(participants)} participants who agreed to share publicly")
            return participants

        except Exception as e:
            logger.error(f"Error loading participant data from {csv_path}: {e}")
            raise

    @staticmethod
    def get_column_summary(participant_data: Dict[str, Dict[str, Any]], column: str) -> Dict[str, Any]:
        """Get summary statistics for a specific column across all participants.

        Args:
            participant_data: Dictionary of participant data
            column: Column name to summarize

        Returns:
            Summary statistics dictionary
        """
        try:
            values = []
            for participant in participant_data.values():
                value = participant.get(column, '')
                if value and str(value).strip():
                    values.append(str(value).strip())

            # Basic statistics
            summary = {
                'column': column,
                'total_participants': len(participant_data),
                'responses_count': len(values),
                'response_rate': len(values) / len(participant_data) if participant_data else 0,
                'unique_responses': len(set(values)),
                'avg_response_length': sum(len(v) for v in values) / len(values) if values else 0,
                'values': values[:100]  # Limit to first 100 for analysis
            }

            logger.debug(f"Generated summary for column '{column}': {summary['responses_count']} responses")
            return summary

        except Exception as e:
            logger.error(f"Error generating summary for column '{column}': {e}")
            return {
                'column': column,
                'error': str(e),
                'total_participants': len(participant_data),
                'responses_count': 0,
                'response_rate': 0
            }

    @staticmethod
    def format_participant_for_api(participant_data: Dict[str, Any]) -> str:
        """Format participant data for API consumption.

        Args:
            participant_data: Individual participant data dictionary

        Returns:
            Formatted string for API context
        """
        try:
            sections = []

            # Basic information
            if participant_data.get('name'):
                sections.append(f"Name: {participant_data['name']}")

            if participant_data.get('affiliations'):
                sections.append(f"Affiliations: {participant_data['affiliations']}")

            if participant_data.get('orcid'):
                sections.append(f"ORCID: {participant_data['orcid']}")

            # Background and experience
            if participant_data.get('background'):
                sections.append(f"Background & Prior Works: {participant_data['background']}")

            # Active Inference specific
            if participant_data.get('active_inference_application'):
                sections.append(f"Active Inference Application: {participant_data['active_inference_application']}")

            if participant_data.get('learning_needs'):
                sections.append(f"Learning Needs: {participant_data['learning_needs']}")

            if participant_data.get('challenges'):
                sections.append(f"Challenges: {participant_data['challenges']}")

            # Symposium expectations
            if participant_data.get('pragmatic_value'):
                sections.append(f"Pragmatic Value: {participant_data['pragmatic_value']}")

            if participant_data.get('epistemic_value'):
                sections.append(f"Epistemic Value: {participant_data['epistemic_value']}")

            # Future vision
            if participant_data.get('future_impact'):
                sections.append(f"Future Impact Vision: {participant_data['future_impact']}")

            # Other details
            if participant_data.get('heard_about'):
                sections.append(f"How they heard about symposium: {participant_data['heard_about']}")

            if participant_data.get('comments'):
                sections.append(f"Additional Comments: {participant_data['comments']}")

            return '\n\n'.join(sections)

        except Exception as e:
            logger.error(f"Error formatting participant data for API: {e}")
            return f"Name: {participant_data.get('name', 'Unknown')}\n\nError formatting data: {e}"

