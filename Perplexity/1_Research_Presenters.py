import os
import pandas as pd
from pathlib import Path
import traceback
import time
from Perplexity_Methods import (
    setup_logging,
    get_perplexity_client,
    get_perplexity_response,
    save_markdown_report,
    save_json_report
)

def get_presenter_data(base_path='../publications/AIF/'):
    """Get all presenter data from their respective folders"""
    presenters = {}
    
    for presenter_folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, presenter_folder)
        if os.path.isdir(folder_path):
            # Look for the two key files
            group_by_file = os.path.join(folder_path, 'openalex-group-by-20241103.csv')
            works_file = os.path.join(folder_path, [f for f in os.listdir(folder_path) 
                                                   if f.startswith('works-') and f.endswith('.csv')][0])
            
            if os.path.exists(group_by_file) and os.path.exists(works_file):
                presenters[presenter_folder] = {
                    'name': presenter_folder,
                    'topics': pd.read_csv(group_by_file),
                    'works': pd.read_csv(works_file)
                }
    
    return presenters

def generate_research_prompt(presenter_data):
    """Generate research prompt for a presenter"""
    topics_str = presenter_data['topics'].to_string() if not presenter_data['topics'].empty else "No topic data available"
    recent_works = presenter_data['works'][['title', 'publication_year', 'cited_by_count']].head()
    works_str = recent_works.to_string() if not recent_works.empty else "No works data available"
    
    return f"""Please analyze the research profile of {presenter_data['name']} based on:

Topics and their frequencies:
{topics_str}

Recent publications:
{works_str}

Please provide:
1. Research Focus: Main research areas and expertise
2. Impact Analysis: Citation patterns and research influence
3. Research Evolution: How their research interests have developed
4. Key Contributions: Notable findings and theoretical contributions
5. Future Directions: Potential research trajectories and collaborations
"""

def save_presenter_report(presenter_name, content, report_type='markdown'):
    """Save presenter research report"""
    safe_name = "".join(x for x in presenter_name if x.isalnum() or x in [' ', '-', '_']).strip()
    safe_name = safe_name.replace(' ', '_')
    
    # Create presenter-specific directory within outputs/presenters
    base_path = Path('outputs/presenters')
    presenter_dir = base_path / safe_name
    presenter_dir.mkdir(parents=True, exist_ok=True)
    
    if report_type == 'markdown':
        save_markdown_report(
            content,
            presenter_dir / f"{safe_name}_research_profile.md",
            f"Research Profile: {presenter_name}"
        )
    else:  # json
        save_json_report(
            content,
            presenter_dir / f"{safe_name}_research_profile.json",
            {"presenter": presenter_name}
        )

def main():
    """Main function to orchestrate presenter research."""
    logger = setup_logging("presenter_research")
    total_start_time = time.time()
    
    try:
        logger.info("🚀 Starting presenter research analysis...")
        
        # Initialize Perplexity client
        client = get_perplexity_client()
        
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
                analysis = get_perplexity_response(client, prompt)
                
                # Save results
                save_presenter_report(presenter_name, analysis, 'markdown')
                save_presenter_report(presenter_name, analysis, 'json')
                
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
    main()
