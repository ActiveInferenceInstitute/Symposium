import os
import pandas as pd
from pathlib import Path
import traceback
import time
from dotenv import load_dotenv
from typing import Literal, Dict, Any

# Import both sets of methods
from Perplexity_Methods import (
    setup_logging as setup_perplexity_logging,
    get_perplexity_client,
    get_perplexity_response,
    save_markdown_report as save_perplexity_markdown,
    save_json_report as save_perplexity_json
)
from OpenRouter_Methods import (
    setup_logging as setup_openrouter_logging,
    get_openrouter_client,
    get_openrouter_response,
    save_markdown_report as save_openrouter_markdown,
    save_json_report as save_openrouter_json
)

APIChoice = Literal["perplexity", "openrouter"]

class APIHandler:
    def __init__(self, api_choice: APIChoice):
        self.api_choice = api_choice
        load_dotenv()

        if api_choice == "perplexity":
            self.setup_logging = setup_perplexity_logging
            self.get_client = get_perplexity_client
            self.get_response = get_perplexity_response
            self.save_markdown = save_perplexity_markdown
            self.save_markdown_report = save_perplexity_markdown
            self.save_json_report = save_perplexity_json
            self.save_json = save_perplexity_json
        else:  # openrouter
            self.setup_logging = setup_openrouter_logging
            self.get_client = get_openrouter_client
            self.get_response = get_openrouter_response
            self.save_markdown = save_openrouter_markdown
            self.save_markdown_report = save_openrouter_markdown
            self.save_json_report = save_openrouter_json
            self.save_json = save_openrouter_json

def read_description(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            description = file.read().strip()
        return description
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def load_participant_data(api_handler, base_path='./synthetic/participants/'):
    """Load participant profiles from JSON files"""
    import json
    from pathlib import Path

    logger = api_handler.setup_logging("application_planner")
    participant_data = {}

    try:
        base_dir = Path(base_path)
        for participant_dir in base_dir.iterdir():
            if participant_dir.is_dir():
                # JSON file path
                json_path = participant_dir / f"{participant_dir.name}_research_profile.json"
                if json_path.exists():
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Extract name and profile from JSON structure
                    name = data.get("metadata", {}).get("presenter", participant_dir.name)
                    profile = data.get("content", "")

                    participant_data[participant_dir.name] = {
                        'name': name,
                        'profile': profile
                    }
                else:
                    logger.warning(f"Profile JSON not found for {participant_dir.name}: {json_path}")

        if participant_data:
            logger.info(f"📚 Loaded data for {len(participant_data)} participants")
        else:
            logger.error(f"No participant data found. Checked in: {base_dir}")
            logger.error(f"Available directories: {[d.name for d in base_dir.iterdir() if d.is_dir()]}")

        return participant_data
    except Exception as e:
        logger.error(f"❌ Error loading participant data: {str(e)}")
        logger.error(f"Current working directory: {Path.cwd()}")
        raise

def generate_project_prompt(participant_name, participant_info):
    """Generate prompt for creating project proposals using Catechism"""
    field = read_description('synthetic/IntelligentSoftMatter.md')
    collaborators = read_description('synthetic/merged_research_profiles.md')
    catechism = read_description('Catechism/KarmaGAPGrants.md')

    return f"""You are top researcher in soft matter research field with the expertise in writing successful projects with the focus on innovation and creativity. For '{participant_name}' with this research profile '{participant_info}' you need to create a new and highly original project in the field "{field}" finding solutions to future challenges in the field of intelligent soft matter. Select most suitable 5 collaborators for the project from the list '{collaborators}'. Explicitly name these collaborators and justify the choice. Do not reply immediately, but analyse and choose the most reasonable project and setup. The project have to address important challenges and be breakthrough in nature considering challenges not addressed before in the scientific literature. However the project should be very detailed and technically sound and with high feasibility. Use the technique of Research Domain Field Shift to design a project: Concepts from one domain apply to another to create a shifted domain with new original solution to a problem similar to lateral thinking strategy.

Output the projects according to {catechism} and reply to all questions in detail.

"""

def save_project_proposals(api_handler,participant_name, content):
    """Save project proposals in participant's directory"""
    safe_name = "".join(x for x in participant_name if x.isalnum() or x in [' ', '-', '_']).strip()
    safe_name = safe_name.replace(' ', '_')

    base_path = Path('synthetic/participants')
    participant_dir = base_path / safe_name
    participant_dir.mkdir(parents=True, exist_ok=True)

    # Save as markdown
    api_handler.save_markdown_report(
        content,
        participant_dir / f"{safe_name}_project_proposals_KarmaGAP.md",
        f"Project Proposals: {participant_name}"
    )

    # Save as JSON
    api_handler.save_json_report(
        content,
        participant_dir / f"{safe_name}_project_proposals.json",
        {
            "participant": participant_name,
            "type": "project_proposals",
            "generated": time.strftime("%Y-%m-%d")
        }
    )

def main(api_choice: APIChoice = "perplexity"):
    """Main function to generate project proposals."""
    api_handler = APIHandler(api_choice)
    logger = api_handler.setup_logging("project_planner")
    total_start_time = time.time()

    try:
        logger.info("🚀 Starting project proposal generation...")

        # Initialize Perplexity client
        client = api_handler.get_client()

        # Load participant data
        participant_data = load_participant_data(api_handler)

        if not participant_data:
            logger.error("❌ No participant data found")
            return

        logger.info(f"📋 Generating project proposals for {len(participant_data)} participants")

        for idx, (participant_dir_name, info) in enumerate(participant_data.items(), 1):
            proposal_start_time = time.time()

            # Extract participant's name and profile
            participant_name = info.get('name', participant_dir_name)  # Default to directory name if 'name' is missing
            profile = info.get('profile', "No profile available.")

            logger.info(f"\n📝 Generating proposals ({idx}/{len(participant_data)}): {participant_name}")

            try:
                # Generate project proposals
                prompt = generate_project_prompt(participant_name, profile)
                if api_choice == "perplexity":
                    proposals = get_perplexity_response(
                        client,
                        prompt,
                        "You are a top level research director specializing in "
                        "project development and research planning. Focus on creating "
                        "concrete, original, well-structured proposals that follow the "
                        "Catechism format."
                    )
                else:  # openrouter
                         system_prompt = ("You are a top level research director specializing in "
                                                        "project development and research planning. Focus on creating "
                                                        "concrete, original, well-structured proposals that follow the "
                                                        "Catechism format.")
                         full_prompt = f"{system_prompt}\n\n{prompt}"
                         proposals = get_openrouter_response(client, full_prompt)

                # Save proposals
                save_project_proposals(api_handler, participant_name, proposals)

                proposal_time = time.time() - proposal_start_time
                logger.info(f"✅ Completed proposals for {participant_name} in {proposal_time:.2f} seconds")

            except Exception as e:
                logger.error(f"❌ Error generating proposals for {participant_name}: {e}")
                logger.error(traceback.format_exc())
                continue

        total_time = time.time() - total_start_time
        logger.info(f"\n🎉 All project proposals complete! Total time: {total_time:.2f} seconds")
        logger.info(f"📁 Proposals saved in outputs/participants/")

    except Exception as e:
        logger.error(f"❌ Fatal error in main: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Project Generator')
    parser.add_argument('--api', type=str, choices=['perplexity', 'openrouter'],
                      default='perplexity', help='Choose API to use: openrooter or perplexity (default: perplexity)')

    args = parser.parse_args()
    main(api_choice=args.api)
