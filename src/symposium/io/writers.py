"""Report writers for markdown, JSON, and other formats."""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class ReportWriter:
    """Writer for reports in various formats."""

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Create safe filename from string.
        
        Args:
            name: Original name
            
        Returns:
            Sanitized filename
        """
        safe_name = "".join(x for x in name if x.isalnum() or x in [' ', '-', '_']).strip()
        safe_name = safe_name.replace(' ', '_')
        return safe_name

    @staticmethod
    def save_markdown_report(
        content: str,
        filepath: Path,
        title: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Save report in markdown format.
        
        Args:
            content: Report content
            filepath: Output file path
            title: Report title
            metadata: Optional metadata to include in header
        """
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, 'w', encoding='utf-8') as f:
                # Write title
                f.write(f"# {title}\n\n")
                
                # Write metadata
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                if metadata:
                    f.write("## Metadata\n\n")
                    for key, value in metadata.items():
                        f.write(f"- **{key}**: {value}\n")
                    f.write("\n")
                
                f.write("---\n\n")
                
                # Write content
                f.write(content)

            logger.info(f"Saved markdown report to {filepath}")
        
        except Exception as e:
            logger.error(f"Error saving markdown report to {filepath}: {e}")
            raise

    @staticmethod
    def save_json_report(
        content: str,
        filepath: Path,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Save report in JSON format.
        
        Args:
            content: Report content
            filepath: Output file path
            metadata: Optional metadata dictionary
        """
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "timestamp": datetime.now().isoformat(),
                "content": content
            }

            if metadata:
                data["metadata"] = metadata

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved JSON report to {filepath}")
        
        except Exception as e:
            logger.error(f"Error saving JSON report to {filepath}: {e}")
            raise

    @staticmethod
    def save_both_formats(
        content: str,
        base_path: Path,
        name: str,
        title: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Save report in both markdown and JSON formats.
        
        Args:
            content: Report content
            base_path: Base directory for output
            name: Base filename (without extension)
            title: Report title
            metadata: Optional metadata
        """
        safe_name = ReportWriter.sanitize_filename(name)
        
        # Save markdown
        md_path = base_path / f"{safe_name}.md"
        ReportWriter.save_markdown_report(content, md_path, title, metadata)
        
        # Save JSON
        json_path = base_path / f"{safe_name}.json"
        ReportWriter.save_json_report(content, json_path, metadata)

    @staticmethod
    def save_presenter_report(
        presenter_name: str,
        content: str,
        output_dir: Path,
        report_type: str = "research_profile"
    ):
        """Save presenter research report.
        
        Args:
            presenter_name: Name of presenter
            content: Report content
            output_dir: Output directory (will create subdirectory for presenter)
            report_type: Type of report (e.g., 'research_profile', 'methods')
        """
        safe_name = ReportWriter.sanitize_filename(presenter_name)
        presenter_dir = output_dir / safe_name
        presenter_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            "presenter": presenter_name,
            "report_type": report_type
        }

        ReportWriter.save_both_formats(
            content,
            presenter_dir,
            f"{safe_name}_{report_type}",
            f"{report_type.replace('_', ' ').title()}: {presenter_name}",
            metadata
        )

    @staticmethod
    def save_participant_report(
        participant_name: str,
        content: str,
        output_dir: Path,
        report_type: str = "profile"
    ):
        """Save participant report.
        
        Args:
            participant_name: Name of participant
            content: Report content
            output_dir: Output directory (will create subdirectory for participant)
            report_type: Type of report (e.g., 'profile', 'learning_plan', 'projects')
        """
        safe_name = ReportWriter.sanitize_filename(participant_name)
        participant_dir = output_dir / safe_name
        participant_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            "participant": participant_name,
            "report_type": report_type
        }

        ReportWriter.save_both_formats(
            content,
            participant_dir,
            f"{safe_name}_{report_type}",
            f"{report_type.replace('_', ' ').title()}: {participant_name}",
            metadata
        )

    @staticmethod
    def save_project_proposal(
        participant_name: str,
        content: str,
        output_dir: Path,
        catechism_type: str = "KarmaGAP"
    ):
        """Save project proposal.
        
        Args:
            participant_name: Name of participant
            content: Proposal content
            output_dir: Output directory
            catechism_type: Type of catechism used
        """
        safe_name = ReportWriter.sanitize_filename(participant_name)
        participant_dir = output_dir / safe_name
        participant_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            "participant": participant_name,
            "catechism": catechism_type,
            "report_type": "project_proposal"
        }

        ReportWriter.save_both_formats(
            content,
            participant_dir,
            f"{safe_name}_project_proposal_{catechism_type}",
            f"Project Proposal: {participant_name}",
            metadata
        )

