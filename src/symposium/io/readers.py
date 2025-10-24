"""File readers for various formats."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd

logger = logging.getLogger(__name__)


class ReportReader:
    """Reader for reports and data files."""

    @staticmethod
    def read_markdown(filepath: Path) -> str:
        """Read markdown file.
        
        Args:
            filepath: Path to markdown file
            
        Returns:
            File contents as string
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.debug(f"Read markdown file: {filepath}")
            return content
        except Exception as e:
            logger.error(f"Error reading markdown file {filepath}: {e}")
            raise

    @staticmethod
    def read_json(filepath: Path) -> Dict[str, Any]:
        """Read JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Parsed JSON data
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"Read JSON file: {filepath}")
            return data
        except Exception as e:
            logger.error(f"Error reading JSON file {filepath}: {e}")
            raise

    @staticmethod
    def read_csv(filepath: Path, **kwargs) -> pd.DataFrame:
        """Read CSV file.
        
        Args:
            filepath: Path to CSV file
            **kwargs: Additional parameters for pd.read_csv
            
        Returns:
            DataFrame with CSV data
        """
        try:
            df = pd.read_csv(filepath, **kwargs)
            logger.debug(f"Read CSV file: {filepath} ({len(df)} rows)")
            return df
        except Exception as e:
            logger.error(f"Error reading CSV file {filepath}: {e}")
            raise

    @staticmethod
    def read_catechism(filepath: Path) -> str:
        """Read catechism template file.
        
        Args:
            filepath: Path to catechism template
            
        Returns:
            Template contents as string
        """
        return ReportReader.read_markdown(filepath)

    @staticmethod
    def read_domain_knowledge(filepath: Path) -> str:
        """Read domain knowledge file.
        
        Args:
            filepath: Path to domain knowledge file
            
        Returns:
            Domain knowledge as string
        """
        return ReportReader.read_markdown(filepath)

    @staticmethod
    def read_system_prompt(filepath: Path) -> str:
        """Read system prompt file.
        
        Args:
            filepath: Path to system prompt file
            
        Returns:
            System prompt as string
        """
        return ReportReader.read_markdown(filepath)

    @staticmethod
    def list_files_in_directory(
        directory: Path,
        pattern: str = "*",
        recursive: bool = False
    ) -> List[Path]:
        """List files in directory matching pattern.
        
        Args:
            directory: Directory to search
            pattern: Glob pattern (e.g., "*.json")
            recursive: Whether to search recursively
            
        Returns:
            List of matching file paths
        """
        try:
            if recursive:
                files = list(directory.rglob(pattern))
            else:
                files = list(directory.glob(pattern))
            
            logger.debug(f"Found {len(files)} files matching '{pattern}' in {directory}")
            return files
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {e}")
            return []

