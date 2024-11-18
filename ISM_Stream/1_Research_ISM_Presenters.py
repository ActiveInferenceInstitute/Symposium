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

def get_presenter_data(base_path='../inputs/IntelligentSoftMatter/speakers/'):
    """Get all presenter data from their respective folders by reading all CSV files"""
    presenters = {}
    logger = setup_logging("presenter_data")
    
    try:
        if not os.path.exists(base_path):
            logger.error(f"❌ Base path does not exist: {base_path}")
            return presenters
            
        for presenter_folder in os.listdir(base_path):
            folder_path = os.path.join(base_path, presenter_folder)
            if not os.path.isdir(folder_path):
                continue
                
            try:
                # Get all CSV files in the folder
                csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
                all_data = []
                
                # Read each CSV file
                for csv_file in csv_files:
                    try:
                        file_path = os.path.join(folder_path, csv_file)
                        df = pd.read_csv(file_path)
                        all_data.append({
                            'filename': csv_file,
                            'data': df
                        })
                        logger.info(f"✅ Loaded {csv_file} for {presenter_folder}")
                    except Exception as e:
                        logger.warning(f"⚠️ Error reading {csv_file} for {presenter_folder}: {e}")
                
                if all_data:
                    presenters[presenter_folder] = {
                        'name': presenter_folder,
                        'data': all_data
                    }
                    logger.info(f"✅ Successfully loaded {len(all_data)} files for {presenter_folder}")
                else:
                    logger.warning(f"⚠️ No CSV files found for {presenter_folder}")
                    
            except Exception as e:
                logger.error(f"❌ Error processing presenter folder {presenter_folder}: {e}")
                continue
                
        logger.info(f"📊 Successfully loaded data for {len(presenters)} presenters")
        return presenters
        
    except Exception as e:
        logger.error(f"❌ Fatal error in get_presenter_data: {e}")
        traceback.print_exc()
        return presenters

def truncate_dataframe(df, max_rows=10):
    """Truncate dataframe to a maximum number of rows"""
    if len(df) > max_rows:
        return df.head(max_rows).copy()
    return df

def generate_research_prompt(presenter_data):
    """Generate research prompt using all available CSV data, with token limit handling"""
    data_sections = []
    max_rows_per_file = 10  # Adjust this number based on token limits
    
    # Add each CSV file's data to the prompt, with truncation
    for file_data in presenter_data['data']:
        df = file_data['data']
        truncated_df = truncate_dataframe(df, max_rows_per_file)
        
        # For works files, prioritize recent and highly cited papers
        if 'works-' in file_data['filename']:
            if 'cited_by_count' in df.columns and 'publication_year' in df.columns:
                df = df.sort_values(['publication_year', 'cited_by_count'], 
                                  ascending=[False, False]).head(max_rows_per_file)
        
        data_sections.append(
            f"\nData from {file_data['filename']} (showing top {max_rows_per_file} entries):"
            f"\n{truncated_df.to_string(max_rows=max_rows_per_file)}"
        )
    
    all_data = "\n\n".join(data_sections)
    
    prompt = f"""Please analyze the research profile of {presenter_data['name']} based on the following data samples. Generate a comprehensive, well-cited report focusing on:

1. **RESEARCH FOCUS**
   - Main research areas and expertise
   - Key methodologies and approaches
   - Notable contributions to the field

2. **IMPACT AND INFLUENCE**
   - Citation patterns and research impact
   - Key collaborations and networks
   - Real-world applications

3. **INTELLIGENT SOFT MATTER RELEVANCE**
   - Contributions to soft matter research
   - Integration of computational methods
   - Novel approaches and innovations

4. **FUTURE POTENTIAL**
   - Emerging research directions
   - Collaboration opportunities
   - Potential developments

Available Data (truncated for length):
{all_data}

Guidelines:
- Focus on key insights from the available data
- Highlight most significant contributions
- Consider Intelligent Soft Matter applications
- Identify collaboration opportunities"""

    return prompt

def save_presenter_report(presenter_name, content, report_type='markdown'):
    """Save presenter research report using folder name as identifier"""
    safe_name = presenter_name.replace(' ', '_')
    
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
                
                # Add safety check for token length
                if len(prompt.split()) > 12000:  # Approximate token limit
                    logger.warning(f"⚠️ Truncating prompt for {presenter_name} due to length")
                    prompt = "\n".join(prompt.split("\n")[:300])  # Take first 300 lines
                
                analysis = get_perplexity_response(client, prompt)
                
                # Save results
                save_presenter_report(presenter_name, analysis, 'markdown')
                save_presenter_report(presenter_name, analysis, 'json')
                
                presenter_time = time.time() - presenter_start_time
                logger.info(f"✅ Completed analysis for {presenter_name} in {presenter_time:.2f} seconds")
                
                # Add a small delay between requests
                time.sleep(2)
                
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
