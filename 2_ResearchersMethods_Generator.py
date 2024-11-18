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
            self.save_json = save_perplexity_json
        else:  # openrouter
            self.setup_logging = setup_openrouter_logging
            self.get_client = get_openrouter_client
            self.get_response = get_openrouter_response
            self.save_markdown = save_openrouter_markdown
            self.save_json = save_openrouter_json

def get_presenter_data(base_path='./inputs/IntelligentSoftMatter/participants/') -> Dict:
    """Get all researchers data from their respective folders"""
    presenters = {}
    for presenter_folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, presenter_folder)
        if os.path.isdir(folder_path):
            try:
                # Look for the two key files
                group_by_files = [f for f in os.listdir(folder_path)
                    if f.startswith('openalex-group-by') and f.endswith('.csv')]
                works_files = [f for f in os.listdir(folder_path)
                    if f.startswith('works-') and f.endswith('.csv')]

                # Check if both files exist before proceeding
                if not group_by_files or not works_files:
                    print(f"Missing required files in folder: {presenter_folder}")
                    continue

                group_by_file = os.path.join(folder_path, group_by_files[0])
                works_file = os.path.join(folder_path, works_files[0])

                if os.path.exists(group_by_file) and os.path.exists(works_file):
                    presenters[presenter_folder] = {
                        'name': presenter_folder,
                        'topics': pd.read_csv(group_by_file),
                        'works': pd.read_csv(works_file)
                    }
            except Exception as e:
                print(f"Error processing folder {presenter_folder}: {str(e)}")
                continue

    if not presenters:
        print("No researcher data was loaded. Please check the file structure.")

    return presenters

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

def generate_research_prompt(presenter_data: Dict) -> str:
    """Generate research prompt for a presenter"""
    topics_str = presenter_data['topics'].to_string() if not presenter_data['topics'].empty else "No topic data available"
    recent_works = presenter_data['works'][['title', 'publication_year', 'cited_by_count']].head()
    works_str = recent_works.to_string() if not recent_works.empty else "No works data available"
    field = read_description('synthetic/IntelligentSoftMatter.md')

    return f"""You are the top scientist in the field of Soft Matter serving as a referee of journals Nature and Science. Your are professional and the tone is academic. Do not comment the process of evaluation, only results. Be specific. Please analyze the research methods connected to the work of {presenter_data['name']} based on:

Target research field:
{field}

Topics and their frequencies:
{topics_str}

Recent publications:
{works_str}

Please identify and list experimental techniques or theoretical methods used by this researcher. Output in this form:

1. 'Method': Experimental techniques or theoretical method title
2. 'Detailed description': Description of the method. Elaborate on how the method works, including the underlying principles or mechanisms. Mention the equipment, software, or analytical tools involved.
Specify the scales of observation (e.g., molecular, macroscopic) or systems it is applied to.
3. 'Results or outcomes': Expected outcomes of this method or technique: types of materials, scales. Describe the primary data, metrics, or insights expected from applying the method. Include examples of phenomena or parameters the method helps to investigate or measure from the target field.
4. 'Emerging Trends': Discuss if the method is evolving, with newer variations or complementary technologies that might enhance its performance. Mention if it aligns with current trends, such as sustainability or data-driven modeling.
5. 'Limitations': Explain limitations of this method. Discuss inherent constraints or trade-offs of the method, such as precision, sensitivity, scalability, or applicability to certain systems. Highlight external factors that might affect its reliability, like environmental conditions or the need for specialized training.
Consider how these limitations might impact the interpretation of results or the feasibility of the method in broader contexts.

"""

def save_presenter_report(api_handler: APIHandler, presenter_name: str, content: str, report_type: str = 'markdown'):
    """Save presenter research report using the appropriate API handler"""
    safe_name = "".join(x for x in presenter_name if x.isalnum() or x in [' ', '-', '_']).strip()
    safe_name = safe_name.replace(' ', '_')

    base_path = Path('synthetic/participants')
    presenter_dir = base_path / safe_name
    presenter_dir.mkdir(parents=True, exist_ok=True)

    if report_type == 'markdown':
        api_handler.save_markdown(
            content,
            presenter_dir / f"{safe_name}_research_methods.md",
            f"Research Methods: {presenter_name}"
        )
    else:  # json
        api_handler.save_json(
            content,
            presenter_dir / f"{safe_name}_research_methods.json",
            {"presenter": presenter_name}
        )

def main(api_choice: APIChoice = "perplexity"):
    """Main function to orchestrate presenter research"""
    api_handler = APIHandler(api_choice)
    logger = api_handler.setup_logging("presenter_research")
    total_start_time = time.time()

    try:
        logger.info(f"🚀 Starting presenter research analysis using {api_choice} API...")

        # Initialize client using the appropriate handler
        client = api_handler.get_client()

        # Get presenter data
        presenters = get_presenter_data()

        if not presenters:
            logger.error("❌ No presenter data found")
            return

        logger.info(f"📊 Found {len(presenters)} presenters to analyze")

        # Process each presenter
        for idx, (presenter_name, presenter_data) in enumerate(presenters.items(), 1):
            presenter_start_time = time.time()
            logger.info(f"\n🔍 Analyzing presenter ({idx}/{len(presenters)}): {presenter_name}")

            try:
                # Generate and get research analysis
                prompt = generate_research_prompt(presenter_data)
                analysis = api_handler.get_response(client, prompt)

                # Save results
                save_presenter_report(api_handler, presenter_name, analysis, 'markdown')
                save_presenter_report(api_handler, presenter_name, analysis, 'json')

                presenter_time = time.time() - presenter_start_time
                logger.info(f"✅ Completed analysis for {presenter_name} in {presenter_time:.2f} seconds")

            except Exception as e:
                logger.error(f"❌ Error processing presenter {presenter_name}: {e}")
                continue

        total_time = time.time() - total_start_time
        logger.info(f"\n🎉 Analysis complete! Total time: {total_time:.2f} seconds")
        logger.info(f"📁 Reports saved in outputs/presenters/")

    except Exception as e:
        logger.error(f"❌ Fatal error in main: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Research Profile Analysis')
    parser.add_argument('--api', type=str, choices=['perplexity', 'openrouter'],
                      default='perplexity', help='Choose API to use: openrooter or perplexity (default: perplexity)')

    args = parser.parse_args()
    main(api_choice=args.api)
